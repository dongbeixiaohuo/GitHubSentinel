import smtplib
import markdown2
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from logger import LOG

class Notifier:
    def __init__(self, email_settings):
        self.email_settings = email_settings
        LOG.debug(f"Notifier 初始化，邮件设置: {json.dumps(email_settings, indent=2)}")
    
    def notify_github_report(self, repo, report):
        LOG.debug(f"开始处理 GitHub 报告通知，仓库: {repo}")
        if self.email_settings:
            subject = f"[GitHub] {repo} 进展简报"
            github_receivers = self.email_settings['receivers'].get('github', [])
            all_receivers = self.email_settings['receivers'].get('all', [])
            receivers = list(set(github_receivers + all_receivers))  # 去重
            LOG.debug(f"GitHub 收件人: {github_receivers}")
            LOG.debug(f"所有收件人: {all_receivers}")
            LOG.debug(f"最终收件人列表: {receivers}")
            
            if not receivers:
                LOG.error("GitHub 报告没有配置收件人")
                return
            self.send_email(subject, report, receivers)
        else:
            LOG.warning("邮件设置未配置正确，无法发送 GitHub 报告通知")

    # ... 其他方法 ...
    
    def notify_cybersecurity_report(self, date, report):
        if self.email_settings:
            subject = f"[网络安全] {date} 技术趋势"
            receivers = self.email_settings['receivers']['cybersecurity'] + self.email_settings['receivers']['all']
            self.send_email(subject, report, receivers)
        else:
            LOG.warning("邮件设置未配置正确，无法发送网络安全报告通知")
    
    def send_email(self, subject, report, receivers):
        if not receivers:
            LOG.error("没有指定收件人，无法发送邮件")
            return
        
        LOG.info(f"准备发送邮件:{subject}")
        LOG.debug(f"SMTP服务器: {self.email_settings['smtp_server']}")
        LOG.debug(f"SMTP端口: {self.email_settings['smtp_port']}")
        LOG.debug(f"发件人: {self.email_settings['from']}")
        LOG.debug(f"收件人: {', '.join(receivers)}")
        
        msg = MIMEMultipart()
        msg['From'] = self.email_settings['from']
        msg['To'] = ', '.join(receivers)
        msg['Subject'] = subject
        
        html_report = markdown2.markdown(report)
        msg.attach(MIMEText(html_report, 'html'))

        try:
            with smtplib.SMTP_SSL(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                LOG.debug("登录SMTP服务器")
                server.login(self.email_settings['from'], self.email_settings['password'])
                server.send_message(msg)
                LOG.info(f"邮件发送成功！接收者: {', '.join(receivers)}")
        except smtplib.SMTPRecipientsRefused as e:
            LOG.error(f"邮件发送失败，收件人被拒绝: {e}")
        except Exception as e:
            LOG.error(f"发送邮件时发生错误: {e}", exc_info=True)  # 添加 exc_info=True 以获取完整的错误堆栈

if __name__ == '__main__':
    from config import Config
    config = Config()
    notifier = Notifier(config.email)

    # 测试 GitHub 报告邮件通知
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
    notifier.notify_github_report(test_repo, test_report)

    # 测试 Hacker News 报告邮件通知
    hn_report = """
# Hacker News 前沿技术趋势 (2024-09-01)

## Top 1：硬盘驱动器的讨论引发热门讨论

关于硬盘驱动器的多个讨论，尤其是关于未使用和不需要的硬盘驱动器的文章，显示出人们对科技过时技术的兴趣。

详细内容见相关链接：

- http://tom7.org/harder/
- http://tom7.org/harder/

## Top 2：学习 Linux 的重要性和 Bubbletea 程序开发

有关于 Linux 的讨论，强调了 Linux 在现代开发中的重要性和应用性，以及关于构建 Bubbletea 程序的讨论，展示了 Bubbletea 在开发中的应用性和可能性。

详细内容见相关链接：

- https://opiero.medium.com/why-you-should-learn-linux-9ceace168e5c
- https://leg100.github.io/en/posts/building-bubbletea-programs/

## Top 3：Nvidia 在 AI 领域中的强大竞争力

有关于 Nvidia 的四个未知客户，每个人购买价值超过 3 亿美元的讨论，显示出 N 维达在 AI 领域中的强大竞争力。

详细内容见相关链接：

- https://fortune.com/2024/08/29/nvidia-jensen-huang-ai-customers/

"""
    notifier.notify_hn_report("2024-09-01", hn_report)
