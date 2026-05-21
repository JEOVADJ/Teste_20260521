import json
import time
import paho.mqtt.client as mqtt
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC
from db import get_conn

def ensure_system_device(conn, system_name, device_identifier):
    cur = conn.cursor()
    cur.execute('SELECT id FROM systems WHERE name=%s', (system_name,))
    row = cur.fetchone()
    if row:
        system_id = row[0]
    else:
        cur.execute('INSERT INTO systems (name) VALUES (%s)', (system_name,))
        system_id = cur.lastrowid
    cur.execute('SELECT id FROM devices WHERE system_id=%s AND device_identifier=%s', (system_id, device_identifier))
    row = cur.fetchone()
    if row:
        device_id = row[0]
    else:
        cur.execute('INSERT INTO devices (system_id, device_identifier) VALUES (%s, %s)', (system_id, device_identifier))
        device_id = cur.lastrowid
    cur.close()
    return system_id, device_id

def on_connect(client, userdata, flags, rc):
    print('MQTT connected with result code', rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    try:
        data = json.loads(payload)
    except Exception:
        # try simple CSV: value,device,system,ts
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

    system_name = data.get('system') or 'default'
    device_identifier = data.get('device_id') or 'unknown'
    ts = data.get('timestamp')
    value = data.get('value')
    if value is None:
        return

    conn = get_conn()
    cur = conn.cursor()
    system_id, device_id = ensure_system_device(conn, system_name, device_identifier)
    if ts:
        cur.execute('INSERT INTO readings (device_id, ts, value) VALUES (%s, %s, %s)', (device_id, ts, value))
    else:
        cur.execute('INSERT INTO readings (device_id, ts, value) VALUES (%s, NOW(), %s)', (device_id, value))
    cur.close()
    conn.close()
    print('Saved reading:', system_name, device_identifier, value)

    # emit via socketio if present in userdata
    sio = userdata.get('socketio') if isinstance(userdata, dict) else None
    if sio:
        try:
            sio.emit('new_reading', {
                'system': system_name,
                'device_id': device_identifier,
                'value': value,
                'timestamp': ts
            })
        except Exception:
            pass

def start(socketio=None):
    userdata = {'socketio': socketio} if socketio is not None else None
    client = mqtt.Client(userdata=userdata)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()

if __name__ == '__main__':
    start()
