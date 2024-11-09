import shlex

from src.config import Config
from src.github_client import GitHubClient
from src.notifier import Notifier
from src.llm import LLM
from src.report_generator import ReportGenerator
from src.subscription_manager import SubscriptionManager
from src.command_handler import CommandHandler
from src.logger import LOG

def main():
    config = Config()
    github_client = GitHubClient(config.github_token)
    notifier = Notifier(config.notification_settings)
    llm = LLM()
    report_generator = ReportGenerator(llm)
    subscription_manager = SubscriptionManager(config.subscriptions_file)
    command_handler = CommandHandler(github_client, subscription_manager, report_generator)
    
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
