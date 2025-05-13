import json

class DataLoader:
    def __init__(self, data_path):
        self.data_path = data_path
        
    def load_data(self):
        """加载JSON格式的经验数据"""
        with open(self.data_path, 'r') as f:
            return json.load(f)
            
    def save_data(self, data):
        """保存经验数据到JSON文件"""
        with open(self.data_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def append_data(self, new_data):
        """追加新的经验数据"""
        data = self.load_data()
        if isinstance(data, list):
            data.append(new_data)
        elif isinstance(data, dict):
            data.update(new_data)
        self.save_data(data)