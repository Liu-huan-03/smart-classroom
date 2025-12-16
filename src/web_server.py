# src/web_server.py - 主程序，包含所有功能
from flask import Flask, render_template, jsonify, request
import sqlite3
import json
import time
import random
import threading
from datetime import datetime
import os

app = Flask(__name__)

# ============ 1. 多设备管理 ============
# 设备配置（粘贴第5步的第一个代码块）
devices = {
    "sensors": [
        {"id": "temp1", "type": "temperature", "location": "front"},
        {"id": "humi1", "type": "humidity", "location": "front"},
        {"id": "light_sensor1", "type": "light", "location": "window"},
        {"id": "co2_sensor1", "type": "co2", "location": "middle"},
        {"id": "pir1", "type": "pir", "location": "door"}
    ],
    "actuators": [
        {"id": "light1", "type": "light", "location": "front", "status": "off"},
        {"id": "fan1", "type": "fan", "location": "back", "status": "off"},
        {"id": "curtain1", "type": "curtain", "location": "window", "status": "closed"},
        {"id": "ac1", "type": "ac", "location": "side", "status": "off"}
    ]
}

# 当前传感器数据
current_sensor_data = {
    "temperature": 25.0,
    "humidity": 50.0,
    "light": 500,
    "co2": 800,
    "pir": 0
}

# ============ 2. 智能控制逻辑 ============
# 智能控制函数（粘贴第5步的第二个代码块）
def auto_control_logic(sensor_data):
    """基于规则的自动控制"""
    commands = []
    
    # 光照控制
    if sensor_data['light'] < 300 and sensor_data['pir'] == 1:
        commands.append({"device": "light1", "command": "on"})
    
    # 空气质量控制
    if sensor_data['co2'] > 1000:
        commands.append({"device": "fan1", "command": "on"})
    
    # 温度控制
    if sensor_data['temperature'] > 26:
        commands.append({"device": "ac1", "command": "on", "temp": 25})
    
    return commands

# ============ 3. 数据持久化 ============
# 数据库函数（粘贴第5步的第三个代码块，但要修改参数名）
def init_database():
    """初始化数据库"""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/sensor_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         timestamp DATETIME,
         temperature REAL,
         humidity REAL,
         light INTEGER,
         co2 INTEGER,
         occupancy INTEGER)
    ''')
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

def save_sensor_data(data):
    """保存传感器数据"""
    conn = sqlite3.connect('data/sensor_data.db')
    cursor = conn.cursor()
    # 注意：这里修改了参数名，从 data['temp'] 改为 data['temperature']
    cursor.execute('''
        INSERT INTO sensor_data 
        (timestamp, temperature, humidity, light, co2, occupancy) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now(), data['temperature'], data['humidity'], 
          data['light'], data['co2'], data['pir']))
    conn.commit()
    conn.close()

# ============ 4. Web API路由 ============
@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/sensor_data')
def get_sensor_data():
    """获取传感器数据API"""
    return jsonify({
        "success": True,
        "data": current_sensor_data,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

@app.route('/api/devices')
def get_devices():
    """获取设备列表API"""
    return jsonify({
        "success": True,
        "devices": devices
    })

@app.route('/api/control', methods=['POST'])
def control_device():
    """控制设备API"""
    try:
        data = request.json
        device_id = data.get('device_id')
        command = data.get('command')
        
        # 更新设备状态
        for actuator in devices["actuators"]:
            if actuator["id"] == device_id:
                actuator["status"] = command
                break
        
        return jsonify({
            "success": True,
            "message": f"设备 {device_id} 已执行 {command}",
            "device_id": device_id,
            "command": command
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/scene', methods=['POST'])
def set_scene():
    """设置场景模式API"""
    scene = request.json.get('scene', 'auto')
    
    scenes = {
        'lecture': '上课模式',
        'exam': '考试模式',
        'energy': '节能模式',
        'auto': '自动模式'
    }
    
    return jsonify({
        "success": True,
        "message": f"已切换到{scenes.get(scene, scene)}模式",
        "scene": scene
    })

# ============ 5. 后台任务 ============
def background_task():
    """后台任务：模拟数据更新和自动控制"""
    # 初始化数据库
    init_database()
    
    print("🔄 后台任务启动，开始模拟数据...")
    
    while True:
        try:
            # 1. 生成模拟传感器数据
            new_data = {
                "temperature": round(20 + random.uniform(-2, 5), 1),  # 18-25°C
                "humidity": random.randint(40, 70),                   # 40-70%
                "light": random.randint(0, 1000),                    # 0-1000 lux
                "co2": random.randint(400, 1500),                    # 400-1500 ppm
                "pir": random.choice([0, 1])                         # 0:无人 1:有人
            }
            
            # 2. 更新全局数据
            global current_sensor_data
            current_sensor_data.update(new_data)
            
            # 3. 保存到数据库
            save_sensor_data(new_data)
            
            # 4. 执行自动控制逻辑
            commands = auto_control_logic(new_data)
            for cmd in commands:
                print(f"🤖 自动控制: {cmd['device']} -> {cmd['command']}")
                
                # 更新设备状态
                for actuator in devices["actuators"]:
                    if actuator["id"] == cmd["device"]:
                        actuator["status"] = cmd["command"]
                        break
            
            # 5. 等待5秒
            time.sleep(5)
            
        except Exception as e:
            print(f"后台任务出错: {e}")
            time.sleep(10)

# ============ 6. 启动函数 ============
def start_background_thread():
    """启动后台线程"""
    thread = threading.Thread(target=background_task, daemon=True)
    thread.start()
    print("✅ 后台线程已启动")

# ============ 7. 主程序入口 ============
if __name__ == '__main__':
    # 启动后台任务
    start_background_thread()
    
    # 启动Web服务器
    print("\n" + "="*50)
    print("🏫 智慧教室监控系统")
    print("="*50)
    print("🌐 访问地址: http://localhost:5000")
    print("📊 数据更新: 每5秒自动更新")
    print("🤖 自动控制: 已启用")
    print("💾 数据保存: SQLite数据库")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)