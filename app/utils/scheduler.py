from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .backup import run_backup
from .logger import logger
from ..parsing.cr_scraper import scrape_rules_page
from ..parsing.docs_scraper import scrape_docs_page


class Scheduler:
    def __init__(self):
        job_store = SQLAlchemyJobStore(url="sqlite:///app/resources/generated/jobs.sqlite")
        self.scheduler = AsyncIOScheduler(jobstores={"default": job_store})

    def start(self):
        self.scheduler.start()
        self.scheduler.add_job(scrape_rules_page, "interval", hours=1, coalesce=True)
        self.scheduler.add_job(scrape_docs_page, "interval", hours=1, coalesce=True)
        self.scheduler.add_job(run_backup, "interval", weeks=2, coalesce=True)
        logger.info("Started periodic scrape job")
