import datetime
from typing import Tuple, Type

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from .models import Base, Cr, CrDiff, Mtr, PendingCr, PendingCrDiff, PendingRedirect, Redirect


def get_current_cr(db: Session):
    stmt = select(Cr.data).order_by(Cr.creation_day.desc())
    result = db.execute(stmt).scalars().first()
    return result


def get_current_mtr(db: Session) -> Mtr:
    stmt = select(Mtr).order_by(Mtr.creation_day.desc())
    result = db.execute(stmt).scalars().first()
    return result


def get_rule(db: Session, number: str):
    stmt = select(Cr.data[number]).order_by(Cr.creation_day.desc())
    return db.execute(stmt).scalars().first()


def get_redirect(db: Session, resource: str) -> str | None:
    stmt = select(Redirect.link).where(Redirect.resource == resource)
    return db.execute(stmt).scalar_one_or_none()


def get_pending_redirect(db: Session, resource: str) -> str | None:
    stmt = select(PendingRedirect.link).where(PendingRedirect.resource == resource)
    return db.execute(stmt).scalar_one_or_none()


def apply_pending_redirect(db: Session, resource: str) -> None:
    current: Redirect | None = db.get(Redirect, resource)
    pending: PendingRedirect = db.get(PendingRedirect, resource)
    if current:
        current.link = pending.link
    else:
        db.add(Redirect(resource=resource, link=pending.link))
    db.delete(pending)


def set_pending(db: Session, resource: str, link: str) -> None:
    pending: PendingRedirect | None = db.get(PendingRedirect, resource)
    if pending:
        pending.link = link
    else:
        db.add(PendingRedirect(resource=resource, link=link))


def get_diff(db: Session, old_code: str, new_code: str) -> CrDiff:
    src = aliased(Cr)
    dst = aliased(Cr)

    stmt = (
        select(CrDiff)
        .join(src, CrDiff.source)
        .join(dst, CrDiff.dest)
        .where(src.set_code == old_code)
        .where(dst.set_code == new_code)
    )
    return db.execute(stmt).scalar_one_or_none()


def apply_pending_cr_and_diff(db: Session, set_code: str, set_name: str) -> None:
    pendingCr: PendingCr = db.execute(select(PendingCr)).scalar_one()
    pendingDiff: PendingCrDiff = db.execute(select(PendingCrDiff)).scalar_one()
    newCr = Cr(
        creation_day=pendingCr.creation_day,
        data=pendingCr.data,
        set_name=set_name,
        set_code=set_code,
        file_name=pendingCr.file_name,
    )
    newDiff = CrDiff(
        creation_day=pendingDiff.creation_day,
        source_id=pendingDiff.source_id,
        dest=newCr,
        changes=pendingDiff.changes,
    )
    db.add(newCr)
    db.add(newDiff)
    db.delete(pendingCr)
    db.delete(pendingDiff)


def get_latest_cr_diff_code(db: Session) -> (str, str):
    stmt = select(CrDiff).join(CrDiff.dest).order_by(Cr.creation_day.desc())
    diff: CrDiff = db.execute(stmt).scalars().first()
    return diff.source.set_code, diff.dest.set_code


def get_cr_diff_codes(db: Session, old_code: str | None, new_code: str | None) -> Tuple[str, str] | None:
    stmt = select(CrDiff)
    if old_code:
        stmt = stmt.join(Cr, CrDiff.source).where(Cr.set_code == old_code)
    elif new_code:
        stmt = stmt.join(Cr, CrDiff.dest).where(Cr.set_code == new_code)
    else:
        return None

    diff: CrDiff = db.execute(stmt).scalar_one_or_none()
    if not diff:
        return None

    return diff.source.set_code, diff.dest.set_code


def get_pending_cr_diff(db: Session) -> PendingCrDiff | None:
    return db.execute(select(PendingCrDiff)).scalar_one_or_none()


def get_cr_metadata(db: Session):
    return db.execute(select(Cr.creation_day, Cr.set_code, Cr.set_name).order_by(Cr.creation_day.desc())).fetchall()


def get_cr_diff_metadata(db: Session):
    src = aliased(Cr)
    dst = aliased(Cr)
    stmt = (
        select(CrDiff.creation_day, src.set_code, dst.set_code, dst.set_name, CrDiff.bulletin_url)
        .join(src, CrDiff.source)
        .join(dst, CrDiff.dest)
        .order_by(CrDiff.creation_day.desc())
    )
    return db.execute(stmt).fetchall()


def get_creation_dates(db: Session, table: Type[Base]):
    return db.execute(select(table.creation_day).order_by(table.creation_day.desc())).fetchall()


def get_cr_filename(db: Session, code: str) -> str | None:
    return db.execute(select(Cr.file_name).where(Cr.set_code == code)).scalar_one_or_none()


def get_latest_cr_filename(db: Session) -> str:
    return db.execute(select(Cr.file_name).order_by(Cr.creation_day.desc())).scalar()


def get_doc_filename(db: Session, date: datetime.date, table: Type[Base]) -> str | None:
    return db.execute(select(table.file_name).where(table.creation_day == date)).scalar_one_or_none()


def set_pending_cr_and_diff(db: Session, new_rules: dict, new_diff: list, file_name: str):
    new_cr = PendingCr(creation_day=datetime.date.today(), data=new_rules, file_name=file_name)
    curr_cr_id: Cr = db.execute(select(Cr.id).order_by(Cr.creation_day.desc())).scalars().first()
    new_diff = PendingCrDiff(creation_day=datetime.date.today(), source_id=curr_cr_id, dest=new_cr, changes=new_diff)
    db.add(new_cr)
    db.add(new_diff)


def upload_doc(db: Session, file_name: str, kind: Type[Base]):
    new_doc = kind(creation_day=datetime.date.today(), file_name=file_name)
    db.add(new_doc)
