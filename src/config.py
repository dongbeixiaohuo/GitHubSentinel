import os
import json

class Config:
    def __init__(self):
        self.load_config()

    def load_config(self):
        # 修改配置文件路径
        config_path = os.path.join('config', 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.github_token = config.get('github_token', '')
            self.openai_api_key = config.get('openai_api_key', '')
            self.repositories = config.get('repositories', [])