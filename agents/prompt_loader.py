import os

class PromptLoader:
    def __init__(self, prompts_dir):
        self.prompts_dir = prompts_dir
        self.prompts_cache = {}
    
    def load_prompt(self, agent_name):
        """
        加载指定agent的提示词
        :param agent_name: agent名称(不带.txt后缀)
        :return: 提示词内容字符串
        """
        if agent_name in self.prompts_cache:
            return self.prompts_cache[agent_name]
            
        prompt_file = os.path.join(self.prompts_dir, f"{agent_name}.txt")
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.prompts_cache[agent_name] = content
                return content
        except FileNotFoundError:
            raise ValueError(f"Prompt file for {agent_name} not found at {prompt_file}")