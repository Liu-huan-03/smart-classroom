import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

class VirtualDevice:
    def __init__(self, device_id, device_type):
        self.device_id = device_id
        self.device_type = device_type
        self.status = "off"
        
    def simulate_sensor_data(self):
        """模拟各种传感器数据"""
        if self.device_type == "temperature":
            return round(20 + random.uniform(-2, 5), 1)  # 18-25°C
        elif self.device_type == "humidity":
            return random.randint(40, 70)  # 40-70%
        elif self.device_type == "light":
            return random.randint(0, 1000)  # 0-1000 lux
        elif self.device_type == "co2":
            return random.randint(400, 1500)  # 400-1500 ppm
        elif self.device_type == "pir":
            return random.choice([0, 1])  # 0:无人 1:有人
        return None
    
    def control(self, command):
        """模拟执行器控制"""
        if command == "on":
            self.status = "on"
            return {"status": "success", "power": random.randint(10, 100)}
        elif command == "off":
            self.status = "off"
            return {"status": "success", "power": 0}
        return {"status": "error"}