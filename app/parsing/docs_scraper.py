import logging
import re

import hjson
import requests

from ..utils import db
from ..utils.notifier import notify_scrape_error, notify_new_doc

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
        notify_scrape_error(f"Docs page didn't match parsing regex")
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
        return None

    return docs


def get_doc_link(title, docs):
    docs = [x for x in docs if x.get("title") == title]
    if len(docs) != 1:
        notify_scrape_error(f"Wrong number of links for {title} found ({len(docs)})")
        return None

    doc = docs[0]
    link = doc.get("cta", {}).get("link")
    if not link:
        notify_scrape_error(f"Link not found in item for {title})")
        return None

    return link


async def scrape_docs_page():
    pending = {}
    for id, _ in docs:
        p = await db.get_pending(id)
        if p:
            pending[id] = p

    if len(pending) == len(docs):
        logging.debug("All policy docs already pending, skipping scrape")
        return

    response = requests.get(docs_page_uri)
    if response.status_code != requests.codes.ok:
        notify_scrape_error(f"Couldn't fetch WPN docs page (code {response.status_code})")
        return

    text = response.text
    objects = parse_nuxt_object(text)
    if not objects:
        return

    found = {}
    for id, title in docs:
        f = get_doc_link(title, objects)
        if f:
            found[id] = f

    if len(found) != len(docs):
        # not all links were found correctly, so we don't wanna update anything to be safe
        return

    for id, _ in docs:
        current = await db.get_redirect(id)
        if current != found[id] and pending[id] != found[id]:
            await db.set_pending(id, found[id])
            notify_new_doc(found[id], id)


if __name__ == "__main__":
    scrape_docs_page()
