import unittest
from unittest.mock import MagicMock
from src.command_handler import CommandHandler

class TestCommandHandler(unittest.TestCase):
    def setUp(self):
        self.github_client = MagicMock()
        self.subscription_manager = MagicMock()
        self.report_generator = MagicMock()
        self.handler = CommandHandler(
            self.github_client,
            self.subscription_manager,
            self.report_generator
        )

    def test_add_subscription(self):
        args = MagicMock(repo='owner/repo')
        self.handler.add_subscription(args)
        self.subscription_manager.add_subscription.assert_called_once_with('owner/repo')

    def test_remove_subscription(self):
        args = MagicMock(repo='owner/repo')
        self.handler.remove_subscription(args)
        self.subscription_manager.remove_subscription.assert_called_once_with('owner/repo')

    def test_list_subscriptions(self):
        self.subscription_manager.list_subscriptions.return_value = ['repo1', 'repo2']
        args = MagicMock()
        self.handler.list_subscriptions(args)
        self.subscription_manager.list_subscriptions.assert_called_once()

    def test_export_daily_progress(self):
        args = MagicMock(repo='owner/repo')
        self.handler.export_daily_progress(args)
        self.github_client.export_daily_progress.assert_called_once_with('owner/repo') 