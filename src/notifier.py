import smtplib
import markdown2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logger import LOG

class Notifier:
    def __init__(self, email_settings):
        self.email_settings = email_settings
    
    def notify(self, repo, report):
        if self.email_settings:
            self.send_email(repo, report)
        else:
            LOG.warning("邮件设置未配置正确，无法发送通知")
    
    def send_email(self, subject, body):
        LOG.info("准备发送邮件")
        msg = MIMEMultipart()
        msg['From'] = self.email_settings['from']
        msg['To'] = self.email_settings['to']
        msg['Subject'] = subject
        
        # 确保 body 是字符串
        if not isinstance(body, str):
            LOG.error("邮件正文不是字符串类型")
            return

        # 将 Markdown 内容转换为 HTML
        html_body = markdown2.markdown(body)

        # 确保 html_body 是字符串
        if not isinstance(html_body, str):
            LOG.error("转换后的 HTML 内容不是字符串类型")
            return

        # 添加邮件正文
        msg.attach(MIMEText(html_body, 'html'))  # 使用 'html' 发送 HTML 格式的邮件

        try:
            with smtplib.SMTP_SSL(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                LOG.debug("登录SMTP服务器")
                server.login(msg['From'], self.email_settings['password'])
                LOG.debug("SMTP登录成功")
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                LOG.info("邮件发送成功！")
        except Exception as e:
            LOG.error(f"发送邮件失败：{str(e)}")

if __name__ == '__main__':
    from config import Config
    config = Config()
    notifier = Notifier(config.email)

    test_repo = "DjangoPeng/openai-quickstart"
    test_report = """
# DjangoPeng/openai-quickstart 项目进展

## 时间周期：2024-08-24

## 新增功能
- Assistants API 代码与文档

## 主要改进
- 适配 LangChain 新版本

## 修复问题
- 关闭了一些未解决的问题。

"""
    notifier.notify(test_repo, test_report)
