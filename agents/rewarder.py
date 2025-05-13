import json
import requests
from .prompt_loader import PromptLoader
from .reward_processor import RewardProcessor

class Rewarder:
    def __init__(self, config):
        # 初始化DeepSeek API配置
        self.api_key = config.get("api_key", "")
        self.model_name = config.get("model_name", "deepseek-chat")
        self.max_tokens = config.get("max_tokens", 512)
        self.temperature = config.get("temperature", 0.7)
        self.config = config
        self.reward_processor = RewardProcessor()
        
        # 验证必要参数
        if not self.api_key:
            raise ValueError("API key is required for Rewarder")
        if not self.model_name:
            raise ValueError("Model name is required for Rewarder")

    def evaluate(self, system_response, user_query):
        """
        基于LLM评估系统回答质量
        :param system_response: 系统生成的回答
        :param user_query: 用户原始查询
        :return: 评分字典 {safety, usefulness, completeness}
        """
        # 使用提示词加载器获取评估提示词
        prompt_loader = PromptLoader(os.path.join(os.path.dirname(__file__), "..", "prompts"))
        prompt_template = prompt_loader.load_prompt("rewarder")
        prompt = prompt_template.format(user_query=user_query, system_response=system_response)
        
        # 获取API评估结果
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        response = requests.post(
            "https://api.deepseek.com/v1/completions",
            headers=headers,
            json=data
        ).json()
        
        try:
            # 使用RewardProcessor解析评分
            scores = self.reward_processor.parse_scores(response)
            return {
                "safety": scores["safety"],
                "usefulness": scores["usefulness"],
                "completeness": scores["completeness"]
            }
        except Exception:
            # 默认评分
            return {"safety": 3, "usefulness": 3, "completeness": 3}
from .prompt_loader import PromptLoader