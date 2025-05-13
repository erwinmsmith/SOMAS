from data_loader import DataLoader
from tool_interface import CustomToolkit

class AgentExecutor:
    def __init__(self, config):
        self.data_loader = DataLoader(config["database"]["experience_pool"])
        self.toolkit = CustomToolkit()
        self.download_manager = DownloadManager(config.get("download_dir", "downloads"))
        
    def execute_plan(self, plan):
        """执行任务计划"""
        results = []
        for step in plan["steps"]:
            tool_name = step["tool"]
            params = step["params"]
            
            if not self.toolkit.validate_tool(tool_name):
                # 检查是否为下载任务
                if tool_name == "download":
                    result = self._handle_download(params)
                else:
                    raise ValueError(f"无效工具: {tool_name}")
                
            else:
                result = self.toolkit.execute_tool(tool_name, params)
            results.append(result)
            
            # 记录执行结果
            self._log_execution(step, result)
            
        return {"results": results}
    
    def _handle_download(self, params):
        """处理下载任务"""
        try:
            url = params["url"]
            filename = params.get("filename")
            
            # 下载文件
            filepath = self.download_manager.download_file(url, filename)
            
            # 如果需要执行下载的文件
            if params.get("execute", False):
                return self.download_manager.execute_downloaded_file(filepath)
                
            return {"status": "success", "filepath": filepath}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    def _log_execution(self, step, result):
        """记录执行日志"""
        execution_data = {
            "timestamp": time.time(),
            "step": step,
            "result": result
        }
        
        # 加载现有数据
        current_data = self.data_loader.load_data()
        if not isinstance(current_data, list):
            current_data = []
            
        # 追加新数据
        current_data.append(execution_data)
        self.data_loader.save_data(current_data)