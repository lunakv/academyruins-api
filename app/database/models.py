from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Cr(Base):
    __tablename__ = "cr"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date)
    set_code = Column(String(5))
    set_name = Column(String(50))
    data = Column(JSONB(astext_type=Text()))
    file_name = Column(Text)


class PendingCr(Base):
    __tablename__ = "cr_pending"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date)
    data = Column(JSONB(astext_type=Text()))
    file_name = Column(Text)


class Ipg(Base):
    __tablename__ = "ipg"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date, index=True)
    file_name = Column(Text)


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


class Redirect(Base):
    __tablename__ = "redirects"

    resource = Column(Text, primary_key=True)
    link = Column(Text, nullable=False)


class PendingRedirect(Base):
    __tablename__ = "redirects_pending"

    resource = Column(Text, primary_key=True)
    link = Column(Text, nullable=False)


class CrDiff(Base):
    __tablename__ = "cr_diffs"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date, nullable=False)
    changes = Column(JSONB(astext_type=Text()))
    source_id = Column(ForeignKey("cr.id"), nullable=False)
    dest_id = Column(ForeignKey("cr.id"), nullable=False)
    bulletin_url = Column(Text)
    moves = Column(ARRAY(Text, dimensions=2))

    dest = relationship("Cr", primaryjoin="CrDiff.dest_id == Cr.id")
    source = relationship("Cr", primaryjoin="CrDiff.source_id == Cr.id")


class PendingCrDiff(Base):
    __tablename__ = "cr_diffs_pending"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date)
    source_id = Column(ForeignKey("cr.id"), nullable=False)
    dest_id = Column(ForeignKey("cr_pending.id", ondelete="CASCADE"), nullable=False)
    changes = Column(JSONB(astext_type=Text()))
    moves = Column(ARRAY(Text, dimensions=2))

    dest = relationship("PendingCr")
    source = relationship("Cr")


class MtrDiff(Base):
    __tablename__ = "mtr_diffs"

    id = Column(Integer, primary_key=True)
    changes = Column(JSONB(astext_type=Text()))
    source_id = Column(ForeignKey("mtr.id"), nullable=False)
    dest_id = Column(ForeignKey("mtr.id"), nullable=False)

    dest = relationship("Mtr", primaryjoin="MtrDiff.dest_id == Mtr.id")
    source = relationship("Mtr", primaryjoin="MtrDiff.source_id == Mtr.id")


class PendingMtrDiff(Base):
    __tablename__ = "mtr_diffs_pending"

    id = Column(Integer, primary_key=True)
    changes = Column(JSONB(astext_type=Text()))
    source_id = Column(ForeignKey("mtr.id"), nullable=False)
    dest_id = Column(ForeignKey("mtr_pending.id"), nullable=False)

    source = relationship("Mtr", primaryjoin="PendingMtrDiff.source_id == Mtr.id")
    dest = relationship("PendingMtr", primaryjoin="PendingMtrDiff.dest_id == PendingMtr.id")
