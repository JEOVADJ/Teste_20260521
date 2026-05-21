from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from db import init_pool, get_conn, ensure_tables
import config
import threading
import time

init_pool()
ensure_tables()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/systems')
def api_systems():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM systems')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    items = [{'id': r[0], 'name': r[1]} for r in rows]
    return jsonify(items)

@app.route('/api/devices')
def api_devices():
    system_id = request.args.get('system_id')
    conn = get_conn()
    cur = conn.cursor()
    if system_id:
        cur.execute('SELECT id, device_identifier FROM devices WHERE system_id=%s', (system_id,))
    else:
        cur.execute('SELECT id, device_identifier FROM devices')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    items = [{'id': r[0], 'identifier': r[1]} for r in rows]
    return jsonify(items)

@app.route('/api/readings')
def api_readings():
    device_id = request.args.get('device_id')
    start = request.args.get('start')
    end = request.args.get('end')
    limit = int(request.args.get('limit', 1000))
    if not device_id:
        return jsonify({'error': 'device_id required'}), 400
    conn = get_conn()
    cur = conn.cursor()
    q = 'SELECT ts, value FROM readings WHERE device_id=%s'
    params = [device_id]
    if start:
        q += ' AND ts >= %s'
        params.append(start)
    if end:
        q += ' AND ts <= %s'
        params.append(end)
    q += ' ORDER BY ts DESC LIMIT %s'
    params.append(limit)
    cur.execute(q, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    items = [{'ts': r[0].isoformat(), 'value': r[1]} for r in rows]
    return jsonify(items)

def run_mqtt_subscriber():
    # run mqtt_subscriber in separate thread/process
    import mqtt_subscriber
    mqtt_subscriber.start(socketio)

if __name__ == '__main__':
    # start mqtt subscriber in background thread
    t = threading.Thread(target=run_mqtt_subscriber, daemon=True)
    t.start()
    socketio.run(app, host='0.0.0.0', port=5000)
