import os
from datetime import date
from typing import Literal

import requests

from src.resources import static_paths as paths

_kind_dirs = {"mtr": paths.mtr_dir, "ipg": paths.ipg_dir}


def download_doc(link: str, kind: Literal["mtr", "ipg"]):

    directory = _kind_dirs[kind]
    filename = kind + "-" + date.today().isoformat() + ".pdf"
    filepath = os.path.join(directory, filename)

    r = requests.get(link, stream=True)

    with open(filepath, "wb") as fd:
        for chunk in r.iter_content(chunk_size=None):
            fd.write(chunk)

    return directory, filename
