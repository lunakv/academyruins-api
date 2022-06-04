import os
import json
from . import static_paths as paths
from pathlib import Path
from ..parsing import cr_scraper, refresh_cr
from ..resources.cache import RedirectCache
import logging


def seed_dir(path):
    if not Path(path).is_dir():
        logging.info(f'Creating directory {path}...')
        os.makedirs(path)


def seed_file(path, content):
    if not Path(path).is_file():
        logging.info(f'Creating file {path}...')
        with open(path, 'w') as file:
            json.dump(content, file)


def seed():
    logging.info('Seeding necessary files...')
    seed_dir(paths.__dir)
    seed_dir(paths.cr_dir)
    if not Path(paths.rules_dict).is_file():
        logging.error('Rules file not found, performing initial scrape.')
        logging.debug('Scraping rules page.')
        cr_scraper.scrape_rules_page()
        logging.debug('Updating CR redirect.')
        RedirectCache().update_from_pending('cr')
        logging.debug('Parsing new CR.')
        refresh_cr.refresh_cr()
        logging.error('Rules file initialization complete')
    logging.info('Files seeded.')


if __name__ == '__main__':
    seed()
