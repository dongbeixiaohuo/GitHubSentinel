import gradio as gr  # 导入gradio库用于创建GUI
import os
from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 确保导入 GitHubClient
from cybersecurity_client import CybersecurityClient  # 更改这里
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 初始化配置
config = Config()
print(f"Entire config object: {vars(config)}")  # 打印整个配置对象

# 打印调试信息
print(f"Config subscriptions_file: {config.subscriptions_file}")

# 确保 subscriptions_file 被正确设置
if not config.subscriptions_file:
    raise ValueError("config.subscriptions_file is not set. Please check your configuration.")

# 初始化各个客户端
github_client = GitHubClient(config.github_token)  # 创建 GitHub 客户端实例
cybersecurity_client = CybersecurityClient()  # 更改这里
subscription_manager = SubscriptionManager(config.subscriptions_file)

def generate_github_report(model_type, model_name, repo, days):
    llm = LLM(config, model_type, model_name)
    report_generator = ReportGenerator(llm, config.report_types, github_client)
    
    try:
        report, report_file_path = report_generator.generate_github_report(repo, days)
        return report, report_file_path
    except Exception as e:
        LOG.error(f"生成报告时发生错误：{e}")
        return f"错误：{str(e)}", None

def generate_cybersecurity_report(model_type, model_name):  # 更改这里
    llm = LLM(config, model_type, model_name)
    report_generator = ReportGenerator(llm, config.report_types, github_client)

    markdown_file_path = cybersecurity_client.export_top_stories()  # 更改这里
    report, report_file_path = report_generator.generate_cybersecurity_report(markdown_file_path)  # 更改这里

    return report, report_file_path

def update_model_list(model_type):
    if model_type == "openai":
        return gr.Dropdown(choices=config.openai_models, label="选择模型")
    elif model_type == "ollama":
        return gr.Dropdown(choices=config.ollama_models, label="选择模型")

# 创建 Gradio 界面
with gr.Blocks(title="GitHubSentinel") as demo:
    # GitHub 项目进展 Tab
    with gr.Tab("GitHub 项目进展"):
        gr.Markdown("## GitHub 项目进展")
        model_type = gr.Radio(["openai", "ollama"], label="模型类型", info="使用 OpenAI GPT API 或 Ollama 私有化模型服务")
        model_name = gr.Dropdown(choices=config.openai_models, label="选择模型")
        subscription_list = gr.Dropdown(subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目")
        days = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天")
        model_type.change(fn=update_model_list, inputs=model_type, outputs=model_name)
        button = gr.Button("生成报告")
        markdown_output = gr.Markdown()
        file_output = gr.File(label="下载报告")
        button.click(generate_github_report, inputs=[model_type, model_name, subscription_list, days], outputs=[markdown_output, file_output])

    # Cybersecurity 热点话题 Tab
    with gr.Tab("Cybersecurity 热点话题"):  # 更改这里
        gr.Markdown("## Cybersecurity 热点话题")  # 更改这里
        model_type = gr.Radio(["openai", "ollama"], label="模型类型", info="使用 OpenAI GPT API 或 Ollama 私有化模型服务")
        model_name = gr.Dropdown(choices=config.openai_models, label="选择模型")
        model_type.change(fn=update_model_list, inputs=model_type, outputs=model_name)
        button = gr.Button("生成最新网络安全热点")  # 更改这里
        markdown_output = gr.Markdown()
        file_output = gr.File(label="下载报告")
        button.click(generate_cybersecurity_report, inputs=[model_type, model_name], outputs=[markdown_output, file_output])  # 更改这里

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启界面并设置为公共可访问
    # 可选带有户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))