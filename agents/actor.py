from langchain.llms import VLLM
import json
import datetime
import random

class Actor:
    def __init__(self, config):
        # 初始化vLLM本地模型
        self.local_model = VLLM(
            model=config["model_paths"]["local_model"],
            trust_remote_code=True,
            max_new_tokens=config.get("max_new_tokens", 512),
            temperature=config.get("temperature", 0.7)
        )
        self.tools = []  # 配置工具
        self.reward_prompts = []  # 伪强化学习提示词列表
        self.config = config
        self.experience_pool = []  # 经验池

    def execute(self, plan):
        """
        执行任务并应用伪强化学习提示词
        :param plan: 来自planner的任务规划
        :return: 系统生成的回答
        """
        # 应用当前所有奖励提示词
        prompt = plan
        for reward_prompt in self.reward_prompts:
            prompt += f"\n{reward_prompt}"
            
        response = self.local_model.invoke(prompt)
        return response
        
    def update_reward_prompts(self, scores):
        """
        根据评分更新伪强化学习提示词
        :param scores: 来自rewarder的评分字典
        """
        # 根据评分生成新的提示词
        new_prompts = []
        if scores["safety"] >= 4:
            new_prompts.append("请继续保持安全合规的回答风格。")
        else:
            new_prompts.append("请注意避免讨论危险或违法内容。")
            
        if scores["usefulness"] >= 4:
            new_prompts.append("你的回答很好地解决了用户问题。")
        else:
            new_prompts.append("请提供更有用的信息来解决用户问题。")
            
        if scores["completeness"] >= 4:
            new_prompts.append("你的回答非常全面详细。")
        else:
            new_prompts.append("请提供更完整的回答，涵盖所有相关问题点。")
            
        # 更新提示词列表（保留最近5个提示词）
        self.reward_prompts = (self.reward_prompts + new_prompts)[-5:]
        
    def add_experience(self, system_response, user_response, scores):
        """
        添加经验到经验池
        :param system_response: 系统回答
        :param user_response: 用户输入
        :param scores: 评分字典
        """
        self.experience_pool.append({
            "system_response": system_response,
            "user_response": user_response,
            "scores": scores,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # 检查是否达到PPO训练阈值
        if len(self.experience_pool) >= self.config["ppo_config"]["sample_size"]:
            self.ppo_train(self.experience_pool)
            self.experience_pool = []  # 清空经验池
            self.reward_prompts = []  # 清空提示词列表
        
    def ppo_train(self, experience_pool):
        """
        执行PPO强化学习训练
        :param experience_pool: 经验池数据
        :return: 训练结果
        """
        # 从经验池中随机抽取样本
        batch_size = min(len(experience_pool), self.config["ppo_config"]["sample_size"])
        batch = random.sample(experience_pool, batch_size)
        
        # 使用TRL库实现PPO训练
        from trl import PPOTrainer
        trainer = PPOTrainer(
            model=config["model_paths"]["local_model"],
            learning_rate=3e-4,
            batch_size=self.config["ppo_config"]["batch_size"]
        )
        trainer.step(batch)
        
        return {"status": "success", "batch_size": batch_size}