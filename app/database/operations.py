from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Cr, Redirect, PendingRedirect, CrDiff


def get_current_cr(db: Session):
    stmt = select(Cr.data).order_by(Cr.creation_day.desc())
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


def get_diff(db: Session, old_code: str, new_code: str):
    stmt = select(CrDiff).where(CrDiff.source_id == old_code and CrDiff.dest_id == new_code)
    return db.execute(stmt).scalar_one_or_none()
