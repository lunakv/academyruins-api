from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.scraper.cr_scraper import scrape_rules_page
from src.scraper.docs_scraper import scrape_docs_page
from src.utils.backup import run_backup
from src.utils.logger import logger


class Scheduler:
    def __init__(self):
        job_store = MemoryJobStore()
        self.scheduler = AsyncIOScheduler(jobstores={"default": job_store})

    def start(self):
        self.scheduler.start()
        self.scheduler.add_job(scrape_rules_page, "interval", hours=1, coalesce=True)
        self.scheduler.add_job(scrape_docs_page, "interval", hours=1, coalesce=True)
        self.scheduler.add_job(run_backup, "interval", weeks=2, coalesce=True)
        logger.info("Started periodic scrape job")
