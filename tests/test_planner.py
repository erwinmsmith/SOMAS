import unittest
from agents.planner import Planner
from config import config

class TestPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = Planner(config)
    
    def test_initialization(self):
        self.assertIsNotNone(self.planner.llm)
        self.assertIsNotNone(self.planner.vector_db)
    
    def test_generate_plan(self):
        # 测试生成计划的基本功能
        result = self.planner.generate_plan("test input")
        self.assertIsInstance(result, str)

if __name__ == "__main__":
    unittest.main()