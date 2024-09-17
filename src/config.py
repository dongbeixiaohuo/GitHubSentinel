import json
import os
from logger import LOG

class Config:
    def __init__(self):
        self.config_file = 'config.json'
        print(f"当前工作目录: {os.getcwd()}")
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            LOG.debug(f"加载的配置文件内容: {json.dumps(config, indent=2)}")
            
            self.email = config.get('email', {})
            LOG.debug(f"邮件配置: {json.dumps(self.email, indent=2)}")
            
            self.email['password'] = os.environ.get('EMAIL_PASSWORD', '')
            LOG.debug(f"邮箱密码长度: {len(self.email['password'])}")
            
            if 'receivers' in self.email:
                for key, value in self.email['receivers'].items():
                    LOG.debug(f"收件人 ({key}): {', '.join(value)}")
            else:
                LOG.warning("配置文件中没有找到 receivers 设置")
            
            # 设置配置项
            self.github_token = config.get('github_token', '')
            self.subscriptions_file = config.get('subscriptions_file', 'subscriptions.json')
            self.freq_days = config.get('freq_days', 2)
            self.exec_time = config.get('exec_time', '09:00')
            
            # 邮件配置
            self.email = config.get('email', {})
            self.email['password'] = os.environ.get('EMAIL_PASSWORD', '')
            LOG.debug(f"邮箱密码长度: {len(self.email['password'])}")  # 不要记录实际密码，只记录长度
            
            # 确保 receivers 配置存在
            if 'receivers' not in self.email:
                self.email['receivers'] = {
                    "cybersecurity": ["tom.xia@linemore.com"],
                    "github": ["dante.sun@linemore.com"],
                    "all": ["dante.sun@linemore.com"]
                }
                LOG.info("已设置默认的 receivers")
            
            self.report_types = config.get('report_types', ['github', 'cybersecurity'])
            self.openai_models = config.get('openai_models', ['gpt-4o', 'gpt-4o-mini'])
            self.ollama_models = config.get('ollama_models', ['llama2', 'mistral'])
            self.ollama_api_url = config.get('ollama_api_url', 'http://localhost:11434/api/generate')
            
            # 添加默认模型类型和名称
            self.default_model_type = config.get('default_model_type', 'openai')
            self.default_model_name = config.get('default_model_name', 'gpt-4o')

            # 确保 cybersecurity 订阅者列表存在
            if 'cybersecurity_subscribers' not in self.email['receivers']:
                self.email['receivers']['cybersecurity_subscribers'] = []

        except FileNotFoundError:
            LOG.error(f"配置文件 {self.config_file} 不存在")
            raise
        except json.JSONDecodeError:
            LOG.error(f"配置文件 {self.config_file} 格式错误")
            raise
        except Exception as e:
            LOG.error(f"加载配置文件时发生错误：{str(e)}")
            raise

    def save_config(self):
        config = {
            'github_token': self.github_token,
            'subscriptions_file': self.subscriptions_file,
            'freq_days': self.freq_days,
            'exec_time': self.exec_time,
            'email': self.email,
            'report_types': self.report_types,
            'openai_models': self.openai_models,
            'ollama_models': self.ollama_models,
            'ollama_api_url': self.ollama_api_url,
            'default_model_type': self.default_model_type,
            'default_model_name': self.default_model_name
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            LOG.info("配置已保存")
        except Exception as e:
            LOG.error(f"保存配置文件时发生错误：{str(e)}")
            raise

    def add_cybersecurity_subscriber(self, email):
        if 'cybersecurity_subscribers' not in self.email['receivers']:
            self.email['receivers']['cybersecurity_subscribers'] = []
        if email not in self.email['receivers']['cybersecurity_subscribers']:
            self.email['receivers']['cybersecurity_subscribers'].append(email)
            self.save_config()
            return True
        return False

    def remove_cybersecurity_subscriber(self, email):
        if 'cybersecurity_subscribers' in self.email['receivers'] and email in self.email['receivers']['cybersecurity_subscribers']:
            self.email['receivers']['cybersecurity_subscribers'].remove(email)
            self.save_config()
            return True
        return False

    def get_cybersecurity_subscribers(self):
        return self.email['receivers'].get('cybersecurity_subscribers', [])

    # 其他方法保持不变...
