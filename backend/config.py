import os
from dotenv import load_dotenv

load_dotenv()

# ============ DATABASE CONFIGURATION ============
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DB = os.getenv('MYSQL_DB', 'iot_monitor')

# ============ MQTT CONFIGURATION ============
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'devices/#')
MQTT_USERNAME = os.getenv('MQTT_USERNAME', None)
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', None)

# ============ FLASK CONFIGURATION ============
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_ENV = os.getenv('FLASK_ENV', 'production')
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# ============ LOGGING CONFIGURATION ============
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ============ DATABASE POOL CONFIGURATION ============
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 5))
DB_POOL_NAME = os.getenv('DB_POOL_NAME', 'iot_pool')

# ============ API CONFIGURATION ============
API_LIMIT_READINGS = int(os.getenv('API_LIMIT_READINGS', 10000))
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))

