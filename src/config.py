import os
import json
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()  # 加载 .env 文件中的环境变量

        # 读取 config.json 文件
        try:
            with open('config.json', 'r') as config_file:
                config_data = json.load(config_file)
        except FileNotFoundError:
            raise FileNotFoundError("config.json file not found. Please make sure it exists in the correct directory.")
        except json.JSONDecodeError:
            raise ValueError("config.json is not a valid JSON file. Please check its content.")

        self.github_token = os.getenv('GITHUB_TOKEN')
        self.subscriptions_file = config_data.get('subscriptions_file', 'subscriptions.json')
        
        # 从 config.json 读取邮件设置
        email_config = config_data.get('email', {})
        self.email_settings = {
            'smtp_server': email_config.get('smtp_server'),
            'smtp_port': email_config.get('smtp_port', 465),
            'from': email_config.get('from'),
            'to': email_config.get('to'),
            'password': email_config.get('password') or os.getenv('EMAIL_PASSWORD')
        }

        # 验证必要的配置
        if not self.github_token:
            raise ValueError("GitHub token is not set in config.json.")
        
        missing_settings = [key for key, value in self.email_settings.items() if not value]
        if missing_settings:
            raise ValueError(f"The following email settings are missing or empty: {', '.join(missing_settings)}. "
                             f"Please check your config.json file and EMAIL_PASSWORD environment variable.")

        # 其他设置
        self.slack_webhook_url = config_data.get('slack_webhook_url')
        self.freq_days = config_data.get('github_progress_frequency_days', 1)
        self.exec_time = config_data.get('github_progress_execution_time', "08:00")

        print("Config loaded successfully.")
        print("Email settings:", self.email_settings)
