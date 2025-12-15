# src/web_server.py
from flask import Flask, render_template, jsonify, request
import json
import time
import threading
import random
from datetime import datetime

# 导入你创建的所有模块
try:
    from mqtt_client import MQTTClient, DEVICES_CONFIG
    from control_logic import ControlLogic
    from database import Database
except ImportError:
    # 如果导入失败，创建简单版本
    print("警告：某些模块导入失败，使用简化版本")
    DEVICES_CONFIG = {
        "sensors": [
            {"id": "temp1", "type": "temperature", "location": "front", "mqtt_topic": "sensor/temp1"},
            {"id": "humi1", "type": "humidity", "location": "front", "mqtt_topic": "sensor/humi1"},
            {"id": "light_sensor1", "type": "light", "location": "window", "mqtt_topic": "sensor/light1"},
            {"id": "co2_sensor1", "type": "co2", "location": "middle", "mqtt_topic": "sensor/co2_1"},
            {"id": "pir1", "type": "pir", "location": "door", "mqtt_topic": "sensor/pir1"}
        ],
        "actuators": [
            {"id": "light1", "type": "light", "location": "front", "mqtt_topic": "control/light1", "status": "off"},
            {"id": "fan1", "type": "fan", "location": "back", "mqtt_topic": "control/fan1", "status": "off"},
            {"id": "curtain1", "type": "curtain", "location": "window", "mqtt_topic": "control/curtain1", "status": "closed"},
            {"id": "ac1", "type": "ac", "location": "side", "mqtt_topic": "control/ac1", "status": "off"}
        ]
    }

app = Flask(__name__)

# 初始化各个模块
try:
    # 初始化数据库
    db = Database()
    
    # 初始化MQTT客户端（简单版本，不实际连接）
    class SimpleMQTTClient:
        def __init__(self):
            self.devices = DEVICES_CONFIG
            self.sensor_data = {}
            self.actuator_status = {}
        
        def update_device_status(self, device_id, status):
            self.actuator_status[device_id] = status
    
    mqtt_client = SimpleMQTTClient()
    
    # 初始化控制逻辑
    control_logic = ControlLogic()
    
except Exception as e:
    print(f"初始化模块时出错: {e}")
    # 创建最简单的回退版本
    mqtt_client = None
    control_logic = None
    db = None

# 当前传感器数据（用于Web显示）
current_sensor_data = {
    "temperature": 25.0,
    "humidity": 50.0,
    "light": 500,
    "co2": 800,
    "pir": 0
}

# ============ Web路由 ============
@app.route('/')
def index():
    """主页面"""
    return render_template('index.html', 
                         devices=DEVICES_CONFIG,
                         sensor_data=current_sensor_data)

@app.route('/api/sensor_data')
def get_sensor_data():
    """获取当前传感器数据"""
    return jsonify({
        "success": True,
        "data": current_sensor_data,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/devices')
def get_devices():
    """获取设备列表"""
    return jsonify({
        "success": True,
        "devices": DEVICES_CONFIG
    })

@app.route('/api/control', methods=['POST'])
def control_device():
    """控制设备"""
    try:
        data = request.json
        device_id = data.get('device_id')
        command = data.get('command')
        reason = data.get('reason', '手动控制')
        
        # 更新设备状态
        for actuator in DEVICES_CONFIG["actuators"]:
            if actuator["id"] == device_id:
                actuator["status"] = command
                break
        
        # 保存到数据库
        if db:
            db.save_control_command(device_id, command, reason)
        
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
def set_scene_mode():
    """设置场景模式"""
    scene = request.json.get('scene', 'auto')
    
    if control_logic:
        control_logic.scene_mode = scene
    
    return jsonify({
        "success": True,
        "message": f"已切换到 {scene} 模式",
        "scene": scene
    })

@app.route('/api/history')
def get_history():
    """获取历史数据"""
    try:
        if db:
            data = db.get_recent_data(limit=50)
            return jsonify({
                "success": True,
                "data": data
            })
        else:
            return jsonify({
                "success": False,
                "error": "数据库未初始化"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

# ============ 后台任务 ============
def background_simulation():
    """后台模拟任务：生成模拟数据并执行自动控制"""
    while True:
        try:
            # 1. 生成模拟传感器数据
            simulated_data = {
                "temperature": round(22 + random.uniform(-3, 8), 1),
                "humidity": random.randint(40, 75),
                "light": random.randint(0, 1000),
                "co2": random.randint(400, 1500),
                "pir": random.choice([0, 0, 0, 1])  # 25%概率有人
            }
            
            # 2. 更新当前显示数据
            global current_sensor_data
            current_sensor_data.update(simulated_data)
            
            # 3. 保存到数据库
            if db:
                # 保存各个传感器的数据
                db.save_sensor_data("temp1", "temperature", simulated_data["temperature"], "°C")
                db.save_sensor_data("humi1", "humidity", simulated_data["humidity"], "%")
                db.save_sensor_data("light_sensor1", "light", simulated_data["light"], "lux")
                db.save_sensor_data("co2_sensor1", "co2", simulated_data["co2"], "ppm")
                db.save_sensor_data("pir1", "pir", simulated_data["pir"], "")
            
            # 4. 执行自动控制逻辑
            if control_logic:
                if control_logic.scene_mode == "auto":
                    commands = control_logic.auto_control_logic(simulated_data)
                    
                    # 执行控制命令
                    for cmd in commands:
                        print(f"🔄 自动控制: {cmd['device']} -> {cmd['command']} ({cmd.get('reason', '')})")
                        
                        # 更新设备状态
                        for actuator in DEVICES_CONFIG["actuators"]:
                            if actuator["id"] == cmd["device"]:
                                actuator["status"] = cmd["command"]
                                break
                        
                        # 保存控制记录
                        if db:
                            db.save_control_command(
                                cmd["device"], 
                                cmd["command"], 
                                cmd.get("reason", "自动控制")
                            )
            
            # 5. 等待5秒
            time.sleep(5)
            
        except Exception as e:
            print(f"后台任务出错: {e}")
            time.sleep(10)

# ============ 启动应用 ============
if __name__ == '__main__':
    # 启动后台模拟线程
    sim_thread = threading.Thread(target=background_simulation, daemon=True)
    sim_thread.start()
    
    print("智慧教室监控系统启动中...")
    print("访问地址: http://localhost:5000")
    print("API接口:")
    print("  GET  /api/sensor_data    # 获取传感器数据")
    print("  GET  /api/devices        # 获取设备列表")
    print("  POST /api/control        # 控制设备")
    print("  POST /api/scene          # 设置场景模式")
    print("  GET  /api/history        # 获取历史数据")
    
    # 启动Flask服务器
    app.run(debug=True, host='0.0.0.0', port=5000)