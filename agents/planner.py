from langchain_community.chat_models import ChatOpenAI  # 正确的导入方式
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
import requests
import json

class Planner:
    def __init__(self, config):
        # 初始化 DeepSeek API 配置
        self.deepseek_url = "https://api.deepseek.com"
        self.api_key = config["api_keys"]["deepseek_chat"]
        # 初始化嵌入模型
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            cache_folder=config["model_paths"]["embedding_model"],
            model_kwargs={"device":"cpu", "local_files_only": False}
        )
        # 初始化向量数据库
        self.vector_db = FAISS.load_local(config["database_paths"]["vector_db"], embeddings=self.embedding_model, allow_dangerous_deserialization=True)
        # 加载安全准则
        with open(config["database_paths"]["rules_db"], 'r') as f:
            self.safety_rules = json.load(f)

    def plan(self, query):
        # 检索相关安全准则
        relevant_rules = self.vector_db.similarity_search(query, k=3)
        
        # 检查查询是否符合安全准则
        for rule in relevant_rules:
            if not self._check_safety(query, rule.page_content):
                return "Query violates safety rules: " + rule.page_content
                
        # 生成规划提示
        plan_prompt = PromptTemplate(
            template="Given the safety rules {rules}, plan for the query: {query}",
            input_variables=["rules", "query"]
        )
        prompt = plan_prompt.format(rules=relevant_rules, query=query)
        
        # 使用 DeepSeek API 进行规划
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a safety-focused planner. Always consider safety rules first."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0
        }
        response = requests.post(self.deepseek_url, headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"]
        
    def rag_guidelines(self):
        """从数据库中检索安全准则"""
        return [rule.page_content for rule in self.vector_db.similarity_search("safety guidelines", k=5)]
        
    def _check_safety(self, query, rule):
        """使用RAG检索后的提示词模板进行安全约束"""
        safety_prompt = PromptTemplate(
            template="""根据以下安全规则:
{rule}

请评估以下查询是否符合安全要求:
{query}

请回答'是'或'否'，并简要说明原因:""",
            input_variables=["rule", "query"]
        )
        prompt = safety_prompt.format(rule=rule, query=query)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个安全评估专家，请严格评估查询是否符合安全规则"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0
        }
        response = requests.post(self.deepseek_url, headers=headers, json=data)
        return "是" in response.json()["choices"][0]["message"]["content"].lower()