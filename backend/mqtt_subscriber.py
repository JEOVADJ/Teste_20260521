import json
import time
import paho.mqtt.client as mqtt
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, MQTT_USERNAME, MQTT_PASSWORD
from db import get_conn
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def ensure_system_device(conn, system_name, device_identifier):
    """Ensure system and device exist in database"""
    cur = conn.cursor()
    
    try:
        # Get or create system
        cur.execute('SELECT id FROM systems WHERE name=%s', (system_name,))
        row = cur.fetchone()
        if row:
            system_id = row[0]
        else:
            cur.execute('INSERT INTO systems (name) VALUES (%s)', (system_name,))
            system_id = cur.lastrowid
        
        # Get or create device
        cur.execute(
            'SELECT id FROM devices WHERE system_id=%s AND device_identifier=%s',
            (system_id, device_identifier)
        )
        row = cur.fetchone()
        if row:
            device_id = row[0]
        else:
            cur.execute(
                'INSERT INTO devices (system_id, device_identifier, status) VALUES (%s, %s, %s)',
                (system_id, device_identifier, 'active')
            )
            device_id = cur.lastrowid
        
        return system_id, device_id
    except Exception as e:
        logger.error(f"Error ensuring system/device: {e}")
        return None, None
    finally:
        cur.close()

def on_connect(client, userdata, flags, rc):
    """Callback for when MQTT client connects"""
    if rc == 0:
        logger.info(f'MQTT connected with result code {rc}')
        client.subscribe(MQTT_TOPIC)
        logger.info(f'Subscribed to topic: {MQTT_TOPIC}')
    else:
        logger.error(f'MQTT connection failed with result code {rc}')

def on_disconnect(client, userdata, rc):
    """Callback for when MQTT client disconnects"""
    if rc != 0:
        logger.warning(f'Unexpected MQTT disconnection with result code {rc}')

def on_message(client, userdata, msg):
    """Callback for when MQTT message is received"""
    payload = msg.payload.decode('utf-8')
    logger.debug(f'Message received on topic {msg.topic}: {payload}')
    
    try:
        # Try to parse JSON
        data = json.loads(payload)
    except json.JSONDecodeError:
        try:
            # Try to parse CSV: value,device,system,ts
            parts = payload.split(',')
            data = {}
            if len(parts) >= 1:
                data['value'] = float(parts[0])
            if len(parts) >= 2:
                data['device_id'] = parts[1]
            if len(parts) >= 3:
                data['system'] = parts[2]
            if len(parts) >= 4:
                data['timestamp'] = parts[3]
        except Exception as e:
            logger.warning(f'Error parsing message: {e}')
            return

    # Extract data
    system_name = data.get('system', 'default')
    device_identifier = data.get('device_id', 'unknown')
    ts = data.get('timestamp')
    value = data.get('value')
    
    if value is None:
        logger.warning('No value found in message')
        return

    try:
        # Save to database
        conn = get_conn()
        system_id, device_id = ensure_system_device(conn, system_name, device_identifier)
        
        if device_id is None:
            logger.error('Failed to create device')
            conn.close()
            return
        
        cur = conn.cursor()
        
        # Insert reading
        if ts:
            try:
                # Try to parse timestamp
                from datetime import datetime
                ts_obj = datetime.fromisoformat(ts)
                cur.execute(
                    'INSERT INTO readings (device_id, ts, value) VALUES (%s, %s, %s)',
                    (device_id, ts_obj, value)
                )
            except Exception as e:
                logger.warning(f'Error parsing timestamp {ts}, using NOW(): {e}')
                cur.execute(
                    'INSERT INTO readings (device_id, ts, value) VALUES (%s, NOW(), %s)',
                    (device_id, value)
                )
        else:
            cur.execute(
                'INSERT INTO readings (device_id, ts, value) VALUES (%s, NOW(), %s)',
                (device_id, value)
            )
        
        # Update device last_reading
        cur.execute(
            'UPDATE devices SET last_reading = NOW() WHERE id = %s',
            (device_id,)
        )
        
        cur.close()
        conn.close()
        
        logger.info(f'Saved reading: {system_name} / {device_identifier} = {value}')
        
        # Emit via SocketIO if available
        sio = userdata.get('socketio') if isinstance(userdata, dict) else None
        if sio:
            try:
                sio.emit('new_reading', {
                    'system': system_name,
                    'device_id': device_identifier,
                    'value': float(value),
                    'timestamp': ts or datetime.now().isoformat()
                }, broadcast=True)
            except Exception as e:
                logger.warning(f'Error emitting SocketIO message: {e}')

    except Exception as e:
        logger.error(f'Error processing message: {e}')

def start(socketio=None):
    """Start MQTT subscriber"""
    userdata = {'socketio': socketio} if socketio is not None else None
    
    client = mqtt.Client(client_id='iot_monitor_subscriber')
    client.userdata = userdata
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    
    # Set username/password if provided
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    try:
        logger.info(f'Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}')
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        logger.info('MQTT client loop started')
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info('MQTT subscriber interrupted')
        client.disconnect()
    except Exception as e:
        logger.error(f'MQTT connection error: {e}')
        raise

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    start()

