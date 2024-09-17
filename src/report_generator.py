import os
from datetime import datetime, timedelta
from logger import LOG  # 导入日志模块

class ReportGenerator:
    def __init__(self, llm, report_types, github_client):
        self.llm = llm
        self.report_types = report_types
        self.prompts = {}
        self.github_client = github_client  # 添加 GitHub 客户端
        self._preload_prompts()

    def _preload_prompts(self):
        """
        预加载所有可能的提示文件，并存储在字典中。
        """
        for report_type in self.report_types + ["cybersecurity"]:  # 添加 "cybersecurity" 到预加载列表
            prompt_file = f"prompts/{report_type}_{self.llm.model_type}_prompt.txt"
            if not os.path.exists(prompt_file):
                LOG.warning(f"提示文件不存在: {prompt_file}")
                # 如果特定模型类型的提示文件不存在，尝试加载通用提示文件
                prompt_file = f"prompts/{report_type}_prompt.txt"
                if not os.path.exists(prompt_file):
                    LOG.error(f"通用提示文件也不存在: {prompt_file}")
                    raise FileNotFoundError(f"提示文件未找到: {prompt_file}")
            
            with open(prompt_file, "r", encoding='utf-8') as file:
                self.prompts[report_type] = file.read()

    def generate_github_report(self, markdown_file_path, repo):
        """
        生成 GitHub 项目的报告，如果不存在则先创建原始文件。
        """
        LOG.info(f"开始生成GitHub报告，源文件：{markdown_file_path}")
        try:
            with open(markdown_file_path, 'r', encoding='utf-8') as file:
                markdown_content = file.read()

            system_prompt = self.prompts.get("github")
            if system_prompt is None:
                LOG.error("GitHub 提示未找到")
                raise ValueError("GitHub 提示未找到")

            report = self.llm.generate_report(system_prompt, markdown_content)
            
            # 生成包含模型名称和时间戳的报告文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = self.llm.model_name.replace(" ", "_")
            report_file_name = f"github_report_{repo.replace('/', '_')}_{model_name}_{timestamp}.md"
            report_dir = os.path.join("github", "reports")
            os.makedirs(report_dir, exist_ok=True)
            report_file_path = os.path.join(report_dir, report_file_name)

            with open(report_file_path, 'w', encoding='utf-8') as report_file:
                report_file.write(report)

            LOG.info(f"GitHub报告已保存到 {report_file_path}")
            return report, report_file_path
        except Exception as e:
            LOG.error(f"生成GitHub报告时发生错误：{str(e)}")
            raise

    def _create_github_progress_file(self, repo, start_date, end_date, file_path):
        """
        创建 GitHub 进度文件并填充内容。
        """
        try:
            updates = self.github_client.fetch_updates(repo, since=start_date.isoformat(), until=end_date.isoformat())
            
            with open(file_path, 'w') as file:
                file.write(f"# Progress for {repo} ({start_date} to {end_date})\n\n")
                
                file.write("\n## Issues Closed\n")
                for issue in updates.get('issues', []):
                    file.write(f"- {issue['title']} #{issue['number']}\n")
                
                file.write("\n## Pull Requests Merged\n")
                for pr in updates.get('pull_requests', []):
                    if pr.get('merged_at'):
                        file.write(f"- {pr['title']} #{pr['number']}\n")
                
                file.write("\n## Commits\n")
                for commit in updates.get('commits', []):
                    file.write(f"- {commit['commit']['message']} ({commit['sha'][:7]})\n")
        except Exception as e:
            LOG.error(f"创建 GitHub 进度文件时发生错误：{e}")
            with open(file_path, 'w') as file:
                file.write(f"# Error: Unable to fetch updates for {repo}\n\n")
                file.write(f"An error occurred while fetching updates: {str(e)}\n")

    def generate_cybersecurity_report(self, directory_path):
        """
        生成网络安全每日汇总的报告，并保存到 cybersecurity/tech_trends/ 目录下。
        这里的输入是一个目录路径，其中包含所有以 .md 结尾的文件。
        """
        LOG.info(f"开始生成网络安全报告，源目录：{directory_path}")
        
        if not os.path.exists(directory_path):
            LOG.error(f"目录不存在：{directory_path}")
            raise FileNotFoundError(f"目录不存在：{directory_path}")

        markdown_content = self._aggregate_reports(directory_path)
        
        if not markdown_content:
            LOG.warning(f"在目录 {directory_path} 中没有找到 Markdown 文件")
            return "No content to report", None

        system_prompt = self.prompts.get("cybersecurity")
        if system_prompt is None:
            LOG.error("Cybersecurity 提示未找到")
            raise ValueError("Cybersecurity 提示未找到")

        report = self.llm.generate_report(system_prompt, markdown_content)
        
        # 生成包含模型名称和时间戳的报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = self.llm.model_name.replace(" ", "_")
        report_file_name = f"cybersecurity_report_{model_name}_{timestamp}.md"
        report_dir = os.path.join("cybersecurity", "tech_trends")
        os.makedirs(report_dir, exist_ok=True)
        report_file_path = os.path.join(report_dir, report_file_name)

        with open(report_file_path, 'w+', encoding='utf-8') as report_file:
            report_file.write(report)

        LOG.info(f"网络安全报告已保存到 {report_file_path}")
        return report, report_file_path

    def _aggregate_reports(self, directory_path):
        """
        聚合目录下所有以 '.md' 结尾的 Markdown 文件内容，生成每日汇总报告的输入。
        """
        markdown_content = ""
        for filename in os.listdir(directory_path):
            if filename.endswith(".md"):
                file_path = os.path.join(directory_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    markdown_content += file.read() + "\n\n"
        return markdown_content

if __name__ == '__main__':
    from config import Config  # 导入配置管理类
    from llm import LLM

    config = Config()
    llm = LLM(config)
    report_generator = ReportGenerator(llm, config.report_types, config.github_client)

    # 手动设置目录路径
    directory_path = "/home/lmroot/AI/lesson0828/GitHubSentinel/src/freebuf_news/"

    # 生成网络安全每日汇总报告
    report, report_file_path = report_generator.generate_cybersecurity_report(directory_path)
    LOG.debug(report)