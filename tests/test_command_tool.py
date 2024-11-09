import unittest
from unittest.mock import patch, MagicMock, call
import sys
from io import StringIO
from src.command_tool import main, create_command_handler

class TestCommandTool(unittest.TestCase):
    def setUp(self):
        self.stdout_patcher = patch('sys.stdout', new_callable=StringIO)
        self.stdin_patcher = patch('sys.stdin', new_callable=StringIO)
        self.mock_stdout = self.stdout_patcher.start()
        self.mock_stdin = self.stdin_patcher.start()
        
        # 模拟所有依赖
        self.config_patcher = patch('src.command_tool.Config')
        self.github_patcher = patch('src.command_tool.GitHubClient')
        self.notifier_patcher = patch('src.command_tool.Notifier')
        self.llm_patcher = patch('src.command_tool.LLM')
        self.report_patcher = patch('src.command_tool.ReportGenerator')
        self.sub_manager_patcher = patch('src.command_tool.SubscriptionManager')
        self.handler_patcher = patch('src.command_tool.CommandHandler')
        
        self.mock_config = self.config_patcher.start()
        self.mock_github = self.github_patcher.start()
        self.mock_notifier = self.notifier_patcher.start()
        self.mock_llm = self.llm_patcher.start()
        self.mock_report = self.report_patcher.start()
        self.mock_sub_manager = self.sub_manager_patcher.start()
        self.mock_handler = self.handler_patcher.start()

    def tearDown(self):
        self.stdout_patcher.stop()
        self.stdin_patcher.stop()
        self.config_patcher.stop()
        self.github_patcher.stop()
        self.notifier_patcher.stop()
        self.llm_patcher.stop()
        self.report_patcher.stop()
        self.sub_manager_patcher.stop()
        self.handler_patcher.stop()

    def simulate_input(self, inputs):
        """模拟用户输入"""
        if isinstance(inputs, str):
            inputs = [inputs]
        self.mock_stdin.write('\n'.join(inputs + ['exit']))
        self.mock_stdin.seek(0)

    def test_create_command_handler(self):
        handler = create_command_handler()
        self.assertIsNotNone(handler)
        self.mock_config.assert_called_once()
        self.mock_github.assert_called_once()
        self.mock_sub_manager.assert_called_once()

    def test_main_add_subscription(self):
        self.simulate_input('add owner/repo')
        main()
        self.mock_handler.return_value.handle_add.assert_called_once_with('owner/repo')

    def test_main_remove_subscription(self):
        self.simulate_input('remove owner/repo')
        main()
        self.mock_handler.return_value.handle_remove.assert_called_once_with('owner/repo')

    def test_main_list_subscriptions(self):
        self.simulate_input('list')
        main()
        self.mock_handler.return_value.handle_list.assert_called_once()

    def test_main_export_progress(self):
        self.simulate_input('export owner/repo')
        main()
        self.mock_handler.return_value.handle_export.assert_called_once_with('owner/repo')

    def test_main_generate_report(self):
        self.simulate_input('generate report.md')
        main()
        self.mock_handler.return_value.handle_generate.assert_called_once_with('report.md')

    def test_main_help(self):
        self.simulate_input('help')
        main()
        self.assertIn('Commands:', self.mock_stdout.getvalue())

    def test_main_invalid_command(self):
        self.simulate_input('invalid')
        main()
        self.assertIn('Invalid command', self.mock_stdout.getvalue())

    def test_main_empty_command(self):
        self.simulate_input('')
        main()
        self.assertIn('Invalid command', self.mock_stdout.getvalue())

    def test_main_keyboard_interrupt(self):
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            main()
        self.assertIn('Exiting', self.mock_stdout.getvalue())

    def test_main_general_exception(self):
        with patch('builtins.input', side_effect=Exception('Test error')):
            main()
        self.assertIn('Unexpected error', self.mock_stdout.getvalue()) 