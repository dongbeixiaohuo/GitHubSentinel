import os
from datetime import date, timedelta
from logger import LOG  # 导入日志模块，用于记录日志信息

class ReportGenerator:
    def __init__(self, llm):
        self.llm = llm  # 初始化时接受一个LLM实例，用于后续生成报告

    def _generate_report(self, markdown_file_path, generate_func, report_type="报告"):
        try:
            if not os.path.exists(markdown_file_path):
                raise FileNotFoundError(f"文件路径不存在: {markdown_file_path}")
            
            LOG.info(f"开始生成 {report_type}，读取文件：{markdown_file_path}")
            with open(markdown_file_path, 'r', encoding='utf-8') as file:
                markdown_content = file.read()

            LOG.info(f"调用语言模型生成 {report_type}")
            report = generate_func(markdown_content)  # 调用传入的生成函数

            report_file_path = os.path.splitext(markdown_file_path)[0] + "_report.md"
            with open(report_file_path, 'w+', encoding='utf-8') as report_file:
                report_file.write(report)  # 写入生成的报告

            LOG.info(f"{report_type} 已保存到 {report_file_path}")
            return report, report_file_path
        except Exception as e:
            LOG.error(f"生成 {report_type} 时发生错误: {e}")
            return None, None

    def generate_daily_report(self, markdown_file_path):
        return self._generate_report(markdown_file_path, self.llm.generate_daily_report, "每日报告")

    def generate_report_by_date_range(self, markdown_file_path, days):
        return self._generate_report(markdown_file_path, self.llm.generate_daily_report, f"{days}天范围报告")

    def generate_hackernews_report(self, markdown_content):
        try:
            LOG.info("开始生成 Hacker News 报告")
            report = self.llm.generate_hackernews_report(markdown_content)
            if not isinstance(report, str):
                raise ValueError("生成的报告不是字符串类型")
            LOG.info("Hacker News 报告生成成功")
            return report
        except Exception as e:
            LOG.error(f"生成 Hacker News 报告时发生错误: {e}")
            return None

    def generate_daily_report_from_markdown(self, markdown_file_path):
        return self._generate_report(markdown_file_path, self.llm.generate_daily_report, "每日报告")

    def get_latest_markdown_file(self, directory):
        try:
            LOG.info(f"获取目录中最新的Markdown文件：{directory}")
            if not os.path.exists(directory):
                raise FileNotFoundError(f"目录不存在: {directory}")

            markdown_files = [f for f in os.listdir(directory) if f.endswith('.md')]
            if not markdown_files:
                raise FileNotFoundError(f"No Markdown files found in directory: {directory}")

            markdown_files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
            latest_file = markdown_files[0]
            latest_file_path = os.path.join(directory, latest_file)
            
            LOG.info(f"最新的Markdown文件: {latest_file_path}")
            return latest_file_path
        except Exception as e:
            LOG.error(f"获取最新Markdown文件时发生错误: {e}")
            return None