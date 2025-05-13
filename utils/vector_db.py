from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import json
from sentence_transformers import SentenceTransformer
import numpy as np
from langchain_community.docstore import InMemoryDocstore
from langchain_core.documents import Document

def initialize_vector_db(knowledge_db_path, vector_db_path):
    # 加载模型
    embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    
    # 创建 HuggingFaceEmbeddings 对象
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    
    # 加载知识库
    knowledge_db = []
    with open(knowledge_db_path, "r") as f:
        for line in f:
            knowledge_db.append(json.loads(line)["content"])
    
    # 创建文档列表
    docs = [Document(page_content=text) for text in knowledge_db]
    
    # 创建文档存储
    docstore = InMemoryDocstore()
    docstore._dict = {str(i): doc for i, doc in enumerate(docs)}
    
    # 创建索引到文档存储的映射
    index_to_docstore_id = {i: str(i) for i in range(len(docs))}
    
    # 初始化 FAISS 向量数据库
    vector_db = FAISS.from_documents(
        documents=docs,
        embedding=embeddings,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id
    )
    
    # 保存向量数据库
    vector_db.save_local(vector_db_path)
    return vector_db

if __name__ == "__main__":
    initialize_vector_db(
        knowledge_db_path="database/knowledge.jsonl",
        vector_db_path="database/vector_db"
    )