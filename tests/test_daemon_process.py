import unittest
from unittest.mock import patch, MagicMock, call
from src.daemon_process import run_scheduler, main

class TestDaemonProcess(unittest.TestCase):
    def setUp(self):
        self.patches = [
            patch('src.daemon_process.Config'),
            patch('src.daemon_process.GitHubClient'),
            patch('src.daemon_process.Notifier'),
            patch('src.daemon_process.LLM'),
            patch('src.daemon_process.ReportGenerator'),
            patch('src.daemon_process.SubscriptionManager'),
            patch('src.daemon_process.Scheduler'),
            patch('threading.Thread'),
            patch('daemon.DaemonContext'),
            patch('time.sleep')
        ]
        self.mocks = [p.start() for p in self.patches]
        self.mock_scheduler = self.mocks[6].return_value
        self.mock_thread = self.mocks[7].return_value
        self.mock_daemon = self.mocks[8].return_value

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_run_scheduler_normal(self):
        run_scheduler(self.mock_scheduler)
        self.mock_scheduler.start.assert_called_once()

    def test_run_scheduler_exception(self):
        self.mock_scheduler.start.side_effect = Exception('Test error')
        run_scheduler(self.mock_scheduler)
        self.mock_scheduler.start.assert_called_once()

    def test_main_normal_execution(self):
        self.mocks[9].side_effect = [None, KeyboardInterrupt]  # sleep twice then exit
        main()
        self.mock_thread.start.assert_called_once()
        self.mock_daemon.assert_called_once()

    def test_main_daemon_exception(self):
        self.mock_daemon.__enter__.side_effect = Exception('Test error')
        main()
        self.mock_thread.start.assert_called_once()

    def test_main_thread_exception(self):
        self.mock_thread.start.side_effect = Exception('Test error')
        main()
        self.mock_daemon.assert_called_once()