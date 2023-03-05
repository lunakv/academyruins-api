from datetime import date
from pathlib import Path

from app.database import operations as ops
from app.database.db import SessionLocal
from app.database.models import PendingMtr, PendingMtrDiff
from app.difftool.diffmaker import MtrDiffMaker
from app.parsing.mtr.extract_mtr import extract
from app.parsing.utils.download_doc import download_doc


def refresh_mtr(link: str):
    dir, name = download_doc(link, "mtr")
    file_path = Path(dir) / name
    effective_date, sections = extract(file_path)
    mtr = PendingMtr(file_name=name, creation_day=date.today(), sections=sections, effective_date=effective_date)
    with SessionLocal() as session:
        with session.begin():
            current_mtr = ops.get_current_mtr(session)
            diff_result = MtrDiffMaker().diff(current_mtr.sections, sections)
            diff = PendingMtrDiff(changes=diff_result.diff, source=current_mtr, dest=mtr)
            session.add(mtr)
            session.add(diff)
