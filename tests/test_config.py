import unittest
import json
import os
from src.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        # 创建测试用的配置文件
        self.test_config = {
            'github_token': 'test_token',
            'notification_settings': {'enabled': True},
            'subscriptions_file': 'test_subscriptions.json',
            'update_interval': 3600
        }
        with open('config.json', 'w') as f:
            json.dump(self.test_config, f)

    def tearDown(self):
        # 清理测试配置文件
        if os.path.exists('config.json'):
            os.remove('config.json')

    def test_load_config(self):
        config = Config()
        self.assertEqual(config.github_token, 'test_token')
        self.assertEqual(config.notification_settings, {'enabled': True})
        self.assertEqual(config.subscriptions_file, 'test_subscriptions.json')
        self.assertEqual(config.update_interval, 3600) 