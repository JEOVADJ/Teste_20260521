from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from db import init_pool, get_conn, ensure_tables
from datetime import datetime, timedelta
import config
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_pool()
ensure_tables()

# Create Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')

# ============ STATIC FILES ============
@app.route('/')
def index():
    return app.send_static_file('index.html')

# ============ API ENDPOINTS ============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/systems', methods=['GET'])
def api_systems():
    """Get all systems"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('SELECT id, name FROM systems ORDER BY name')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        items = [{'id': r[0], 'name': r[1]} for r in rows]
        return jsonify(items)
    except Exception as e:
        logger.error(f"Error fetching systems: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices', methods=['GET'])
def api_devices():
    """Get devices, optionally filtered by system"""
    try:
        system_id = request.args.get('system_id')
        conn = get_conn()
        cur = conn.cursor()
        
        if system_id:
            cur.execute('SELECT id, system_id, device_identifier FROM devices WHERE system_id=%s ORDER BY device_identifier', (system_id,))
        else:
            cur.execute('SELECT id, system_id, device_identifier FROM devices ORDER BY device_identifier')
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        items = [{'id': r[0], 'system_id': r[1], 'identifier': r[2]} for r in rows]
        return jsonify(items)
    except Exception as e:
        logger.error(f"Error fetching devices: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/readings', methods=['GET'])
def api_readings():
    """Get readings with filtering options"""
    try:
        device_id = request.args.get('device_id')
        start = request.args.get('start')
        end = request.args.get('end')
        limit = int(request.args.get('limit', 1000))
        
        if not device_id:
            return jsonify({'error': 'device_id is required'}), 400
        
        conn = get_conn()
        cur = conn.cursor()
        
        query = 'SELECT ts, value FROM readings WHERE device_id=%s'
        params = [device_id]
        
        if start:
            query += ' AND ts >= %s'
            params.append(start)
        
        if end:
            query += ' AND ts <= %s'
            params.append(end)
        
        query += ' ORDER BY ts DESC LIMIT %s'
        params.append(limit)
        
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        items = [{'ts': r[0].isoformat() if r[0] else None, 'value': float(r[1])} for r in rows]
        return jsonify(items)
    except Exception as e:
        logger.error(f"Error fetching readings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/readings/stats', methods=['GET'])
def api_readings_stats():
    """Get statistics for a device"""
    try:
        device_id = request.args.get('device_id')
        hours = int(request.args.get('hours', 24))
        
        if not device_id:
            return jsonify({'error': 'device_id is required'}), 400
        
        conn = get_conn()
        cur = conn.cursor()
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        cur.execute('''
            SELECT 
                COUNT(*) as count,
                MIN(value) as min_value,
                MAX(value) as max_value,
                AVG(value) as avg_value,
                STDDEV(value) as stddev_value
            FROM readings
            WHERE device_id=%s AND ts >= %s
        ''', (device_id, start_time))
        
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify({
                'count': row[0] or 0,
                'min': float(row[1]) if row[1] else None,
                'max': float(row[2]) if row[2] else None,
                'avg': float(row[3]) if row[3] else None,
                'stddev': float(row[4]) if row[4] else None
            })
        else:
            return jsonify({'error': 'No data found'}), 404
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<int:device_id>/latest', methods=['GET'])
def api_device_latest(device_id):
    """Get latest reading for a device"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('SELECT ts, value FROM readings WHERE device_id=%s ORDER BY ts DESC LIMIT 1', (device_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify({'ts': row[0].isoformat(), 'value': float(row[1])})
        else:
            return jsonify({'error': 'No readings found'}), 404
    except Exception as e:
        logger.error(f"Error fetching latest reading: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/readings', methods=['POST'])
def api_add_reading():
    """Add a new reading (manual insertion)"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        value = data.get('value')
        ts = data.get('ts')
        
        if not device_id or value is None:
            return jsonify({'error': 'device_id and value are required'}), 400
        
        conn = get_conn()
        cur = conn.cursor()
        
        if ts:
            cur.execute('INSERT INTO readings (device_id, ts, value) VALUES (%s, %s, %s)', (device_id, ts, value))
        else:
            cur.execute('INSERT INTO readings (device_id, ts, value) VALUES (%s, NOW(), %s)', (device_id, value))
        
        cur.close()
        conn.close()
        
        # Emit to all connected clients
        socketio.emit('new_reading', {
            'device_id': device_id,
            'value': value,
            'timestamp': ts or datetime.now().isoformat()
        }, broadcast=True)
        
        return jsonify({'status': 'ok', 'id': cur.lastrowid}), 201
    except Exception as e:
        logger.error(f"Error adding reading: {e}")
        return jsonify({'error': str(e)}), 500

# ============ WEBSOCKET EVENTS ============

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('connect_response', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('refresh_data')
def handle_refresh_data(data):
    """Client requests data refresh"""
    logger.info(f'Refresh requested: {data}')
    emit('data_refreshed', {'timestamp': datetime.now().isoformat()}, broadcast=True)

# ============ MQTT SUBSCRIBER ============

def run_mqtt_subscriber():
    """Run MQTT subscriber in a separate thread"""
    try:
        import mqtt_subscriber
        mqtt_subscriber.start(socketio)
    except Exception as e:
        logger.error(f"MQTT subscriber error: {e}")

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ============ MAIN ============

if __name__ == '__main__':
    # Start MQTT subscriber in background thread
    mqtt_thread = threading.Thread(target=run_mqtt_subscriber, daemon=True)
    mqtt_thread.start()
    
    logger.info('Starting Flask-SocketIO server on 0.0.0.0:5000')
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

