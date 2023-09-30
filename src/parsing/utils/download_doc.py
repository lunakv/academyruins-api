from datetime import date
from typing import Literal

import requests

from resources import static_paths as paths


def download_doc(link: str, kind: Literal["mtr", "ipg"]):

    directory = paths.docs_dir + "/" + kind
    filename = kind + "-" + date.today().isoformat() + ".pdf"
    filepath = directory + "/" + filename

    r = requests.get(link, stream=True)

    with open(filepath, "wb") as fd:
        for chunk in r.iter_content(chunk_size=None):
            fd.write(chunk)

    return directory, filename
