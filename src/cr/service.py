from sqlalchemy import select
from sqlalchemy.orm import Session

from src.cr import utils
from src.cr.models import Cr
from src.cr.schemas import Trace
from src.diffs.models import CrDiff, CrDiffItem

_cr_cache: dict | None = None
_cr_toc_cache: list | None = None


def get_latest_cr(db: Session) -> Cr:
    stmt = select(Cr).order_by(Cr.creation_day.desc()).limit(1)
    result = db.execute(stmt).scalars().first()
    return result


def get_latest_cr_data(db: Session) -> dict | None:
    global _cr_cache
    if _cr_cache is None:
        cr = get_latest_cr(db)
        if cr:
            _cr_cache = cr.data
    return _cr_cache


def get_latest_cr_toc(db: Session) -> list | None:
    global _cr_toc_cache
    if _cr_toc_cache is None:
        cr = get_latest_cr(db)
        if cr:
            _cr_toc_cache = cr.toc
    return _cr_toc_cache


def invalidate_cr_cache():
    global _cr_cache, _cr_toc_cache
    _cr_cache = None
    _cr_toc_cache = None


def get_cr_by_set_code(db: Session, code: str) -> Cr | None:
    return db.execute(select(Cr).where(Cr.set_code == code)).scalar_one_or_none()


def get_rule(db: Session, number: str) -> dict | None:
    stmt = select(Cr.data[number]).order_by(Cr.creation_day.desc())
    return db.execute(stmt).scalars().first()


def get_cr_metadata(db: Session):
    return db.execute(select(Cr.creation_day, Cr.set_code, Cr.set_name).order_by(Cr.creation_day.desc())).fetchall()


def get_cr_trace(db: Session, rule_number: str) -> Trace:
    items = get_cr_trace_items(db, rule_number) or []
    return Trace(ruleNumber=rule_number, items=[utils.format_trace_item(item) for item in items])


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
