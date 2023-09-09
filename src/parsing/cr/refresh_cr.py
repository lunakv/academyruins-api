import datetime
import re
from dataclasses import asdict

import requests

from src.database import operations as ops
from src.database.db import SessionLocal
from src.difftool.diffmaker import CRDiffMaker
from src.parsing.cr import extract_cr
from src.resources import static_paths as paths
from src.resources.cache import GlossaryCache, KeywordCache
from src.utils import notifier
from src.utils.logger import logger


def get_response_text(response: requests.Response) -> str | None:
    """
    Since WotC can't just decide on a consistent character encoding for its text files, and I don't really care for
    manually changing it every other set, this method performs a simple heuristic to decide which encodings should be
    tried out.

    It runs through a list of common encodings and checks whether the file
    a) starts with the phrase "Magic: The Gathering", and
    b) contains some properly encoded common phrases that I don't expect to disappear from the CR anytime soon.

    It also re-formats the text by replacing all line endings with just LF and removing a BOM if present.
    """
    encodings = [response.encoding, "UTF-8", "UTF-16BE", "WINDOWS-1252", "UTF-16LE", "ISO-8859-1"]

    starting_phrase = "Magic: The Gathering"
    # some phrases with non-ASCII diacritics (mostly Arabian Nights card names)
    phrases = ["Magic: The Gathering®", "™", "Ring of Ma’rûf", "Dandân", "Ghazbán Ogre"]

    bom = re.compile("^\ufeff")

    for encoding in encodings:
        response.encoding = encoding
        text = response.text
        text = bom.sub("", text)
        if text.startswith(starting_phrase) and all((phrase in text) for phrase in phrases):
            return text.replace("\r\n", "\n").replace("\r", "\n")

    return None


def download_cr(uri: str) -> tuple[str, str] | None:
    response = requests.get(uri)
    if not response.ok:
        msg = f"Couldn't download CR from link (code {response.status_code}). Tried link: {uri}"
        logger.error(msg)
        notifier.notify(msg, "CR parsing error", uri, "Tried link")
        return None

    text = get_response_text(response)
    if text is None:
        logger.error("Couldn't determine encoding for new CR")
        notifier.notify("Couldn't determine encoding for new CR", "CR parsing error")
        return None

    # save to file
    file_name = "cr-" + datetime.date.today().isoformat() + ".txt"
    file_path = paths.cr_dir + "/" + file_name
    with open(file_path, "w", encoding="utf-8") as output:
        output.write(text)
    with open(paths.current_cr, "w", encoding="utf-8") as output:
        output.write(text)

    return text, file_name


async def refresh_cr(link):
    with SessionLocal() as session:
        with session.begin():
            if link is None:
                link = ops.get_redirect(session, "cr")

            current_cr = ops.get_current_cr(session)
            new_cr = download_cr(link)
            if new_cr is None:
                return
            new_text, file_name = new_cr

            result = await extract_cr.extract(new_text)
            diff_result = CRDiffMaker().diff(current_cr.data, result["rules"])
            # TODO add to database instead?
            KeywordCache().replace(result["keywords"])
            GlossaryCache().replace(result["glossary"])
            ops.set_pending_cr_and_diff(
                session,
                result["rules"],
                [asdict(s) for s in result["toc"]],
                diff_result.diff,
                file_name,
                diff_result.moved,
            )


if __name__ == "__main__":
    refresh_cr(None)
