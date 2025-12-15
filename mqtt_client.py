# src/mqtt_client.py 顶部添加

# 设备配置
DEVICES_CONFIG = {
    "sensors": [
        {"id": "temp1", "type": "temperature", "location": "front", "mqtt_topic": "sensor/temp1"},
        {"id": "humi1", "type": "humidity", "location": "front", "mqtt_topic": "sensor/humi1"},
        {"id": "light_sensor1", "type": "light", "location": "window", "mqtt_topic": "sensor/light1"},
        {"id": "co2_sensor1", "type": "co2", "location": "middle", "mqtt_topic": "sensor/co2_1"},
        {"id": "pir1", "type": "pir", "location": "door", "mqtt_topic": "sensor/pir1"}
    ],
    "actuators": [
        {"id": "light1", "type": "light", "location": "front", "mqtt_topic": "control/light1"},
        {"id": "fan1", "type": "fan", "location": "back", "mqtt_topic": "control/fan1"},
        {"id": "curtain1", "type": "curtain", "location": "window", "mqtt_topic": "control/curtain1"},
        {"id": "ac1", "type": "ac", "location": "side", "mqtt_topic": "control/ac1"}
    ]
}

# 在MQTTClient类中添加设备管理
class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.devices = DEVICES_CONFIG
        self.sensor_data = {}  # 存储最新数据
        self.actuator_status = {}  # 存储设备状态
        
    def update_device_status(self, device_id, status):
        """更新设备状态"""
        self.actuator_status[device_id] = status