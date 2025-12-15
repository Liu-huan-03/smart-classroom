 # src/control_logic.py
import time

class ControlLogic:
    def __init__(self, device_manager=None):
        self.device_manager = device_manager
        self.scene_mode = "auto"  # auto, lecture, exam, energy
        
    def auto_control_logic(self, sensor_data):
        """基于规则的自动控制"""
        commands = []
        
        # 安全获取数据，避免KeyError
        light = sensor_data.get('light', 0)
        pir = sensor_data.get('pir', 0)
        co2 = sensor_data.get('co2', 0)
        temperature = sensor_data.get('temperature', 25)
        
        # 光照控制
        if light < 300 and pir == 1:
            commands.append({"device": "light1", "command": "on", "reason": "光照不足且有人"})
        elif light > 500 or pir == 0:
            commands.append({"device": "light1", "command": "off", "reason": "光照充足或无人"})
        
        # 空气质量控制
        if co2 > 1000:
            commands.append({"device": "fan1", "command": "on", "reason": "CO2浓度过高"})
        elif co2 < 800:
            commands.append({"device": "fan1", "command": "off", "reason": "CO2浓度正常"})
        
        # 温度控制
        if temperature > 26:
            commands.append({"device": "ac1", "command": "on", "temp": 25, "reason": "温度过高"})
        elif temperature < 22:
            commands.append({"device": "ac1", "command": "off", "reason": "温度适宜"})
        
        # 窗帘控制
        if light > 800:
            commands.append({"device": "curtain1", "command": "close", "reason": "光线过强"})
        elif light < 200:
            commands.append({"device": "curtain1", "command": "open", "reason": "需要更多光线"})
        
        return commands
    
    def scene_mode_control(self, mode, sensor_data):
        """场景模式控制"""
        commands = []
        
        if mode == "lecture":  # 上课模式
            commands.append({"device": "light1", "command": "on"})
            commands.append({"device": "ac1", "command": "on", "temp": 24})
            
        elif mode == "exam":  # 考试模式
            commands.append({"device": "light1", "command": "on"})
            commands.append({"device": "fan1", "command": "off"})
            
        elif mode == "energy":  # 节能模式
            pir = sensor_data.get('pir', 0)
            if pir == 0:  # 无人
                commands.append({"device": "light1", "command": "off"})
                commands.append({"device": "ac1", "command": "off"})
                commands.append({"device": "fan1", "command": "off"})
                
        return commands