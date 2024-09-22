# src/command_handler.py

import argparse

import argparse  # 导入argparse库，用于处理命令行参数解析

from hacknews import hackernews_job
from logger import LOG

class CommandHandler:
    def __init__(self, github_client, subscription_manager, report_generator, notifier):
        # 初始化CommandHandler，接收GitHub客户端、订阅管理器和报告生成器
        self.github_client = github_client
        self.subscription_manager = subscription_manager
        self.report_generator = report_generator
        self.notifier = notifier
        self.parser = argparse.ArgumentParser(description="GitHub Sentinel CLI")
        self.subparsers = self.parser.add_subparsers(dest="command")

        # 现有的命令注册...

        # 添加订阅命令
        parser_add = self.subparsers.add_parser('add', help='Add a subscription')
        parser_add.add_argument('repo', type=str, help='The repository to subscribe to (e.g., owner/repo)')
        parser_add.set_defaults(func=self.add_subscription)

        # 删除订阅命令
        parser_remove = self.subparsers.add_parser('remove', help='Remove a subscription')
        parser_remove.add_argument('repo', type=str, help='The repository to unsubscribe from (e.g., owner/repo)')
        parser_remove.set_defaults(func=self.remove_subscription)

        # 列出所有订阅命令
        parser_list = self.subparsers.add_parser('list', help='List all subscriptions')
        parser_list.set_defaults(func=self.list_subscriptions)

        # 导出每日进展命令
        parser_export = self.subparsers.add_parser('export', help='Export daily progress')
        parser_export.add_argument('repo', type=str, help='The repository to export progress from (e.g., owner/repo)')
        parser_export.set_defaults(func=self.export_daily_progress)

        # 导出特定日期范围进展命令
        parser_export_range = self.subparsers.add_parser('export-range', help='Export progress over a range of dates')
        parser_export_range.add_argument('repo', type=str, help='The repository to export progress from (e.g., owner/repo)')
        parser_export_range.add_argument('days', type=int, help='The number of days to export progress for')
        parser_export_range.set_defaults(func=self.export_progress_by_date_range)

        # 生成日报命令
        parser_generate = self.subparsers.add_parser('generate', help='Generate daily report from markdown file')
        parser_generate.add_argument('file', type=str, help='The markdown file to generate report from')
        parser_generate.set_defaults(func=self.generate_daily_report)

        # 帮助命令
        parser_help = self.subparsers.add_parser('help', help='Show help message')
        parser_help.set_defaults(func=self.print_help)

        # 添加 Hacker News 报告命令
        hackernews_parser = self.subparsers.add_parser("hackernews", help="Generate Hacker News report")
        hackernews_parser.set_defaults(func=self.generate_hackernews_report)

    # 下面是各种命令对应的方法实现，每个方法都使用了相应的管理器来执行实际操作，并输出结果信息
    def add_subscription(self, args):
        self.subscription_manager.add_subscription(args.repo)
        print(f"Added subscription for repository: {args.repo}")

    def remove_subscription(self, args):
        self.subscription_manager.remove_subscription(args.repo)
        print(f"Removed subscription for repository: {args.repo}")

    def list_subscriptions(self, args):
        subscriptions = self.subscription_manager.list_subscriptions()
        print("Current subscriptions:")
        for sub in subscriptions:
            print(f"  - {sub}")

    def export_daily_progress(self, args):
        self.github_client.export_daily_progress(args.repo)
        print(f"Exported daily progress for repository: {args.repo}")

    def export_progress_by_date_range(self, args):
        self.github_client.export_progress_by_date_range(args.repo, days=args.days)
        print(f"Exported progress for the last {args.days} days for repository: {args.repo}")

    def generate_daily_report(self, args):
        self.report_generator.generate_daily_report(args.file)
        print(f"Generated daily report from file: {args.file}")

    def generate_hackernews_report(self, args):
        try:
            LOG.info("开始生成 Hacker News 报告")
            result = hackernews_job(self.notifier, self.report_generator)
            
            if result is None:
                print("生成 Hacker News 报告失败")
                return

            if isinstance(result, tuple) and len(result) == 2:
                report, file_path = result
                print("Hacker News 报告生成成功")
                if file_path:
                    print(f"报告已保存到: {file_path}")
                if report:
                    print("\n报告内容:")
                    print(report)
            else:
                print("Hacker News 报告生成成功，但返回格式不符合预期")
                print("结果:", result)

        except Exception as e:
            LOG.error(f"生成 Hacker News 报告时发生错误: {e}")
            print(f"生成报告时发生错误: {e}")

    def print_help(self, args=None):
        self.parser.print_help()  # 输出帮助信息
