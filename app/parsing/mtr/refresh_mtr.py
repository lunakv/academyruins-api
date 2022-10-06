from datetime import date
from pathlib import Path

from app.database.db import SessionLocal
from app.database.models import Mtr
from app.parsing.mtr.extract_mtr import extract
from app.parsing.refresh_docs import download_doc


def refresh_mtr(link: str):
    dir, name = download_doc(link, "mtr")
    file_path = Path(dir) / name
    sections = extract(file_path)
    mtr = Mtr(file_name=name, creation_day=date.today(), sections=sections)
    with SessionLocal() as session:
        with session.begin():
            session.add(mtr)
