import json
import schedule # 导入 schedule 实现定时任务执行器
import time  # 导入time库，用于控制时间间隔
import os   # 导入os模块用于文件和目录操作
import signal  # 导入signal库，用于信号处理
import sys  # 导入sys库，用于执行系统相关的操作
from datetime import datetime  # 导入 datetime 模块用于获取当前日期

from config import Config  # 导入配置管理类
from github_client import GitHubClient  # 导入GitHub客户端类，处理GitHub API请求
from cybersecurity_client import CybersecurityClient  # 更改这里
from notifier import Notifier  # 导入通知器类，用于发送通知
from report_generator import ReportGenerator  # 导入报告生成器类
from llm import LLM  # 导入语言模型类，可能用于生成报告内容
from subscription_manager import SubscriptionManager  # 导入订阅管理器类，管理GitHub仓库订阅
from logger import LOG  # 导入日志记录器


def graceful_shutdown(signum, frame):
    # 优雅关闭程序的函数，处理信号时调用
    LOG.info("[优雅退出]守护进程接收到终止信号")
    sys.exit(0)  # 安全退出程序

def github_job(subscription_manager, github_client, report_generator, notifier, days):
    LOG.info("[开始执行定时任务]GitHub Repo 项目进展报告")
    subscriptions = subscription_manager.list_subscriptions()
    LOG.info(f"订阅列表：{subscriptions}")
    for repo in subscriptions:
        try:
            LOG.info(f"处理仓库: {repo}")
            markdown_file_path = github_client.export_progress_by_date_range(repo, days)
            LOG.info(f"生成的 Markdown 文件路径: {markdown_file_path}")
            report, _ = report_generator.generate_github_report(markdown_file_path, repo)
            LOG.info(f"生成报告完成，准备发邮件")
            notifier.notify_github_report(repo, report)
        except Exception as e:
            LOG.error(f"处理仓库 {repo} 时发生错误: {e}", exc_info=True)
    LOG.info("[定时任务执行完毕]")

def cybersecurity_topic_job(cybersecurity_client, report_generator):
    LOG.info("[开始执行定时任务]网络安全热点话题跟踪")
    markdown_file_path = cybersecurity_client.export_latest_news()  # 更改这里
    _, _ = report_generator.generate_cybersecurity_report(markdown_file_path)  # 更改这里
    LOG.info(f"[定时任务执行完毕]")


def cybersecurity_daily_job(cybersecurity_client, report_generator, notifier):
    LOG.info("[开始执行定时任务]网络安全每日前沿技术趋势")
    date = datetime.now().strftime('%Y-%m-%d')
    directory_path = os.path.join('cybersecurity', date)
    
    # 确保目录存在
    os.makedirs(directory_path, exist_ok=True)
    
    # 获取最新的网络安全新闻
    top_stories = cybersecurity_client.fetch_top_stories()
    
    # 将获取的新闻保存到指定目录
    for i, story in enumerate(top_stories, 1):
        file_name = f"article_{i}.md"
        file_path = os.path.join(directory_path, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {story['title']}\n\n")
            f.write(f"链接：{story['link']}\n\n")
            f.write(f"时间：{story['time'].strftime('%Y-%m-%d') if story['time'] else '未知'}\n\n")
            f.write(f"内容：{story['content']}\n")
    
    try:
        report, report_file_path = report_generator.generate_cybersecurity_report(directory_path)
        if report and report != "No content to report":
            notifier.notify_cybersecurity_report(date, report)
            LOG.info(f"[定时任务执行完毕] 报告已生成并发送：{report_file_path}")
        else:
            LOG.warning("没有生成报告或报告内容为空")
    except Exception as e:
        LOG.error(f"生成网络安全报告时发生错误：{str(e)}")

def send_test_email(notifier):
    LOG.info("[测试邮件] 正在发送测试邮件")
    subject = "GitHubSentinel 启动测试"
    content = f"GitHubSentinel 守护进程已于 {datetime.now()} 成功启动。这是一封测试邮件，用于验证邮件功能是否正常。"
    try:
        notifier.send_email(subject, content)
        LOG.info("[测试邮件] 测试邮件发送成功")
    except Exception as e:
        LOG.error(f"[测试邮件] 发送测试邮件时发生错误：{str(e)}")

def main():
    # 设置信号处理器
    signal.signal(signal.SIGTERM, graceful_shutdown)

    config = Config()  # 创建配置实例
    LOG.debug(f"创建 Notifier 实例，邮件设置: {json.dumps(config.email, indent=2)}")
    github_client = GitHubClient(config.github_token)  # 创建GitHub客户端实例
    cybersecurity_client = CybersecurityClient()  # 更改这里
    notifier = Notifier(config.email)  # 创建通知器实例
    llm = LLM(config, config.default_model_type, config.default_model_name)  # 使用默认模型类型和名称
    report_generator = ReportGenerator(llm, config.report_types, github_client)  # 创建报告生成器实例
    subscription_manager = SubscriptionManager(config.subscriptions_file)  # 创建订阅管理器实例

    # 启动时立即执行一次任务（如不需要可注释）
    cybersecurity_daily_job(cybersecurity_client, report_generator, notifier)
    github_job(subscription_manager, github_client, report_generator, notifier, config.freq_days)

    # 安排 GitHub 的定时任务，每天晚上 9 点执行
    schedule.every().day.at("21:00").do(github_job, subscription_manager, github_client, report_generator, notifier, config.freq_days)
    
    # 安排 cybersecurity_daily_job 每天早上10点执行一次
    schedule.every().day.at("10:00").do(cybersecurity_daily_job, cybersecurity_client, report_generator, notifier)

    try:
        # 在守护进程中持续运行
        while True:
            schedule.run_pending()
            time.sleep(1)  # 短暂休眠以减少 CPU 使用
    except Exception as e:
        LOG.error(f"主进程发生异常: {str(e)}")
        sys.exit(1)



if __name__ == '__main__':
    main()
