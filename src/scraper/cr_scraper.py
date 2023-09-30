import re

import requests
from bs4 import BeautifulSoup

from db import SessionLocal
from link import service as links_service
from utils.logger import logger
from utils.notifier import notify_new_cr, notify_scrape_error

rules_page_uri = "https://magic.wizards.com/en/rules/"


def is_txt_link(tag):
    return tag.name == "a" and tag.has_attr("href") and re.search(r".*\.txt", tag["href"])


def scrape_rules_page():
    with SessionLocal() as session:
        with session.begin():
            pending = links_service.get_pending_redirect(session, "cr")
            if pending:
                logger.debug("New CR redirect already pending, skipping scrape")
                return

            response = requests.get(rules_page_uri)
            if response.status_code != requests.codes.ok:
                notify_scrape_error(f"Couldn't fetch rules page (code {response.status_code})")
                return

            soup = BeautifulSoup(response.text, "html.parser")
            txt_links = soup.find_all(is_txt_link)
            if len(txt_links) != 1:
                notify_scrape_error(f"Wrong number of TXT links found! (expected 1, got {len(txt_links)})")
                return

            href = txt_links[0]["href"]
            href = href.replace(" ", "%20")  # the last path segment sometimes has a space (kinda hacky, but whatever)

            current = links_service.get_redirect(session, "cr")
            if href != current:
                links_service.set_pending_redirect(session, "cr", href)
                notify_new_cr(href)


if __name__ == "__main__":
    scrape_rules_page()
