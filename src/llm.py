import os
import openai  # 确保导入正确的 openai 库
from logger import LOG

class LLM:
    def __init__(self, system_message=None):
        # 从环境变量中获取 OpenAI 的 API 密钥
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API 密钥未设置。请确保已在环境变量中配置 OPENAI_API_KEY。")

        # 设置自定义 API 基地址
        self.base_url = "https://api.javis3000.com/v1/"

        # 配置 OpenAI 全局设置
        openai.api_key = self.api_key
        openai.base_url = self.base_url
        
        # 设置日志文件
        LOG.add("daily_progress/llm_logs.log", rotation="1 MB", level="DEBUG")
        
        # 保存 system role 的消息
        self.system_message = system_message or "你是一个帮助生成项目简报的助手。"

    def generate_daily_report(self, markdown_content, dry_run=False):
        # 生成提示内容
        prompt = f"以下是项目的最新进展，根据功能合并同类项，形成一份简报包含：1）新增功能部分，请列出所有新增功能，并按功能模块或重要性进行分类；对于每个功能，说明其实际作用、对用户或开发者的影响，并提供至少一个具体的应用场景或实例；2）主要改进部分，按功能模块分类，总结项目在性能、稳定性或可用性方面的主要改进；详细说明每项改进如何提升项目的整体表现，并突出性能和效率优化的具体效果；3）在修复问题部分，列出所有修复的问题，并按重要性或功能模块进行分类；说明每个修复的具体问题、修复后的改善效果，以及它如何提高了用户体验或项目的稳定性；:\n\n{markdown_content}"
        
        if dry_run:
            LOG.info("Dry run 模式启用。将提示保存到文件。")
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(prompt)
            LOG.debug("提示已保存到 daily_progress/prompt.txt")
            return "DRY RUN"

        LOG.info("开始使用 GPT-4o 模型生成报告。")
        
        try:
            # 创建消息列表，包含 system role 的消息和用户的提示
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ]

            # 调用 OpenAI API 生成报告
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            
            # 从响应中提取内容
            content = response.choices[0].message.content  # 正确地访问消息内容
            
            # 确保 content 是字符串类型，然后将其写入文件
            report_file_path = "daily_progress/report.txt"
            with open(report_file_path, "w") as f:
                f.write(str(content))
            
            LOG.debug("GPT 响应: %s", content)
            return content

        except Exception as e:
            LOG.error("生成报告时发生错误: %s", str(e))
            raise