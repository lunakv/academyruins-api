from sqlalchemy import Column, Integer, Text, Date
from sqlalchemy.dialects.postgresql import JSONB

from models import Base


class Mtr(Base):
    __tablename__ = "mtr"

    id = Column(Integer, primary_key=True)
    file_name = Column(Text)
    creation_day = Column(Date, index=True)
    sections = Column(JSONB)
    effective_date = Column(Date)


class PendingMtr(Base):
    __tablename__ = "mtr_pending"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date)
    file_name = Column(Text)
    sections = Column(JSONB)
    effective_date = Column(Date)
