from datetime import date
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from diffs import service
from db import get_db
from diffs.models import PendingCrDiff
from difftool.diffsorter import CRDiffSorter

from diffs import schemas
from openapi.strings import diffTag

router = APIRouter(tags=[diffTag.name])


@router.get(
    "/diff/cr",
    summary="CR diff",
    response_model=Union[schemas.CrDiffError, schemas.CRDiff],
    responses={200: {"model": schemas.CRDiff}, 404: {"model": schemas.CrDiffError}},
)
async def cr_diff(
    response: Response,
    old: str | None = Query(None, description="Set code of the old set.", min_length=3, max_length=5),
    new: str | None = Query(None, description="Set code of the new set", min_length=3, max_length=5),
    nav: bool | None = Query(False, description="Flag to include the navigation data."),
    db: Session = Depends(get_db),
):
    """
    Returns a diff of the CR between the two specified sets. Diffs only exist for neighboring CR releases.

    The set code query parameters are **not** case-sensitive. If both are supplied, the server attempts to find a
    diff between exactly those two sets. If only one is supplied, a diff with that set at the provided end is found.
    If neither is supplied, the latest CR diff is returned.

    The `changes` property is an ordered array of diff items, with each item consisting of the `old` and `new`
    versions of a rule. If a new rule is added, `old` is `null`. If an old rule is deleted, `new` is `null`.
    Otherwise, the differing parts of the `ruleText` string are wrapped between "<<<<" and ">>>>". Rules with
    identical text but changed rule number aren't part of this array, and neither are rules whose only change in text
    was a reference to a renumbered rule.

    The `moves` property contains an ordered array representing the rules that changed their number but didn't change
    their content. This property may be `null` or missing. If present, each element in the array is a dictionary with
    strings describing `from` which number `to` which number the rule moved. of strings, containing the old and new
    numbers for the given rule. No items that are part of the `changes` property are included here. In particular,
    this means that both values are always present and not `null` nor empty.

    `sourceSet` and `destSet` contain full names of the sets being diffed, and `sourceCode` and `destCode` contain
    the canonical set codes of those sets. If the `nav` query parameter is set to `true`, an optional `nav` property
    is added to the response, containing codes of sets in the preceding and following diffs (if such diffs exist).
    """
    old = old and old.upper()
    new = new and new.upper()

    diff = service.get_cr_diff(db, old, new)
    if diff is None:
        response.status_code = 404
        return {
            "detail": "No diff between these set codes found",
            "old": old,
            "new": new,
        }

    sorter = CRDiffSorter()
    changes = sorter.sort_diffs([service.format_cr_change(change) for change in diff.get_changes()])
    moves = [schemas.CRMoveItem(from_number=m.old_number, to_number=m.new_number) for m in diff.get_moves()]
    moves.sort(key=lambda m: sorter.move_to_sort_key((m.from_number, m.to_number)))

    ret_val = {
        "creationDay": diff.creation_day,
        "changes": changes,
        "sourceSet": diff.source.set_name,
        "sourceCode": diff.source.set_code,
        "destSet": diff.dest.set_name,
        "destCode": diff.dest.set_code,
        "moves": moves,
    }

    if nav:
        before = service.get_cr_diff(db, None, diff.source.set_code)
        after = service.get_cr_diff(db, diff.dest.set_code, None)
        ret_val["nav"] = {
            "prevSourceCode": before and before.source.set_code,
            "nextDestCode": after and after.dest.set_code,
        }

    return ret_val


@router.get(
    "/diff/mtr/{effective_date}",
    summary="MTR diff",
    response_model=Union[schemas.MtrDiffError, schemas.MtrDiff],
    responses={200: {"model": schemas.MtrDiff}, 404: {"model": schemas.MtrDiffError}},
)
def mtr_diff(
    effective_date: date = Path(description="Effective date of the “new“ set of the diff"),
    db: Session = Depends(get_db),
):
    diff = service.get_mtr_diff(db, effective_date)
    if diff is None:
        raise HTTPException(404, {"detail": "No diff found at this date.", "effective_date": effective_date})

    return {
        "changes": diff.changes,
        "effectiveDate": effective_date,
    }


@router.get("/diff/mtr/", status_code=307, summary="Latest MTR diff", responses={307: {"content": None}})
def latest_mtr_diff(db: Session = Depends(get_db)):
    mtr = service.get_latest_mtr_diff(db)
    return RedirectResponse("./" + mtr.effective_date.isoformat())


@router.get("/metadata/cr-diffs", include_in_schema=False)
async def cr_diff_metadata(db: Session = Depends(get_db)):
    meta = service.get_cr_diff_metadata(db)

    if meta:
        ret = [
            {"creationDay": d, "sourceCode": sc, "destCode": dc, "destName": n, "bulletinUrl": b}
            for d, sc, dc, n, b in meta
        ]
    else:
        ret = []

    return {"data": ret}


@router.get("/admin/pending/cr", include_in_schema=False)
async def cr_preview(response: Response, db: Session = Depends(get_db)):
    diff: PendingCrDiff = service.get_pending_cr_diff(db)
    if not diff:
        response.status_code = 404
        return {"detail": "No diffs are pending"}

    return {"data": {"changes": diff.changes, "source_set": diff.source.set_name}}


@router.get("/admin/pending/mtr", include_in_schema=False)
def mtr_preview(db: Session = Depends(get_db)):
    mtr = service.get_pending_mtr_diff(db)
    if not mtr:
        raise HTTPException(404, "No diffs are pending")

    return {"effective_date": mtr.dest.effective_date, "changes": mtr.changes}
