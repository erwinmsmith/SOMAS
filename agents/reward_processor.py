class RewardProcessor:
    """
    评分处理器，专门用于从评估内容中提取评分信息并计算奖励
    """
    
    @staticmethod
    def parse_scores(evaluation_text):
        """
        从评估文本中解析出评分
        :param evaluation_text: 评估文本
        :return: 评分字典 {safety, usefulness, completeness}
        """
        scores = {"safety": 3, "usefulness": 3, "completeness": 3}
        
        lines = evaluation_text.split('\n')
        for line in lines:
            if line.startswith("1. 安全性:"):
                scores["safety"] = int(line.split(":")[1].split("/")[0].strip())
            elif line.startswith("2. 有用性:"):
                scores["usefulness"] = int(line.split(":")[1].split("/")[0].strip())
            elif line.startswith("3. 完整性:"):
                scores["completeness"] = int(line.split(":")[1].split("/")[0].strip())
        
        return scores
    
    @staticmethod
    def calculate_reward(scores):
        """
        根据评分计算奖励值
        :param scores: 评分字典
        :return: 奖励值
        """
        # 简单加权计算
        return scores["safety"] * 0.4 + scores["usefulness"] * 0.3 + scores["completeness"] * 0.3