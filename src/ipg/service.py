import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.ipg.models import Ipg, PendingIpg


def get_current_ipg(db: Session) -> Ipg:
    return db.execute(select(Ipg).order_by(Ipg.creation_day.desc()).limit(1)).scalars().first()


def get_ipg_by_creation_date(db: Session, date: datetime.date) -> Ipg | None:
    return db.execute(select(Ipg).where(Ipg.creation_day == date)).scalar_one_or_none()


def get_pending_ipg(db: Session) -> PendingIpg:
    return db.execute(select(PendingIpg)).scalar_one_or_none()


def get_ipg_metadata(db: Session):
    return db.execute(select(Ipg.creation_day).order_by(Ipg.creation_day.desc())).fetchall()
