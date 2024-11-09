import unittest
from unittest.mock import MagicMock, patch
from src.scheduler import Scheduler

class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.github_client = MagicMock()
        self.notifier = MagicMock()
        self.report_generator = MagicMock()
        self.subscription_manager = MagicMock()
        self.scheduler = Scheduler(
            self.github_client,
            self.notifier,
            self.report_generator,
            self.subscription_manager,
            interval=1
        )

    @patch('time.sleep')
    def test_run(self, mock_sleep):
        # 设置运行一次后退出
        mock_sleep.side_effect = KeyboardInterrupt()
        
        # 模拟订阅列表
        self.subscription_manager.list_subscriptions.return_value = ['owner/repo']
        
        # 运行调度器
        try:
            self.scheduler.run()
        except KeyboardInterrupt:
            pass

        # 验证调用
        self.github_client.export_daily_progress.assert_called_once_with('owner/repo')
        self.report_generator.export_daily_progress.assert_called_once() 