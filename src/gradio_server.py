import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器
from hacknews import fetch_hackernews_top_stories, save_stories_to_markdown
from cyber_security import CybersecurityClient  # 导入网络安全模块

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)
cybersecurity_client = CybersecurityClient()

def generate_report(fetch_func, save_dir, generate_func, log_prefix):
    try:
        LOG.info(f"[{log_prefix}] 开始抓取新闻")
        top_stories = fetch_func()
        LOG.info(f"[{log_prefix}] 成功爬取 {len(top_stories)} 条新闻")
        
        markdown_file_path = save_stories_to_markdown(top_stories, save_dir)
        LOG.info(f"[{log_prefix}] 新闻已保存到: {markdown_file_path}")
        
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        processed_report = generate_func(markdown_content)
        LOG.info(f"[{log_prefix}] 日报生成成功")
        
        return processed_report, markdown_file_path
    except Exception as e:
        LOG.error(f"[{log_prefix}] 任务执行失败: {e}")
        return f"{log_prefix} 任务执行失败: {e}", None

def export_progress_by_date_range(repo, days):
    try:
        if not repo or not isinstance(days, int) or days <= 0:
            raise ValueError("无效的输入参数")
        
        LOG.info(f"开始导出项目 {repo} 的 {days} 天进展报告")
        raw_file_path = github_client.export_progress_by_date_range(repo, days)
        report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)
        LOG.info(f"项目 {repo} 的 {days} 天进展报告生成成功")
        return report, report_file_path
    except Exception as e:
        LOG.error(f"导出项目进展报告失败: {e}")
        return f"导出项目进展报告失败: {e}", None

def generate_hackernews_report():
    return generate_report(fetch_hackernews_top_stories, "hackernews_reports", report_generator.generate_hackernews_report, "Hacker News")

def generate_cybersecurity_report():
    return generate_report(cybersecurity_client.fetch_top_stories, "cybersecurity_reports", report_generator.generate_hackernews_report, "Cybersecurity")

# 创建Gradio界面
with gr.Blocks(title="GitHubSentinel") as demo:
    gr.Markdown("# GitHubSentinel")
    
    with gr.Tab("GitHub项目报告"):
        gr.Markdown("## 生成GitHub项目报告")
        repo_dropdown = gr.Dropdown(subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目")
        days_slider = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天")
        github_submit = gr.Button("生成报告")
        github_output = gr.Markdown()
        github_file = gr.File(label="下载报告")
        
        github_submit.click(export_progress_by_date_range, inputs=[repo_dropdown, days_slider], outputs=[github_output, github_file])
    
    with gr.Tab("Hacker News报告"):
        gr.Markdown("## 生成Hacker News报告")
        hackernews_submit = gr.Button("生成Hacker News报告")
        hackernews_output = gr.Markdown()
        hackernews_file = gr.File(label="下载原始Markdown文件")
        
        hackernews_submit.click(generate_hackernews_report, inputs=[], outputs=[hackernews_output, hackernews_file])

    with gr.Tab("Cybersecurity报告"):
        gr.Markdown("## 生成Cybersecurity报告")
        cybersecurity_submit = gr.Button("生成Cybersecurity报告")
        cybersecurity_output = gr.Markdown()
        cybersecurity_file = gr.File(label="下载原始Markdown文件")
        
        cybersecurity_submit.click(generate_cybersecurity_report, inputs=[], outputs=[cybersecurity_output, cybersecurity_file])

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))