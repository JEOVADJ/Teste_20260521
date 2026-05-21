import mysql.connector
from mysql.connector import pooling
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT

pool = None

def init_pool(pool_name='iot_pool', pool_size=5):
    global pool
    if pool is None:
        pool = pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            autocommit=True,
        )

def get_conn():
    if pool is None:
        init_pool()
    return pool.get_connection()

def ensure_tables():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS systems (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL
    ) ENGINE=InnoDB;
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INT AUTO_INCREMENT PRIMARY KEY,
        system_id INT,
        device_identifier VARCHAR(255),
        UNIQUE(system_id, device_identifier),
        FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS readings (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        device_id INT,
        ts DATETIME,
        value DOUBLE,
        FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
        INDEX (ts)
    ) ENGINE=InnoDB;
    ''')
    cur.close()
    conn.close()
