from sqlalchemy import Column, Date, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from src.models import Base


class Cr(Base):
    __tablename__ = "cr"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date)
    set_code = Column(String(5))
    set_name = Column(String(50))
    data = Column(JSONB(astext_type=Text()))
    toc = Column(JSONB(astext_type=Text()))
    file_name = Column(Text)


class PendingCr(Base):
    __tablename__ = "cr_pending"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date)
    data = Column(JSONB(astext_type=Text()))
    toc = Column(JSONB(astext_type=Text()))
    file_name = Column(Text)
