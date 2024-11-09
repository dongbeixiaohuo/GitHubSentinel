import unittest
from unittest.mock import patch, MagicMock
import argparse
from src.main import main, setup_logging, parse_args

class TestMain(unittest.TestCase):
    def setUp(self):
        self.config_patcher = patch('src.main.Config')
        self.github_patcher = patch('src.main.GitHubClient')
        self.notifier_patcher = patch('src.main.Notifier')
        self.report_patcher = patch('src.main.ReportGenerator')
        self.scheduler_patcher = patch('src.main.Scheduler')
        self.logger_patcher = patch('src.main.logger')
        self.parser_patcher = patch('argparse.ArgumentParser')
        
        self.mock_config = self.config_patcher.start()
        self.mock_github = self.github_patcher.start()
        self.mock_notifier = self.notifier_patcher.start()
        self.mock_report = self.report_patcher.start()
        self.mock_scheduler = self.scheduler_patcher.start()
        self.mock_logger = self.logger_patcher.start()
        self.mock_parser = self.parser_patcher.start()
        
        self.mock_args = MagicMock()
        self.mock_parser.return_value.parse_args.return_value = self.mock_args

    def tearDown(self):
        self.config_patcher.stop()
        self.github_patcher.stop()
        self.notifier_patcher.stop()
        self.report_patcher.stop()
        self.scheduler_patcher.stop()
        self.logger_patcher.stop()
        self.parser_patcher.stop()

    def test_setup_logging(self):
        logger = setup_logging()
        self.assertIsNotNone(logger)
        self.mock_logger.add.assert_called()

    def test_parse_args_export(self):
        self.mock_args.command = 'export'
        self.mock_args.repo = 'owner/repo'
        args = parse_args()
        self.assertEqual(args.command, 'export')
        self.assertEqual(args.repo, 'owner/repo')

    def test_parse_args_generate(self):
        self.mock_args.command = 'generate'
        self.mock_args.file = 'report.md'
        args = parse_args()
        self.assertEqual(args.command, 'generate')
        self.assertEqual(args.file, 'report.md')

    def test_main_export_command(self):
        self.mock_args.command = 'export'
        self.mock_args.repo = 'owner/repo'
        main()
        self.mock_github.return_value.export_daily_progress.assert_called_once_with('owner/repo')

    def test_main_generate_command(self):
        self.mock_args.command = 'generate'
        self.mock_args.file = 'report.md'
        main()
        self.mock_report.return_value.generate_daily_report.assert_called_once_with('report.md')

    def test_main_invalid_command(self):
        self.mock_args.command = 'invalid'
        with self.assertRaises(SystemExit):
            main()

    def test_main_github_error(self):
        self.mock_args.command = 'export'
        self.mock_github.return_value.export_daily_progress.side_effect = Exception('GitHub error')
        with self.assertRaises(SystemExit):
            main()
        self.mock_logger.error.assert_called()

    def test_main_report_error(self):
        self.mock_args.command = 'generate'
        self.mock_report.return_value.generate_daily_report.side_effect = Exception('Report error')
        with self.assertRaises(SystemExit):
            main()
        self.mock_logger.error.assert_called()

    def test_main_no_command(self):
        self.mock_args.command = None
        with self.assertRaises(SystemExit):
            main() 