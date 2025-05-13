import os
import requests
import time
from typing import Optional

class DownloadManager:
    def __init__(self, download_dir: str = "downloads"):
        """初始化下载管理器"""
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
    
    def download_file(self, url: str, filename: Optional[str] = None) -> str:
        """下载文件到指定目录"""
        if not filename:
            filename = os.path.basename(url)
            
        filepath = os.path.join(self.download_dir, filename)
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return filepath
        except Exception as e:
            raise Exception(f"下载失败: {str(e)}")
    
    def execute_downloaded_file(self, filepath: str) -> dict:
        """执行下载的文件"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")
            
        if not os.access(filepath, os.X_OK):
            os.chmod(filepath, 0o755)
            
        try:
            # 执行文件并返回结果
            result = os.popen(filepath).read()
            return {"status": "success", "output": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}"