import unittest
import json
import os
from src.subscription_manager import SubscriptionManager

class TestSubscriptionManager(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_subscriptions.json'
        self.test_subscriptions = ['owner/repo1', 'owner/repo2']
        with open(self.test_file, 'w') as f:
            json.dump(self.test_subscriptions, f)
        self.manager = SubscriptionManager(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_list_subscriptions(self):
        subscriptions = self.manager.list_subscriptions()
        self.assertEqual(subscriptions, self.test_subscriptions)

    def test_add_subscription(self):
        new_repo = 'owner/repo3'
        self.manager.add_subscription(new_repo)
        self.assertIn(new_repo, self.manager.list_subscriptions())

    def test_remove_subscription(self):
        repo_to_remove = 'owner/repo1'
        self.manager.remove_subscription(repo_to_remove)
        self.assertNotIn(repo_to_remove, self.manager.list_subscriptions()) 