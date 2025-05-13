import json
import os

# 加载配置文件
config_path = "config/config.json"
with open(config_path, "r") as f:
    config = json.load(f)

# 数据库路径配置
config["database"] = {
    "rules_db": os.path.join("database", "rules.json"),
    "knowledge_db": os.path.join("database", "knowledge.jsonl"),
    "experience_pool": os.path.join("database", "experience_pool.json"),
    "vector_db": os.path.join("database", "vector_db")
}

# 智能体配置
config["planner"] = {
    "model": config["api_keys"]["deepseek_chat"],
    "vector_db_path": config["database"]["vector_db"]
}

# 合并actor配置
config["actor"] = config.get("actor", {})
config["actor"].setdefault("model_paths", {})
config["actor"]["model_paths"] = config["model_paths"]