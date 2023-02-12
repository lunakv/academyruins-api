from datetime import date
from typing import Literal

import requests

from ..database import operations as ops
from ..database.db import SessionLocal
from ..database.models import Ipg, Mtr
from ..resources import static_paths as paths


async def download_doc(link: str, kind: Literal["mtr", "ipg"]):

    directory = paths.docs_dir + "/" + kind
    filename = kind + "-" + date.today().isoformat() + ".pdf"
    filepath = directory + "/" + filename

    r = requests.get(link, stream=True)

    with open(filepath, "wb") as fd:
        for chunk in r.iter_content(chunk_size=None):
            fd.write(chunk)

    docType = Mtr if kind == "mtr" else Ipg

    with SessionLocal() as session:
        with session.begin():
            ops.upload_doc(session, filename, docType)
