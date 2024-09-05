import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器
from hacknews import fetch_hackernews_top_stories, save_stories_to_markdown

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

def generate_hackernews_report():
    try:
        LOG.info("[开始执行Hacker News定时任务]")
        top_stories = fetch_hackernews_top_stories()
        LOG.info(f"成功爬取 {len(top_stories)} 条新闻")
        
        save_directory = "hackernews_reports"
        markdown_file_path = save_stories_to_markdown(top_stories, save_directory)
        LOG.info(f"新闻已保存到: {markdown_file_path}")
        
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        processed_report = report_generator.generate_hackernews_report(markdown_content)
        LOG.info("Hacker News 日报生成成功")
        
        return processed_report, markdown_file_path
    except Exception as e:
        LOG.error(f"Hacker News 任务执行失败: {e}")
        return str(e), None

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

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))