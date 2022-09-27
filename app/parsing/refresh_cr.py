import datetime
import re

import requests

from app.database import operations as ops
from app.database.db import SessionLocal
from app.parsing.difftool.diffmaker import CRDiffMaker
from app.utils.logger import logger
from . import extract_cr
from ..resources import static_paths as paths
from ..resources.cache import KeywordCache, GlossaryCache


def download_cr(uri):
    response = requests.get(uri)
    if not response.ok:
        logger.error(f"Couldn't download CR from link (code {response.status_code}). Tried link: {uri}")
        return

    response.encoding = "utf-8"
    text = response.text
    # replace CR and CRLF with LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # remove BOM
    bom = re.compile("^\ufeff")
    text = re.sub(bom, "", text)

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
            new_text, file_name = download_cr(link)
            result = await extract_cr.extract(new_text)

            diff_result = CRDiffMaker().diff(current_cr, result["rules"])
            # TODO add to database instead?
            KeywordCache().replace(result["keywords"])
            GlossaryCache().replace(result["glossary"])
            ops.set_pending_cr_and_diff(session, result["rules"], diff_result.diff, file_name)


if __name__ == "__main__":
    refresh_cr(None)
