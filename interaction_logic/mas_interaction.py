import json
import time
from config import config
from agents.planner import Planner
from agents.actor import Actor
from agents.rewarder import Rewarder
from agents.quiz_master import QuizMaster

class MASInteraction:
    def __init__(self, debug_mode=False, enable_pseudo_rl=True, enable_ppo=True):
        self.config = config
        self.planner = Planner(self.config)
        self.actor = Actor(self.config["actor"])
        self.rewarder = Rewarder(self.config["rewarder"])
        self.load_experience_pool()
        self.dialogue_queue = []  # 对话队列(仅用于实时监控)
        self.dialogue_cache = {}  # 对话缓存
        self.dialogue_log_path = "data/dialogue_log.jsonl"  # 对话日志文件路径
        self.debug_mode = debug_mode
        self.enable_pseudo_rl = enable_pseudo_rl
        self.enable_ppo = enable_ppo
        self.dialogue_round = 0  # 对话轮次计数器
        self._initialized = True
        
    def is_initialized(self):
        """检查MASInteraction是否已初始化"""
        return getattr(self, '_initialized', False)

    def load_experience_pool(self):
        try:
            with open(self.config["database"]["experience_pool"], "r") as f:
                self.experience_pool = json.load(f)["experiences"]
        except FileNotFoundError:
            self.experience_pool = []
            if self.debug_mode:
                print("[DEBUG] 经验池文件不存在，创建空经验池")
        except json.JSONDecodeError:
            self.experience_pool = []
            if self.debug_mode:
                print("[DEBUG] 经验池文件格式错误，创建空经验池")

    def save_experience_pool(self):
        try:
            with open(self.config["database"]["experience_pool"], "w") as f:
                json.dump({"experiences": self.experience_pool}, f)
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] 保存经验池失败: {e}")
        
        # 同时保存对话队列到日志文件
        try:
            with open(self.dialogue_log_path, "a") as log_file:
                for dialogue in self.dialogue_queue:
                    log_file.write(json.dumps(dialogue) + "\n")
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] 保存对话日志失败: {e}")

    def online_mode(self, user_query):
        # 缓存检查
        if user_query in self.dialogue_cache:
            return self.dialogue_cache[user_query]
            
        if self.debug_mode:
            print(f"[DEBUG] 用户查询: {user_query}")
            
        # RAG准则数据库
        guidelines = self.planner.rag_guidelines()
        
        if self.debug_mode:
            print(f"[DEBUG] RAG准则: {guidelines}")
            
        # 任务规划与工具选择
        plan = self.planner.plan(user_query, guidelines)
        
        if self.debug_mode:
            print(f"[DEBUG] 任务计划: {plan}")
            
        # 执行工具并获取响应
        system_response = self.actor.execute(plan)
        
        if self.debug_mode:
            print(f"[DEBUG] 系统响应: {system_response}")
            
        # 实时监控与评分
        self.dialogue_round += 1  # 轮次计数
        if self.dialogue_round > 1:  # 第一轮不调用rewarder
            scores = self.rewarder.evaluate(
                system_response, 
                user_query,
                metrics=["safety", "usefulness", "completeness"]
            )
        else:
            scores = {"safety": 3, "usefulness": 3, "completeness": 3}  # 中立评分
        
        if self.debug_mode:
            print(f"[DEBUG] 评分结果: {scores}")
        else:
            print("\n=== 评分结果 ===")
            print(f"安全性评分: {scores['safety']:.1f}/6.0")
            print(f"有用性评分: {scores['usefulness']:.1f}/6.0")
            print(f"完整性评分: {scores['completeness']:.1f}/6.0")
            print("===============\n")
        
        # 记录对话历史
        self.dialogue_queue.append({
            "timestamp": time.time(),
            "query": user_query,
            "response": system_response
        })
        
        # 维护队列大小并将超出队列的对话存入日志
        if len(self.dialogue_queue) > 100:
            removed_dialogue = self.dialogue_queue.pop(0)
            with open(self.dialogue_log_path, "a") as log_file:
                log_file.write(json.dumps(removed_dialogue) + "\n")
            
        # 添加缓存
        self.dialogue_cache[user_query] = system_response
        
        # 检查经验池大小限制
        if len(self.experience_pool) >= 1000:
            if self.debug_mode:
                print("[DEBUG] 经验池已满(1000条)，丢弃最早样本")
            self.experience_pool.pop(0)
            
        # 记录经验数据
        if self.enable_pseudo_rl:
            self.experience_pool.append({
                "query": user_query,
                "response": system_response,
                "scores": scores,
                "pseudo_rl_prompts": self.actor.get_pseudo_rl_prompts()
            })
        else:
            self.experience_pool.append({
                "query": user_query,
                "response": system_response,
                "scores": scores
            })
        
        # 检查样本量并执行PPO
        if len(self.experience_pool) >= 100 and self.enable_ppo:
            samples = random.sample(self.experience_pool, 50)
            self.actor.ppo_update(samples)
            if self.enable_pseudo_rl:
                self.actor.clear_pseudo_rl_prompts()
            
            if self.debug_mode:
                print("[DEBUG] 执行PPO更新")
            
        self.save_experience_pool()
        return system_response

    def perform_ppo_update(self):
        if len(self.experience_pool) < 50:
            if self.debug_mode:
                print("[DEBUG] 经验池样本不足50个，跳过PPO更新")
            return
            
        samples = random.sample(self.experience_pool, 50)
        self.actor.ppo_update(samples)
        if self.enable_pseudo_rl:
            self.actor.clear_pseudo_rl_prompts()
        self.experience_pool = []
        
        if self.debug_mode:
            print("[DEBUG] 执行PPO更新")
        self.save_experience_pool()

    def offline_mode(self):
        quiz_master = QuizMaster(self.config["database"]["knowledge_db"])
        questions = quiz_master.generate_quiz(100)
        
        for question in questions:
            # 模拟现场情况
            scenario = quiz_master.generate_scenario(question)
            
            if self.debug_mode:
                print(f"[DEBUG] 测试场景: {scenario}")
            
            # 联合执行
            plan = self.planner.plan(scenario)
            
            if self.debug_mode:
                print(f"[DEBUG] 测试计划: {plan}")
            
            system_response = self.actor.execute(plan)
            
            if self.debug_mode:
                print(f"[DEBUG] 测试响应: {system_response}")
            
            # 人工评分
            print(f"\nScenario: {scenario}")
            print(f"Response: {system_response}")
            print("\n请对以下指标进行评分(1-6分):")
            print("1. 安全性 - 内容是否安全无害")
            print("2. 有用性 - 回答是否解决了问题")
            print("3. 完整性 - 回答是否全面详细\n")
            human_scores = {
                "safety": int(input("安全性评分(1-6): ")),
                "usefulness": int(input("有用性评分(1-6): ")),
                "completeness": int(input("完整性评分(1-6): "))
            }
            
            if self.debug_mode:
                print(f"[DEBUG] 人工评分: {human_scores}")
            
            # 记录经验数据
            self.experience_pool.append({
                "scenario": scenario,
                "response": system_response,
                "scores": human_scores
            })
            self.save_experience_pool()
        
        # 完成所有题目后执行PPO
        if self.enable_ppo:
            self.actor.ppo_update(self.experience_pool)
            if self.debug_mode:
                print("[DEBUG] 执行PPO更新")
            self.experience_pool = []
            self.save_experience_pool()