from datetime import date
from typing import Literal
from ..resources import static_paths as paths
import requests

from ..utils import db


async def download_doc(link: str, kind: Literal["mtr", "ipg"]):
    directory = paths.docs_dir + "/" + kind
    filename = kind + "-" + date.today().isoformat() + ".pdf"
    filepath = directory + "/" + filename

    r = requests.get(link, stream=True)

    with open(filepath, "wb") as fd:
        for chunk in r.iter_content(chunk_size=None):
            fd.write(chunk)

    await db.upload_doc(filename, kind)
