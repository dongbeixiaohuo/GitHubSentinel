import unittest
from unittest.mock import patch, MagicMock
from src.llm import LLM

class TestLLM(unittest.TestCase):
    def setUp(self):
        self.llm = LLM()

    @patch('openai.OpenAI')
    def test_generate_daily_report(self, mock_openai):
        # 模拟 OpenAI 响应
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test Report"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # 测试正常生成报告
        result = self.llm.generate_daily_report("Test Content")
        self.assertEqual(result, "Test Report")

    def test_generate_daily_report_dry_run(self):
        # 测试 dry run 模式
        result = self.llm.generate_daily_report("Test Content", dry_run=True)
        self.assertIsNotNone(result) 