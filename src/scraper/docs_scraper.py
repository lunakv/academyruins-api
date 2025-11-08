from datetime import datetime

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from src.db import SessionLocal
from src.link import service as links_service
from src.link.models import PendingRedirect
from src.utils.logger import logger
from src.utils.notifier import notify_new_doc, notify_scrape_error

docs_page_uri = "https://wpn.wizards.com/en/rules-documents"

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

    response = requests.get(docs_page_uri)
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
    soup = BeautifulSoup(page, "html.parser")
    links = {}
    for id, title in docs.items():
        link = find_link(soup, title)
        if link:
            links[id] = link

    return links


def find_link(soup: BeautifulSoup, title: str) -> str | None:
    # If a tag has one child, it inherits its .string. Checking for None.contents means we only find the bottommost tags
    title_elements = soup.find_all(lambda tag: tag.string == title and tag.contents[0].name is None)
    if len(title_elements) != 1:
        logger.error('Unexpected number of tags with title "%s" found: %d', title, len(title_elements))
        return None

    # go up the tree from the title until you find the 'div' that contains the download link
    link_parent = title_elements[0]
    anchors = link_parent.find_all("a")
    while link_parent and not anchors:
        link_parent = link_parent.parent
        anchors = link_parent.find_all("a")

    if len(anchors) != 1:
        logger.error('Unexpected number of links found for "%s": %d', title, len(anchors))
        if len(anchors) > 1:
            logger.error(anchors)
        return None

    return anchors[0]["href"]


def update_pending_links(session: Session, currently_pending: dict, found_links: dict[str, str]):
    for id, found_link in found_links.items():
        live_link = links_service.get_redirect(session, id)
        pending_link = currently_pending.get(id)
        if live_link != found_link and pending_link != found_link:
            links_service.set_pending_redirect(session, id, found_link)
            notify_new_doc(found_link, id)


if __name__ == "__main__":
    scrape_docs_page()
