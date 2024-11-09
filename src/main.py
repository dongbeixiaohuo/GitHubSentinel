# src/main.py

import sys
import argparse
from loguru import logger
import os
from datetime import datetime

from src.config import Config
from src.github_client import GitHubClient
from src.notifier import Notifier
from src.report_generator import ReportGenerator
from src.scheduler import Scheduler

def run_scheduler(scheduler):
    scheduler.start()

def main():
    config = Config()
    github_client = GitHubClient(config.github_token)
    notifier = Notifier(config.notification_settings)
    llm = LLM()
    report_generator = ReportGenerator(llm)
    subscription_manager = SubscriptionManager(config.subscriptions_file)
    command_handler = CommandHandler(github_client, subscription_manager, report_generator)
    
    scheduler = Scheduler(
        github_client=github_client,
        notifier=notifier,
        report_generator=report_generator,
        subscription_manager=subscription_manager,
        interval=config.update_interval
    )
    
    scheduler_thread = threading.Thread(target=run_scheduler, args=(scheduler,))
    scheduler_thread.daemon = True
    # scheduler_thread.start()

    parser = command_handler.parser
    command_handler.print_help()

    while True:
        try:
            user_input = input("GitHub Sentinel> ")
            if user_input in ['exit', 'quit']:
                break
            try:
                args = parser.parse_args(shlex.split(user_input))
                if args.command is None:
                    continue
                args.func(args)
            except SystemExit as e:
                LOG.error("Invalid command. Type 'help' to see the list of available commands.")
        except Exception as e:
            LOG.error(f"Unexpected error: {e}")

if __name__ == '__main__':
    main()
