import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from mtr.models import Mtr, PendingMtr


def get_current_mtr(db: Session) -> Mtr:
    stmt = select(Mtr).order_by(Mtr.creation_day.desc())
    result = db.execute(stmt).scalars().first()
    return result


def get_mtr_by_date(db: Session, date: datetime.date) -> Mtr | None:
    return db.execute(select(Mtr).where(Mtr.creation_day == date)).scalar_one_or_none()


def get_pending_mtr(db: Session) -> PendingMtr:
    return db.execute(select(PendingMtr)).scalar_one_or_none()


def get_mtr_metadata(db: Session) -> list:
    return db.execute(select(Mtr.creation_day).order_by(Mtr.creation_day.desc())).fetchall()
