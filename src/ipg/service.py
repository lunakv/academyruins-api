import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session
from ipg.models import Ipg


def get_ipg_by_creation_date(db: Session, date: datetime.date) -> Ipg | None:
    return db.execute(select(Ipg).where(Ipg.creation_day == date)).scalar_one_or_none()


def upload_ipg(db: Session, file_name: str):
    db.add(Ipg(creation_day=datetime.date.today(), file_name=file_name))
