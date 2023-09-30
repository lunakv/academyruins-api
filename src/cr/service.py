from sqlalchemy import select
from sqlalchemy.orm import Session

from cr import utils
from cr.models import Cr
from cr.schemas import TraceItem
from diffs.models import CrDiff, CrDiffItem
from diffs.schemas import CrDiffMetadata


def get_latest_cr(db: Session) -> Cr:
    stmt = select(Cr).order_by(Cr.creation_day.desc())
    result = db.execute(stmt).scalars().first()
    return result


def get_cr_by_set_code(db: Session, code: str) -> Cr | None:
    return db.execute(select(Cr).where(Cr.set_code == code)).scalar_one_or_none()


def get_rule(db: Session, number: str) -> dict | None:
    stmt = select(Cr.data[number]).order_by(Cr.creation_day.desc())
    return db.execute(stmt).scalars().first()


def get_cr_metadata(db: Session):
    return db.execute(select(Cr.creation_day, Cr.set_code, Cr.set_name).order_by(Cr.creation_day.desc())).fetchall()


def get_cr_trace(db: Session, rule_number: str) -> list[TraceItem]:
    items = get_cr_trace_items(db, rule_number) or []
    return [utils.format_trace_item(item) for item in items]


def get_cr_trace_items(db: Session, rule_number: str) -> list[CrDiffItem] | None:
    # parts that are the same for the base query and the recursive query
    common_query = select(CrDiffItem).join(CrDiff).add_columns(CrDiff.creation_day).order_by(CrDiff.creation_day.desc())

    # non-recursive part of the query (finds the latest matching change)
    base_cte = common_query.where(CrDiffItem.new_number == rule_number).limit(1).cte("trace", recursive=True)

    # recursive part of the query (finds the previous change based on the last found change)
    recursive = (
        common_query.join(base_cte, base_cte.c.old_number == CrDiffItem.new_number)
        .where(CrDiff.creation_day < base_cte.c.creation_day)
        .limit(1)
    )

    query = base_cte.union(recursive).select()
    return db.execute(select(CrDiffItem).from_statement(query)).scalars().fetchall()


def get_trace_diff_metadata(diff_item: CrDiffItem) -> CrDiffMetadata:
    diff = diff_item.diff
    return CrDiffMetadata(
        source_code=diff.source.set_code,
        source_set=diff.source.set_name,
        dest_code=diff.dest.set_code,
        dest_set=diff.dest.set_name,
    )


def format_cr_change(db_item: CrDiffItem) -> dict:
    item = {"old": None, "new": None}
    if db_item.old_number:
        item["old"] = {"ruleNum": db_item.old_number, "ruleText": db_item.old_text}
    if db_item.new_number:
        item["new"] = {"ruleNum": db_item.new_number, "ruleText": db_item.new_text}
    return item
