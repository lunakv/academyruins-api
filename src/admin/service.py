from sqlalchemy import select
from sqlalchemy.orm import Session

from cr.models import Cr, PendingCr
from diffs.models import CrDiff, CrDiffItem, MtrDiff, PendingCrDiff, PendingMtrDiff
from links.models import PendingRedirect, Redirect
from mtr.models import Mtr, PendingMtr
from mtr.service import get_pending_mtr


def apply_pending_redirect(db: Session, resource: str) -> str | None:
    current: Redirect | None = db.get(Redirect, resource)
    pending: PendingRedirect | None = db.get(PendingRedirect, resource)
    if not pending:
        return None

    ret = pending.link
    if current:
        current.link = ret
    else:
        db.add(Redirect(resource=resource, link=ret))
    db.delete(pending)
    return ret


def apply_pending_cr_and_diff(db: Session, set_code: str, set_name: str) -> None:
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
    )
    db.add(newCr)
    db.add(newDiff)
    db.delete(pendingCr)
    db.delete(pendingDiff)


def apply_pending_mtr_and_diff(db: Session):
    pending: PendingMtr = get_pending_mtr(db)
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
