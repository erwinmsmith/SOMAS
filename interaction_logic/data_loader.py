import json
import os
from typing import Dict, List

class DataLoader:
    def __init__(self, config: Dict):
        self.config = config
        self.experience_pool_path = config["database"]["experience_pool"]
        self._ensure_experience_pool_file()
        
    def _ensure_experience_pool_file(self):
        if not os.path.exists(self.experience_pool_path):
            with open(self.experience_pool_path, 'w') as f:
                json.dump({"experiences": []}, f)
    
    def load_experience_pool(self) -> List[Dict]:
        with open(self.experience_pool_path, 'r') as f:
            return json.load(f)["experiences"]
    
    def save_experience_pool(self, experiences: List[Dict]):
        with open(self.experience_pool_path, 'w') as f:
            json.dump({"experiences": experiences}, f, indent=2)
            
    def get_experience_pool_structure(self) -> Dict:
        return {
            "version": "1.0",
            "schema": {
                "query": "str",
                "response": "str",
                "scores": {
                    "safety": "float",
                    "usefulness": "float",
                    "completeness": "float"
                },
                "pseudo_rl_prompts": ["str"],
                "timestamp": "float"
            },
            "description": "经验池数据结构，包含查询、响应、评分和伪强化学习提示词"
        }