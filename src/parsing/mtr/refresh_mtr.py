from datetime import date
from pathlib import Path

from db import SessionLocal
from mtr.models import PendingMtr
from mtr.service import get_current_mtr
from diffs.models import PendingMtrDiff
from src.difftool.diffmaker import MtrDiffMaker
from src.parsing.mtr.extract_mtr import extract
from src.parsing.utils.download_doc import download_doc


def refresh_mtr(link: str):
    dir, file_name = download_doc(link, "mtr")
    file_path = Path(dir) / file_name
    effective_date, sections = extract(file_path)
    mtr = PendingMtr(file_name=file_name, creation_day=date.today(), sections=sections, effective_date=effective_date)
    with SessionLocal() as session:
        with session.begin():
            current_mtr = get_current_mtr(session)
            diff_result = MtrDiffMaker().diff(current_mtr.sections, sections)
            diff = PendingMtrDiff(changes=diff_result.diff, source=current_mtr, dest=mtr)
            session.add(mtr)
            session.add(diff)
