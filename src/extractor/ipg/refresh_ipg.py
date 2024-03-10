from datetime import date
from pathlib import Path

from diffs.models import PendingIpgDiff
from difftool.diffmaker import IpgDiffMaker
from extractor.ipg.extract_ipg import extract
from ipg.models import PendingIpg
from ipg.service import get_current_ipg
from src.db import SessionLocal
from src.extractor.download_doc import download_doc


def refresh_ipg(link: str):
    directory, file_name = download_doc(link, "ipg")
    file_path = Path(directory) / file_name
    effective_date, sections = extract(file_path)
    ipg = PendingIpg(file_name=file_name, creation_day=date.today(), sections=sections, effective_date=effective_date)

    with SessionLocal() as session:
        with session.begin():
            current_ipg = get_current_ipg(session)
            diff_result = IpgDiffMaker().diff(current_ipg.sections, sections)
            diff = PendingIpgDiff(changes=diff_result.diff, source=current_ipg, dest=ipg)
            session.add(ipg)
            session.add(diff)
