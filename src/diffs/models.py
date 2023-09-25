import enum
from datetime import date

from sqlalchemy import Column, Integer, Date, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from models import Base


class CrDiff(Base):
    __tablename__ = "cr_diffs"

    id = Column(Integer, primary_key=True)
    creation_day = Column(Date, nullable=False)
    source_id = Column(ForeignKey("cr.id"), nullable=False)
    dest_id = Column(ForeignKey("cr.id"), nullable=False)
    bulletin_url = Column(Text)

    dest = relationship("Cr", primaryjoin="CrDiff.dest_id == cr.id")
    source = relationship("Cr", primaryjoin="CrDiff.source_id == cr.id")
    items = relationship("CrDiffItem", back_populates="diff")

    def get_changes(self) -> list:
        return [i for i in self.items if i.kind != DiffItemKind.move]

    def get_moves(self) -> list:
        return [i for i in self.items if i.kind == DiffItemKind.move]


class DiffItemKind(enum.Enum):
    change = 1
    move = 2
    addition = 3
    deletion = 4


class CrDiffItem(Base):
    __tablename__ = "cr_diff_items"
    id = Column(Integer, primary_key=True)
    diff_id = Column(ForeignKey("cr_diffs.id"), nullable=False, index=True)
    old_number = Column(Text, index=True)
    old_text = Column(Text)
    new_number = Column(Text, index=True)
    new_text = Column(Text)

    diff = relationship("CrDiff")

    @property
    def kind(self) -> DiffItemKind:
        if self.old_text is None and self.new_text is None:
            return DiffItemKind.move
        if self.old_text is None and self.old_number is None:
            return DiffItemKind.addition
        if self.new_text is None and self.new_number is None:
            return DiffItemKind.deletion
        return DiffItemKind.change

    @staticmethod
    def from_move(move: tuple[str, str]):
        return CrDiffItem(old_number=move[0], new_number=move[1])

    @staticmethod
    def from_change(change: dict):
        item = CrDiffItem()
        if change["old"]:
            item.old_text = change["old"].get("ruleText")
            item.old_number = change["old"].get("ruleNum")
        if change["new"]:
            item.new_text = change["new"].get("ruleText")
            item.new_number = change["new"].get("ruleNum")
        return item


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
