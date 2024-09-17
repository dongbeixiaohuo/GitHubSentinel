import json
import os
import requests
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块

class LLM:
    def __init__(self, config, model_type, model_name):
        self.config = config
        self.model_type = model_type.lower()
        self.model_name = model_name

        if self.model_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
            api_base_url = "https://api.javis3000.com/v1/"
            self.client = OpenAI(api_key=api_key, base_url=api_base_url)
        elif self.model_type == "ollama":
            self.api_url = config.ollama_api_url
        else:
            LOG.error(f"不支持的模型类型: {self.model_type}")
            raise ValueError(f"不支持的模型类型: {self.model_type}")

    def generate_report(self, system_prompt, user_content):
        """
        生成报告，根据配置选择不同的模型来处理请求。

        :param system_prompt: 系统提示信息，包含上下文和规则。
        :param user_content: 用户提供的内容，通常是Markdown格式的文本。
        :return: 生成的报告内容。
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        # 根据选择的模型调用相应的生成报告方法
        if self.model_type == "openai":
            return self._generate_report_openai(messages)
        elif self.model_type == "ollama":
            return self._generate_report_ollama(messages)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")

    def _generate_report_openai(self, messages):
        """
        使用 OpenAI GPT 模型生成报告。

        :param messages: 包含系统提示和用户内容的消息��表。
        :return: 生成的报告内容。
        """
        LOG.info(f"使用 OpenAI {self.model_name} 模型生成报告。")
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": m["role"], "content": m["content"]} for m in messages]
            )
            LOG.debug(f"GPT 响应: {response}")
            return response.choices[0].message.content  # 返回生成的报告内容
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")
            raise

    def _generate_report_ollama(self, messages):
        """
        使用 Ollama LLaMA 模型生成报告。

        :param messages: 包含系统提示和用户内容的消息列表。
        :return: 生成的报告内容。
        """
        LOG.info(f"使用 Ollama {self.model_name} 模型生成报告。")
        try:
            payload = {
                "model": self.model_name,  # 使用配置中的Ollama模型名称
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.7,
                "stream": False
            }

            response = requests.post(self.api_url, json=payload)  # 发送POST请求到Ollama API
            response_data = response.json()

            # 调试输出查看完整的响应结构
            LOG.debug("Ollama 响应: {}", response_data)

            # 直接从响应数据中获取 content
            message_content = response_data.get("message", {}).get("content", None)
            if message_content:
                return message_content  # 返回生成的报告内容
            else:
                LOG.error("无��从响应中提取报告内容。")
                raise ValueError("Ollama API 返回的响应结构无效")
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")
            raise

if __name__ == '__main__':
    from config import Config  # 导配置管理类
    config = Config()
    llm = LLM(config)

    markdown_content="""
# Progress for langchain-ai/langchain (2024-08-20 to 2024-08-21)

## Issues Closed in the Last 1 Days
- partners/chroma: release 0.1.3 #25599
- docs: few-shot conceptual guide #25596
- docs: update examples in api ref #25589
"""

    # 示例：生成 GitHub 报告
    system_prompt = "Your specific system prompt for GitHub report generation"
    github_report = llm.generate_report(system_prompt, markdown_content)
    LOG.debug(github_report)
