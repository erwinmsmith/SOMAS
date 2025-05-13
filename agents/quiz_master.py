import json
import random
import requests
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class QuizMaster:
    def __init__(self, knowledge_db_path, config):
        with open(knowledge_db_path, "r") as f:
            self.knowledge_db = json.load(f)
        
        # 初始化嵌入模型
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            cache_folder=config["model_paths"]["embedding_model"],
            model_kwargs={"device":"cpu", "local_files_only": False}
        )
        
        # 初始化向量数据库
        self.vector_db = FAISS.load_local(config["database"]["vector_db"], 
                                         embeddings=self.embedding_model, allow_dangerous_deserialization=True)
        
        # 从config获取DeepSeek API配置
        self.deepseek_url = "https://api.deepseek.com"
        self.api_key = config["api_keys"]["deepseek_chat"]

    def _call_deepseek_api(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 512
        }
        response = requests.post(self.deepseek_url, headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"]

    def generate_quiz(self, num_questions):
        # 从知识库中随机选择上下文
        contexts = random.sample(self.knowledge_db, min(5, len(self.knowledge_db)))
        
        questions = []
        for context in contexts:
            # 使用RAG检索相关文档
            similar_docs = self.vector_db.similarity_search(context["content"], k=2)
            
            # 构建DeepSeek API的提示词
            prompt = f"基于以下上下文生成一个测试问题:\n\n上下文:{context['content']}\n\n"
            prompt += "\n".join(f"相关文档:{doc.page_content}" for doc in similar_docs)
            prompt += "\n\n请生成一个清晰、具体的问题，用于测试对该主题的理解。"
            
            # 调用DeepSeek API生成问题
            question_content = self._call_deepseek_api(prompt)
            
            questions.append({
                "context": context["content"],
                "content": question_content,
                "metadata": context.get("metadata", {})
            })
            
            if len(questions) >= num_questions:
                break
                
        return questions