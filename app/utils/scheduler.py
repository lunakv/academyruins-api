from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ..parsing.cr_scraper import scrape_rules_page
from ..parsing.docs_scraper import scrape_docs_page
import logging


class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        self.scheduler.start()
        self.scheduler.add_job(scrape_rules_page, "interval", hours=1)
        self.scheduler.add_job(scrape_docs_page, "interval", hours=1)
        logging.info("Started periodic scrape job")
