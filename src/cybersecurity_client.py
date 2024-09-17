import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from logger import LOG

class CybersecurityClient:
    def __init__(self):
        self.urls = [
            'https://www.freebuf.com/articles/es',
            'https://www.freebuf.com/vuls',
            'https://www.freebuf.com/articles/network',
            'https://www.freebuf.com/articles/neopoints'
        ]

    def fetch_top_stories(self):
        LOG.info("准备获取FreeBuf的企业安全热门新闻。")
        all_stories = []
        for url in self.urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                all_stories.extend(self.parse_stories(response.text, url))
            except Exception as e:
                LOG.error(f"获取FreeBuf的企业安全热门新闻失败：{str(e)}")
        
        # 按时间顺序排序，最近的在前面，并只取前十名
        all_stories.sort(key=lambda x: x['time'] if x['time'] else datetime.min, reverse=True)
        top_stories = all_stories[:10]
        
        # 提取标题和前三段文字
        for story in top_stories:
            story.update(self.fetch_article_details(story['link']))
        
        return top_stories

    def parse_stories(self, html_content, url):
        LOG.debug("解析FreeBuf的HTML内容。")
        soup = BeautifulSoup(html_content, 'html.parser')
        story_containers = soup.find_all('p', class_='bottom-right', attrs={"data-v-4c98f879": True})  # 查找所有包含新闻的<p>标签
        
        LOG.debug(f"找到 {len(story_containers)} 个 <p> 标签。")
        
        stories = []
        for container in story_containers:
            # 查找 <a> 标签
            story = container.find('a', href=True, target="_blank", attrs={"data-v-4c98f879": True})
            if not story:
                LOG.debug("未找到 <a> 标签，跳过。")
                continue
            
            # 只解析特定类型的 <a> 标签
            if any(story['href'].startswith(prefix) for prefix in ['/articles/es/', '/vuls/', '/articles/network/', '/articles/neopoints/']):
                link = story['href']
                if not link.startswith('http'):
                    link = 'https://www.freebuf.com' + link  # 补全相对链接
                
                # 提取文章时间
                time_tag = container.find('span', style="margin-left:30px;margin-right:4px", attrs={"data-v-4c98f879": True})
                if time_tag:
                    article_time = time_tag.text.strip()
                    LOG.debug(f"找到时间标签：{article_time}")
                    try:
                        article_time = datetime.strptime(article_time, '%Y-%m-%d')
                    except ValueError:
                        LOG.debug(f"时间格式错误：{article_time}")
                        article_time = None
                else:
                    LOG.debug("未找到时间标签")
                    article_time = None
                
                stories.append({'link': link, 'time': article_time})
                LOG.debug(f"添加新闻链接：{link} - {article_time}")
        
        return stories

    def fetch_article_details(self, link):
        try:
            response = requests.get(link, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title_tag = soup.find('span', class_='title-span', attrs={"data-v-7868286e": True})
            title = title_tag.text.strip() if title_tag else '未知标题'
            LOG.debug(f"提取到的标题：{title}")
            
            # 提取正文前三段文字
            content_div = soup.find('div', class_='artical-body', attrs={"data-v-7868286e": True})
            if content_div:
                paragraphs = content_div.find_all('p')
                LOG.debug(f"找到 {len(paragraphs)} 个段落")
                # 过滤掉包含 <img> 标签或 align="center" 属性的段落
                filtered_paragraphs = [p for p in paragraphs if not p.find('img') and p.get('align') != 'center']
                content = "\n\n".join(p.text.strip() for p in filtered_paragraphs[:3])  # 获取前三段文字
            else:
                LOG.debug("未找到文章内容的 <div> 标签")
                content = "获取文章内容失败"
            
            return {'title': title, 'content': content}
        except Exception as e:
            LOG.error(f"获取文章详情失败：{str(e)}")
            return {'title': '获取标题失败', 'content': '获取文章内容失败'}

    def fetch_latest_news(self, directory_path):
        LOG.info(f"开始获取最新网络安全新闻，保存到目录：{directory_path}")
        try:
            response = requests.get(self.base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('div', class_='article-item')  # 根据实际网页结构调整

            for i, article in enumerate(articles[:10]):  # 获取前10篇文章
                title = article.find('h3').text.strip()
                link = self.base_url + article.find('a')['href']
                summary = article.find('p', class_='summary').text.strip()

                file_name = f"article_{i+1}.md"
                file_path = os.path.join(directory_path, file_name)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {title}\n\n")
                    f.write(f"链接：{link}\n\n")
                    f.write(f"摘要：{summary}\n")

            LOG.info(f"成功获取并保存了 {len(articles)} 篇文章")
        except Exception as e:
            LOG.error(f"获取网络安全新闻时发生错误：{str(e)}")

    def export_top_stories(self, date=None, hour=None):
        LOG.debug("准备导出FreeBuf的企业安全热门新闻。")
        top_stories = self.fetch_top_stories()  # 获取新闻数据
        
        if not top_stories:
            LOG.warning("未找到任何FreeBuf的企业安全新闻。")
            return None
        
        # 如果未提供 date 和 hour 参数，使用当前日期和时间
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if hour is None:
            hour = datetime.now().strftime('%H')

        # 构建存储路径
        dir_path = os.path.join('freebuf_news', date)
        os.makedirs(dir_path, exist_ok=True)  # 确保目录存在
        LOG.debug(f"目录路径：{dir_path}")
        
        file_path = os.path.join(dir_path, f'{hour}.md')  # 定义文件路径
        LOG.debug(f"文件路径：{file_path}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(f"# FreeBuf 企业安全热门新闻 ({date} {hour}:00)\n\n")
                for idx, story in enumerate(top_stories, start=1):
                    time_str = story['time'].strftime('%Y-%m-%d') if story['time'] else '未知时间'
                    file.write(f"{idx}. [{story['title']}]({story['link']}) - {time_str}\n\n")
                    file.write(f"{story['content']}\n\n")
            LOG.info(f"FreeBuf企业安全热门新闻文件生成：{file_path}")
        except Exception as e:
            LOG.error(f"写入文件时发生错误：{e}")
        
        return file_path


if __name__ == "__main__":
    client = CybersecurityClient()
    client.export_top_stories()  # 默认情况下使用当前日期和时间