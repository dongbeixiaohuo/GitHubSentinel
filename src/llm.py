import os
import json
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块
import openai  # 导入openai库

class LLM:
    def __init__(self):
        # 从环境变量中获取 OpenAI API Key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
        
        # 指定自定义的 API 基础 URL
        api_base_url = "https://api.javis3000.com/v1/"  # 假设API路径是这个

        # 设置OpenAI库的API密钥和自定义的API基础URL
        openai.api_key = api_key
        openai.base_url = api_base_url
        
        # 设置 self.client 为 openai 模块
        self.client = openai
        
        # 从TXT文件加载提示信息
        with open("prompts/report_prompt.txt", "r", encoding='utf-8') as file:
            self.system_prompt = file.read()

        # 加载Hacker News专用的提示信息
        with open("prompts/hackernews_prompt.txt", "r", encoding='utf-8') as file:
            self.hackernews_prompt = file.read()

    def generate_daily_report(self, markdown_content, dry_run=False):
        # 使用从TXT文件加载的提示信息
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": markdown_content},
        ]

        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                # 格式化JSON字符串的保存
                json.dump(messages, f, indent=4, ensure_ascii=False)
            LOG.debug("Prompt已保存到 daily_progress/prompt.txt")

            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("使用 GPT 模型开始生成报告。")
        
        try:
            # 调用OpenAI GPT模型生成报告
            response = self.client.chat.completions.create(
                model="gpt-4o",  # 指定使用的模型版本
                messages=messages
            )
            LOG.debug("GPT response: {}", response)
            # 返回模型生成的内容
            return response.choices[0].message.content
        except openai.APIConnectionError as e:
            LOG.error(f"OpenAI API 连接错误: {str(e)}")
            # 你可以在这里添加重试逻辑或其他处理方式
            raise
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error(f"生成报告时发生错误：{e}")
            raise

    def generate_hackernews_report(self, markdown_content):
        # 使用Hacker News专用的提示信息
        messages = [
            {"role": "system", "content": self.hackernews_prompt},
            {"role": "user", "content": markdown_content},
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content
