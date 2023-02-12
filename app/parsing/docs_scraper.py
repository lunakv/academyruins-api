import re
from datetime import datetime

import hjson
import requests
from sqlalchemy.orm import Session

from app.database import operations as ops
from app.database.db import SessionLocal
from app.database.models import PendingRedirect
from app.utils.logger import logger

from ..utils.notifier import notify_new_doc, notify_scrape_error

docs_page_uri = "https://wpn.wizards.com/en/rules-documents/"

docs = [
    ("mtr", "Magic: The Gathering Tournament Rules"),
    ("ipg", "Magic Infraction Procedure Guide"),
    ("jar", "Magic: The Gathering Judging at Regular REL"),
]


# So... this probably needs an explanation
# Here I am parsing the WPN documents page. However, unlike the Rules page, this site doesn't have the common decency
# to render all the links directly in HTML. Instead, it's a Vue site that renders only a couple and requires a button
# click to load more of them. An automated Python scraper has a hard time clicking buttons, so I had to get the data
# from someplace else. The site uses Nuxt for state management, so all the data I need is actually included in a
# window.__NUXT__ property. Parsing that property proves to be a challenge though, because
# a) it's loaded as an IIFE, which means the result includes function parameters and whatnot,
# b) the return value isn't JSON, but a JS object literal, which doesn't have quoted keys (among other niceties)
# I could use selenium to render the page, but I really didn't feel like spinning up a webdriver instance just for this.
# Instead, I first use regex to get the return value of the function (luckily it's just a return instruction),
# then do some hacky pre-processing and throw it into a HJSON parser (which is a superset of JSON).
# This works, but is *very* brittle, so at even the slightest issue we just abort and send a notification
def parse_nuxt_object(page):
    match = re.search(r"window\.__NUXT__=\(function\(([^)]*)\)\{return (.*?)}\(", page)
    if not match:
        notify_scrape_error("Docs page didn't match parsing regex")
        return None

    params = match.group(1).split(",")
    obj = match.group(2)

    # replace function parameters (key:a) with null values (key:null) to make this parseable
    for param in params:
        # some values have a trailing $ at the end for some reason (key:a$)
        obj = re.sub(":" + param + r"\b\$?", ":null", obj)

    # similarly, some values are just $, which breaks the parser
    obj = obj.replace(":$,", ":null,")

    try:
        parsed = hjson.loads(obj)
    except hjson.HjsonDecodeError as ex:
        notify_scrape_error("Failed hjson parsing of docs page object" + "\n" + ex.msg + f"({ex.pos})")
        return None

    docs = parsed.get("fetch", {}).get("DocumentationDownload:0", {}).get("documents")
    if not docs:
        notify_scrape_error("List of policy documents not found in parsed NUXT object")
        logger.error("List of policy documents not found in parsed NUXT object")
        logger.error(parsed)
        return None

    return docs


def get_doc_link(title, objects):
    objects = [x for x in objects if x.get("title") == title]
    if len(objects) != 1:
        notify_scrape_error(f"Wrong number of links for {title} found ({len(objects)})")
        return None

    doc = objects[0]
    link = doc.get("cta", {}).get("link")
    if not link:
        notify_scrape_error(f"Link not found in item for {title})")
        return None

    return link


async def set_broken(session: Session):
    ops.set_pending(session, "__broken__", datetime.now().isoformat())


# once an error is detected, retry only once per day instead of once per hour
async def can_scrape(session: Session):
    link: PendingRedirect | None = session.get(PendingRedirect, "__broken__")
    if not link:
        return True
    broken_date = datetime.fromisoformat(link.link)
    return (datetime.now() - broken_date).days > 0


async def scrape_docs_page():
    with SessionLocal() as session:
        with session.begin():
            if not (await can_scrape(session)):
                logger.info("Skipping broken scrape, retry moved to daily")
                return

            pending = {}
            for id, _ in docs:
                p = ops.get_pending_redirect(session, id)
                if p:
                    pending[id] = p

            if len(pending) == len(docs):
                logger.debug("All policy docs already pending, skipping scrape")
                return

            response = requests.get(docs_page_uri)
            if response.status_code != requests.codes.ok:
                notify_scrape_error(f"Couldn't fetch WPN docs page (code {response.status_code})")
                logger.error("Couldn't fetch WPN docs page: %s", response.reason)
                await set_broken(session)
                return

            text = response.text
            objects = parse_nuxt_object(text)
            if not objects:
                await set_broken(session)
                return

            found = {}
            for id, title in docs:
                f = get_doc_link(title, objects)
                if f:
                    found[id] = f

            if len(found) != len(docs):
                # not all links were found correctly, so we don't wanna update anything to be safe
                notify_scrape_error("Couldn't find links for all WPN documents")
                logger.error("Couldn't find links for all WPN documents")
                logger.error(found)
                await set_broken(session)
                return

            for id, _ in docs:
                current = ops.get_redirect(session, id)
                if current != found[id] and (id not in pending or pending[id] != found[id]):
                    ops.set_pending(session, id, found[id])
                    notify_new_doc(found[id], id)


if __name__ == "__main__":
    scrape_docs_page()
