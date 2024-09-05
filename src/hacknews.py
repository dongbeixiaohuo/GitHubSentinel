import requests
from bs4 import BeautifulSoup
from logger import LOG  # 导入日志记录器
from notifier import Notifier  # 导入通知器类
from report_generator import ReportGenerator
import os
import datetime
import logging
from llm import LLM  # 从 llm.py 导入 ReportGenerator

def fetch_hackernews_top_stories():
    url = 'https://news.ycombinator.com/'
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功

    soup = BeautifulSoup(response.text, 'html.parser')
    stories = soup.find_all('tr', class_='athing')  # 找到所有新闻条目

    top_stories = []
    for story in stories:
        title_tag = story.find('span', class_='titleline').find('a')
        if title_tag:
            title = title_tag.text
            link = title_tag['href']
            top_stories.append({'title': title, 'link': link})

    print(f"爬取到的新闻数量: {len(top_stories)}")  # 打印爬取到的新闻数量
    return top_stories

def hackernews_job(notifier, report_generator):
    try:
        logging.info("[开始执行Hacker News定时任务]")
        
        top_stories = fetch_hackernews_top_stories()
        logging.info(f"成功爬取 {len(top_stories)} 条新闻")
        
        save_directory = "hackernews_reports"
        markdown_file_path = save_stories_to_markdown(top_stories, save_directory)
        logging.info(f"新闻已保存到: {markdown_file_path}")
        
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        processed_report = report_generator.generate_hackernews_report(markdown_content)
        logging.info("Hacker News 日报生成成功")
        
        subject = "Hacker News 日报生成成功"
        notifier.send_email(subject, processed_report)
        logging.info("通知邮件发送成功")
        
        return processed_report, markdown_file_path
    except Exception as e:
        logging.error(f"Hacker News 任务执行失败: {e}")
        return None  # 在失败的情况下返回 None

def save_stories_to_markdown(stories, save_directory):
    # 确保保存目录存在
    os.makedirs(save_directory, exist_ok=True)

    # 获取当前日期并格式化为 YYYYMMDD
    current_date = datetime.datetime.now().strftime("%Y%m%d")

    # 生成Markdown文件的路径，文件名为 hackernews_YYYYMMDD.md
    markdown_file_path = os.path.join(save_directory, f"hackernews_{current_date}.md")

    # 写入Markdown文件
    with open(markdown_file_path, 'w', encoding='utf-8') as file:
        file.write("# Hacker News Top Stories\n\n")
        for idx, story in enumerate(stories, start=1):
            file.write(f"## {idx}. {story['title']}\n")
            file.write(f"[Link]({story['link']})\n\n")

    print(f"新闻已保存到: {markdown_file_path}")
    return markdown_file_path

