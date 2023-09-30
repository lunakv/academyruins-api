import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from cr.models import Cr
from diffs.models import CrDiff, CrDiffItem, MtrDiff, PendingCrDiff, PendingMtrDiff
from mtr.models import Mtr


def get_cr_diff(db: Session, old_code: str | None, new_code: str | None) -> CrDiff | None:
    src = aliased(Cr)
    dst = aliased(Cr)

    stmt = select(CrDiff).join(src, CrDiff.source).join(dst, CrDiff.dest).join(CrDiff.items)

    if not old_code and not new_code:
        stmt = stmt.order_by(CrDiff.creation_day.desc()).limit(1)
    else:
        if old_code:
            stmt = stmt.where(src.set_code == old_code)
        if new_code:
            stmt = stmt.where(dst.set_code == new_code)

    return db.execute(stmt).scalars().first()


def get_latest_mtr_diff(db: Session) -> MtrDiff:
    return db.execute(select(MtrDiff).join(MtrDiff.dest).order_by(Mtr.effective_date.desc())).scalars().first()


def get_mtr_diff(db: Session, date: datetime.date) -> MtrDiff | None:
    return db.execute(select(MtrDiff).join(MtrDiff.dest).where(Mtr.effective_date == date)).scalar_one_or_none()


def get_cr_diff_metadata(db: Session) -> list:
    src = aliased(Cr)
    dst = aliased(Cr)
    stmt = (
        select(CrDiff.creation_day, src.set_code, dst.set_code, dst.set_name, CrDiff.bulletin_url)
        .join(src, CrDiff.source)
        .join(dst, CrDiff.dest)
        .order_by(CrDiff.creation_day.desc())
    )
    return db.execute(stmt).fetchall()


def get_pending_mtr_diff(db: Session) -> PendingMtrDiff:
    return db.execute(select(PendingMtrDiff).join(PendingMtrDiff.dest)).scalar_one_or_none()


def get_pending_cr_diff(db: Session) -> PendingCrDiff | None:
    return db.execute(select(PendingCrDiff)).scalar_one_or_none()


def format_cr_change(db_item: CrDiffItem):
    item = {"old": None, "new": None}
    if db_item.old_number:
        item["old"] = {"ruleNum": db_item.old_number, "ruleText": db_item.old_text}
    if db_item.new_number:
        item["new"] = {"ruleNum": db_item.new_number, "ruleText": db_item.new_text}
    return item
