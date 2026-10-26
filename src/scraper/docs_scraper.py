import json
import re
from datetime import datetime

import requests
from sqlalchemy.orm import Session

from src.db import SessionLocal
from src.link import service as links_service
from src.link.models import PendingRedirect
from src.utils.logger import logger
from src.utils.notifier import notify_new_doc, notify_scrape_error

docs_page_uri = "https://wpn.wizards.com/en/rules-documents"
# if we don't tell the WPN page we're from the US, it doesn't show the JAR for some reason.
docs_page_cookies = {"cookie-agreed": "2", "visitor_country": "country-united-states", "visitor_language": "en"}

docs = {
    "mtr": "Magic: The Gathering Tournament Rules",
    "ipg": "Magic Infraction Procedure Guide",
    "jar": "Magic: The Gathering Judging at Regular REL",
}


def scrape_docs_page():
    with SessionLocal() as session:
        with session.begin():
            do_scrape(session)


def do_scrape(session: Session):
    if not can_scrape(session):
        logger.info("Skipping broken scrape, retry moved to daily")
        return

    pending = get_currently_pending(session)
    if len(pending) == len(docs):
        logger.debug("All policy docs already pending, skipping scrape")
        return

    response = requests.get(docs_page_uri, cookies=docs_page_cookies)
    if response.status_code != requests.codes.ok:
        notify_scrape_error(f"Couldn't fetch WPN docs page (code {response.status_code})")
        logger.error(response.reason)
        set_broken(session)
        return

    found_links = get_links_from_html(response.text)
    if not found_links:
        notify_scrape_error("Unable to parse any links from WPN docs page")
        set_broken(session)
        return

    if len(found_links) == len(docs):
        unset_broken(session)
    else:
        found = set(found_links)
        not_found = set(docs).difference(found)
        notify_scrape_error(f"Not all links found in WPN docs page. Found: {found}, not_found: {not_found}")
        set_broken(session)
        # we set_broken to not get spammed with notifications, but we can still proceed with the links we found

    update_pending_links(session, pending, found_links)


# once an error is detected, retry only once per day instead of once per hour
def can_scrape(session: Session):
    link: PendingRedirect | None = session.get(PendingRedirect, "__broken__")
    if not link:
        return True
    broken_date = datetime.fromisoformat(link.link)
    return (datetime.now() - broken_date).days > 0


def set_broken(session: Session):
    links_service.set_pending_redirect(session, "__broken__", datetime.now().isoformat())


def unset_broken(session: Session):
    link: PendingRedirect | None = session.get(PendingRedirect, "__broken__")
    if link:
        session.delete(link)


def get_currently_pending(session: Session) -> dict[str, str]:
    pending = {}
    for id in docs:
        currently_pending = links_service.get_pending_redirect(session, id)
        if currently_pending:
            pending[id] = currently_pending

    return pending


def get_links_from_html(page: str) -> dict[str, str]:
    links = {}
    for id, title in docs.items():
        link = find_link(page, title)
        if link:
            links[id] = link

    return links


def find_link(page: str, title: str) -> str | None:
    # Only the first few documents are rendered as HTML. So instead of parsing HTML we look at the embedded NUXT
    # state, where each download button is serialized as a string containing the title (e.g. "CTA | Download | <title>")
    # immediately followed by the link
    string = r'(?:[^"\\]|\\.)*'  # JS string literal - anything except " or \, but with backslash escapes allowed
    pattern = re.compile(f'"{string}{re.escape(title)}{string}","(https?:{string})"')
    matches = set(pattern.findall(page))
    if len(matches) != 1:
        logger.error('Unexpected number of links found for "%s": %d', title, len(matches))
        if len(matches) > 1:
            logger.error(matches)
        return None

    # the value is a JS string literal, with slashes escaped as \u002F
    link = json.loads(f'"{matches.pop()}"')
    if not links_service.is_valid_link(link):
        logger.error('Link found for "%s" is not a valid http(s) URL: %s', title, link)
        return None
    return link


def update_pending_links(session: Session, currently_pending: dict, found_links: dict[str, str]):
    for id, found_link in found_links.items():
        live_link = links_service.get_redirect(session, id)
        pending_link = currently_pending.get(id)
        if live_link != found_link and pending_link != found_link:
            links_service.set_pending_redirect(session, id, found_link)
            notify_new_doc(found_link, id)


if __name__ == "__main__":
    scrape_docs_page()
