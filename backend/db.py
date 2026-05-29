import mysql.connector
from mysql.connector import pooling
from config import (
    MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT,
    DB_POOL_SIZE, DB_POOL_NAME
)
import logging

logger = logging.getLogger(__name__)

pool = None

def init_pool(pool_name=DB_POOL_NAME, pool_size=DB_POOL_SIZE):
    """Initialize MySQL connection pool"""
    global pool
    if pool is None:
        try:
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
            logger.info(f"Database pool initialized: {pool_name} (size: {pool_size})")
        except Exception as e:
            logger.error(f"Error initializing connection pool: {e}")
            raise

def get_conn():
    """Get a connection from the pool"""
    if pool is None:
        init_pool()
    return pool.get_connection()

def ensure_tables():
    """Create tables if they don't exist"""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Systems table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS systems (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX (name)
        ) ENGINE=InnoDB;
        ''')
        
        # Devices table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            system_id INT NOT NULL,
            device_identifier VARCHAR(255) NOT NULL,
            description TEXT,
            unit VARCHAR(50),
            status ENUM('active', 'inactive', 'error') DEFAULT 'active',
            last_reading DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_device (system_id, device_identifier),
            FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE,
            INDEX (system_id),
            INDEX (device_identifier),
            INDEX (status)
        ) ENGINE=InnoDB;
        ''')
        
        # Readings table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            device_id INT NOT NULL,
            ts DATETIME NOT NULL,
            value DOUBLE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
            INDEX (device_id),
            INDEX (ts),
            INDEX (device_id, ts)
        ) ENGINE=InnoDB;
        ''')
        
        # Alerts table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_id INT NOT NULL,
            alert_type VARCHAR(50),
            message TEXT,
            severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
            resolved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at DATETIME,
            FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
            INDEX (device_id),
            INDEX (resolved)
        ) ENGINE=InnoDB;
        ''')
        
        cur.close()
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        cur.close()
        raise
    finally:
        conn.close()

def get_system_stats():
    """Get overall system statistics"""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        cur.execute('SELECT COUNT(*) FROM systems')
        systems_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM devices')
        devices_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM readings')
        readings_count = cur.fetchone()[0]
        
        return {
            'systems': systems_count,
            'devices': devices_count,
            'readings': readings_count
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def cleanup_old_readings(days=30):
    """Delete readings older than specified days"""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        cur.execute('DELETE FROM readings WHERE ts < %s', (cutoff_date,))
        deleted = cur.rowcount
        logger.info(f"Deleted {deleted} old readings (older than {days} days)")
        return deleted
    except Exception as e:
        logger.error(f"Error cleaning up old readings: {e}")
        return 0
    finally:
        cur.close()
        conn.close()

