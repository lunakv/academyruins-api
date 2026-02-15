"""
Bootstrap the database from scratch with zero human intervention.

Downloads the current CR, MTR, and IPG from WotC, parses them,
and inserts the initial rows directly (bypassing the pending/confirm flow
since there's no previous version to diff against).
"""

import datetime
import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select

from src.cr.models import Cr
from src.db import SessionLocal
from src.extractor.cr import extract_cr
from src.extractor.cr.refresh_cr import download_cr, get_response_text
from src.extractor.download_doc import download_doc
from src.ipg.models import Ipg
from src.link.models import Redirect
from src.mtr.models import Mtr
from src.resources import static_paths as paths
from src.resources.cache import GlossaryCache, KeywordCache
from src.resources.seeder import seed
from src.scraper.cr_scraper import is_txt_link, rules_page_uri
from src.scraper.docs_scraper import docs_page_uri, get_links_from_html
from src.utils.logger import logger


def _scrape_cr_link() -> str | None:
    """Scrape the current CR .txt link from WotC's rules page."""
    response = requests.get(rules_page_uri)
    if not response.ok:
        logger.error(f"Couldn't fetch rules page (code {response.status_code})")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    txt_links = soup.find_all(is_txt_link)
    if len(txt_links) != 1:
        logger.error(f"Wrong number of TXT links found (expected 1, got {len(txt_links)})")
        return None

    href = txt_links[0]["href"]
    return href.replace(" ", "%20")


def _scrape_doc_links() -> dict[str, str]:
    """Scrape current MTR/IPG/JAR links from WPN docs page."""
    response = requests.get(docs_page_uri)
    if not response.ok:
        logger.error(f"Couldn't fetch WPN docs page (code {response.status_code})")
        return {}

    return get_links_from_html(response.text)


def _seed_redirect(db, resource: str, link: str):
    """Insert a redirect directly into the active table."""
    existing = db.get(Redirect, resource)
    if existing:
        existing.link = link
    else:
        db.add(Redirect(resource=resource, link=link))


def _bootstrap_cr(db, cr_link: str) -> bool:
    """Download, parse, and insert the first CR directly."""
    result = download_cr(cr_link)
    if result is None:
        logger.error("Failed to download CR")
        return False

    text, file_name = result
    parsed = extract_cr.extract(text)

    cr = Cr(
        creation_day=datetime.date.today(),
        set_code="SEED",
        set_name="Bootstrap Seed",
        data=parsed["rules"],
        toc=[s.model_dump() for s in parsed["toc"]],
        file_name=file_name,
    )
    db.add(cr)

    # Write cache files
    KeywordCache().replace(parsed["keywords"])
    GlossaryCache().replace(parsed["glossary"])

    logger.info("Bootstrapped CR successfully")
    return True


def _bootstrap_mtr(db, mtr_link: str) -> bool:
    """Download, parse, and insert the first MTR directly."""
    if os.environ.get("USE_TIKA") != "1":
        logger.warning("Tika not enabled (USE_TIKA != 1), skipping MTR bootstrap")
        return False

    from src.extractor.mtr.extract_mtr import extract

    directory, file_name = download_doc(mtr_link, "mtr")
    file_path = Path(directory) / file_name
    result = extract(file_path)
    if result is None:
        logger.error("Failed to extract MTR")
        return False

    effective_date, sections = result
    mtr = Mtr(
        file_name=file_name,
        creation_day=datetime.date.today(),
        effective_date=effective_date,
        sections=sections,
    )
    db.add(mtr)

    logger.info("Bootstrapped MTR successfully")
    return True


def _bootstrap_ipg(db, ipg_link: str) -> bool:
    """Download and insert the first IPG."""
    _, file_name = download_doc(ipg_link, "ipg")
    db.add(Ipg(creation_day=datetime.date.today(), file_name=file_name))

    logger.info("Bootstrapped IPG successfully")
    return True


def bootstrap():
    """
    Bootstrap the database from scratch.

    Idempotent: if the CR table already has data, exits early.
    """
    seed()

    with SessionLocal() as db:
        with db.begin():
            existing = db.execute(select(Cr).limit(1)).scalar_one_or_none()
            if existing:
                logger.info("Database already has CR data, skipping bootstrap")
                return

    logger.info("Starting bootstrap — scraping current document links...")

    cr_link = _scrape_cr_link()
    if not cr_link:
        logger.error("Could not find CR link, aborting bootstrap")
        return

    doc_links = _scrape_doc_links()

    with SessionLocal() as db:
        with db.begin():
            # Seed redirects
            _seed_redirect(db, "cr", cr_link)
            for resource, link in doc_links.items():
                _seed_redirect(db, resource, link)
            logger.info("Seeded redirect links")

            # Bootstrap CR (required)
            if not _bootstrap_cr(db, cr_link):
                logger.error("CR bootstrap failed, aborting")
                return

            # Bootstrap MTR (optional, needs Tika)
            mtr_link = doc_links.get("mtr")
            if mtr_link:
                _bootstrap_mtr(db, mtr_link)
            else:
                logger.warning("No MTR link found, skipping MTR bootstrap")

            # Bootstrap IPG (optional)
            ipg_link = doc_links.get("ipg")
            if ipg_link:
                _bootstrap_ipg(db, ipg_link)
            else:
                logger.warning("No IPG link found, skipping IPG bootstrap")

    logger.info("Bootstrap complete")
