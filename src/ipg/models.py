from sqlalchemy import Column, Date, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB

from src.models import Base


class Ipg(Base):
    __tablename__ = "ipg"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date, index=True)
    file_name = Column(Text)
    sections = Column(JSONB)
    effective_date = Column(Date, index=True)


class PendingIpg(Base):
    __tablename__ = "ipg_pending"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date, index=True)
    file_name = Column(Text)
    sections = Column(JSONB)
    effective_date = Column(Date, index=True)
