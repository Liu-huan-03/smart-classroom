# src/database.py
import sqlite3
import json
from datetime import datetime
import os

class Database:
    def __init__(self, db_path="data/sensor_data.db"):
        # 确保data目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建传感器数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_id VARCHAR(50),
                sensor_type VARCHAR(20),
                value REAL,
                unit VARCHAR(10)
            )
        ''')
        
        # 创建控制历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS control_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_id VARCHAR(50),
                command VARCHAR(20),
                reason TEXT
            )
        ''')
        
        # 创建能耗记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy_consumption (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                device_id VARCHAR(50),
                power_consumed REAL,
                duration INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"数据库初始化完成: {self.db_path}")
    
    def save_sensor_data(self, device_id, sensor_type, value, unit=None):
        """保存传感器数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_data (timestamp, device_id, sensor_type, value, unit)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now(), device_id, sensor_type, value, unit))
        
        conn.commit()
        conn.close()
    
    def save_control_command(self, device_id, command, reason=None):
        """保存控制命令"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO control_history (timestamp, device_id, command, reason)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now(), device_id, command, reason))
        
        conn.commit()
        conn.close()
    
    def query_recent_data(self, sensor_type=None, limit=100):
        """查询最近的数据"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if sensor_type:
            cursor.execute('''
                SELECT * FROM sensor_data 
                WHERE sensor_type = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (sensor_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM sensor_data 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_daily_summary(self, date=None):
        """获取每日摘要"""
        if date is None:
            date = datetime.now().date()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                sensor_type,
                COUNT(*) as count,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value
            FROM sensor_data 
            WHERE DATE(timestamp) = ?
            GROUP BY sensor_type
        ''', (date,))
        
        result = cursor.fetchall()
        conn.close()
        
        return result