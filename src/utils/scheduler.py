import asyncio
from datetime import timedelta
from typing import Callable

from src.scraper.cr_scraper import scrape_rules_page
from src.scraper.docs_scraper import scrape_docs_page
from src.utils.backup import run_backup
from src.utils.logger import logger

jobs: list[tuple[Callable[[], None], timedelta]] = [
    (scrape_rules_page, timedelta(hours=1)),
    (scrape_docs_page, timedelta(hours=1)),
    (run_backup, timedelta(days=1)),
]


async def run_periodically(job: Callable[[], None], interval: timedelta):
    while True:
        try:
            # jobs are blocking (requests, SQLAlchemy, boto3), so they run in a worker thread
            await asyncio.to_thread(job)
        except Exception:
            logger.exception(f"Periodic job {job.__name__} failed")
        await asyncio.sleep(interval.total_seconds())


def start_periodic_jobs() -> list[asyncio.Task]:
    tasks = [asyncio.create_task(run_periodically(job, interval)) for job, interval in jobs]
    logger.info("Started periodic jobs")
    return tasks
