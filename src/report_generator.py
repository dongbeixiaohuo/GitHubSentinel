# src/report_generator.py

import os
from datetime import date, timedelta
from logger import LOG  # 导入日志模块，用于记录日志信息

class ReportGenerator:
    def __init__(self, llm):
        self.llm = llm  # 初始化时接受一个LLM实例，用于后续生成报告

    def generate_daily_report(self, markdown_file_path):
        # 读取Markdown文件并使用LLM生成日报
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        report = self.llm.generate_daily_report(markdown_content)  # 调用LLM生成报告

        report_file_path = os.path.splitext(markdown_file_path)[0] + "_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)  # 写入生成的报告

        LOG.info(f"GitHub 项目报告已保存到 {report_file_path}")

        return report, report_file_path


    def generate_report_by_date_range(self, markdown_file_path, days):
        # 生成特定日期范围的报告，流程与日报生成类似
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        report = self.llm.generate_daily_report(markdown_content)

        report_file_path = os.path.splitext(markdown_file_path)[0] + f"_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)
        
        LOG.info(f"GitHub 项目报告已保存到 {report_file_path}")

        return report, report_file_path


    def generate_hackernews_report(self, markdown_content):
        # 使用 LLM 处理 Markdown 内容，生成 Hacker News 报告
        report = self.llm.generate_hackernews_report(markdown_content)
        
        # 确保返回的是字符串
        if not isinstance(report, str):
            raise ValueError("生成的报告不是字符串类型")
        
        return report

def generate_daily_report_from_markdown(self, markdown_file_path):
    # 读取Markdown文件并使用LLM生成日报
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    report = self.llm.generate_daily_report(markdown_content)  # 调用LLM生成报告

    # 打印生成的报告内容
    print(f"生成的日报内容:\n{report}")

    # 生成日报的文件路径
    report_file_path = os.path.splitext(markdown_file_path)[0] + "_daily_report.md"
    
    # 将生成的日报写入新的Markdown文件
    with open(report_file_path, 'w+', encoding='utf-8') as report_file:
        report_file.write(report)  # 写入生成的报告

    LOG.info(f"日报已保存到 {report_file_path}")
    print(f"日报已保存到: {report_file_path}")

    return report, report_file_path

def get_latest_markdown_file(directory):
    # 获取目录中所有的Markdown文件
    markdown_files = [f for f in os.listdir(directory) if f.endswith('.md')]
    
    if not markdown_files:
        raise FileNotFoundError(f"No Markdown files found in directory: {directory}")

    # 按照文件的修改时间排序，获取最新的文件
    markdown_files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    
    latest_file = markdown_files[0]
    latest_file_path = os.path.join(directory, latest_file)
    
    print(f"最新的Markdown文件: {latest_file_path}")
    return latest_file_path



