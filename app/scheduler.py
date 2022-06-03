from apscheduler.schedulers.background import BackgroundScheduler
from cr_scraper import scrape_rules_page
import logging


class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def start(self):
        self.scheduler.start()
        self.scheduler.add_job(scrape_rules_page, 'interval', hours=1)
        logging.info('Started periodic scrape job')

