import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.cr.models import Cr, PendingCr
from src.diffs.models import CrDiff, CrDiffItem, MtrDiff, PendingCrDiff, PendingMtrDiff
from src.link.models import PendingRedirect, Redirect
from src.mtr.models import Mtr, PendingMtr
from src.mtr.service import get_pending_mtr


def get_redirects(db: Session) -> list[Redirect]:
    return list(db.execute(select(Redirect).order_by(Redirect.resource)).scalars())


def get_pending_redirects(db: Session) -> list[PendingRedirect]:
    return list(db.execute(select(PendingRedirect).order_by(PendingRedirect.resource)).scalars())


def set_redirect(db: Session, resource: str, link: str) -> None:
    current: Redirect | None = db.get(Redirect, resource)
    if current:
        current.link = link
    else:
        db.add(Redirect(resource=resource, link=link))


def apply_pending_redirect(db: Session, resource: str) -> str | None:
    pending: PendingRedirect | None = db.get(PendingRedirect, resource)
    if not pending:
        return None

    ret = pending.link
    set_redirect(db, resource, ret)
    db.delete(pending)
    return ret


def apply_pending_cr_and_diff(db: Session, set_code: str, set_name: str, bulletin_url: str | None = None) -> None:
    pendingCr: PendingCr = db.execute(select(PendingCr)).scalar_one()
    pendingDiff: PendingCrDiff = db.execute(select(PendingCrDiff)).scalar_one()
    diff_items = [CrDiffItem.from_change(x) for x in pendingDiff.changes]
    diff_items += [CrDiffItem.from_move(x) for x in pendingDiff.moves]
    newCr = Cr(
        creation_day=pendingCr.creation_day,
        data=pendingCr.data,
        set_name=set_name,
        set_code=set_code,
        file_name=pendingCr.file_name,
        toc=pendingCr.toc,
    )
    newDiff = CrDiff(
        creation_day=pendingDiff.creation_day,
        source_id=pendingDiff.source_id,
        dest=newCr,
        items=diff_items,
        bulletin_url=bulletin_url,
    )
    db.add(newCr)
    db.add(newDiff)
    db.delete(pendingCr)
    db.delete(pendingDiff)


def apply_pending_mtr_and_diff(db: Session, effective_date: datetime.date | None = None):
    pending: PendingMtr = get_pending_mtr(db)
    if effective_date:
        pending.effective_date = effective_date
    pending_diff: PendingMtrDiff = db.execute(select(PendingMtrDiff)).scalar_one()
    mtr = Mtr(
        file_name=pending.file_name,
        creation_day=pending.creation_day,
        effective_date=pending.effective_date,
        sections=pending.sections,
    )

    diff = MtrDiff(changes=pending_diff.changes, source_id=pending_diff.source_id, dest=mtr)

    db.add(mtr)
    db.delete(pending)
    db.add(diff)
    db.delete(pending_diff)
