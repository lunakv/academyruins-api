import enum

from sqlalchemy import Column, Integer, Date, String, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

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
