import threading
import daemon
import time
from loguru import logger
from src.config import Config
from src.github_client import GitHubClient
from src.notifier import Notifier
from src.llm import LLM
from src.report_generator import ReportGenerator
from src.subscription_manager import SubscriptionManager
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
    
    scheduler = Scheduler(
        github_client=github_client,
        notifier=notifier,
        report_generator=report_generator,
        subscription_manager=subscription_manager,
        interval=config.update_interval
    )
    
    scheduler_thread = threading.Thread(target=run_scheduler, args=(scheduler,))
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    logger.info("Scheduler thread started.")
    
    # Use python-daemon to properly daemonize the process
    with daemon.DaemonContext():
        try:
            while True:
                time.sleep(config.update_interval)
        except KeyboardInterrupt:
            logger.info("Daemon process stopped.")

if __name__ == '__main__':
    main()

# nohup python3 src/daemon_process.py > logs/daemon_process.log 2>&1 &
