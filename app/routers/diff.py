from datetime import date
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import operations as ops
from ..database.db import get_db
from ..utils.response_models import CRDiff, CRMoveItem, Error, MtrDiff

router = APIRouter()


class CrDiffError(Error):
    old: str
    new: str


class MtrDiffError(Error):
    effective_date: date


@router.get(
    "/cr",
    summary="CR diff",
    response_model=Union[CrDiffError, CRDiff],
    responses={200: {"model": CRDiff}, 404: {"model": CrDiffError}},
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

    The set code query parameters are **not** case sensitive. If both are supplied, the server attempts to find a
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

    diff = ops.get_cr_diff(db, old, new)
    if diff is None:
        response.status_code = 404
        return {
            "detail": "No diff between these set codes found",
            "old": old,
            "new": new,
        }

    ret_val = {
        "creationDay": diff.creation_day,
        "changes": diff.changes,
        "sourceSet": diff.source.set_name,
        "sourceCode": diff.source.set_code,
        "destSet": diff.dest.set_name,
        "destCode": diff.dest.set_code,
        "moves": [CRMoveItem(from_number=f, to_number=t) for f, t in diff.moves],
    }

    if nav:
        before = ops.get_cr_diff(db, None, diff.source.set_code)
        after = ops.get_cr_diff(db, diff.dest.set_code, None)
        ret_val["nav"] = {
            "prevSourceCode": before and before.source.set_code,
            "nextDestCode": after and after.dest.set_code,
        }

    return ret_val


@router.get(
    "/mtr/{effective_date}",
    summary="MTR diff",
    response_model=Union[MtrDiffError, MtrDiff],
    responses={200: {"model": MtrDiff}, 404: {"model": MtrDiffError}},
)
def mtr_diff(
    effective_date: date = Path(description="Effective date of the “new“ set of the diff"),
    db: Session = Depends(get_db),
):
    diff = ops.get_mtr_diff(db, effective_date)
    if diff is None:
        raise HTTPException(404, {"detail": "No diff found at this date.", "effective_date": effective_date})

    return {
        "changes": diff.changes,
        "effectiveDate": effective_date,
    }


@router.get("/mtr/", status_code=307, summary="Latest MTR diff", responses={307: {"content": None}})
def latest_mtr_diff(db: Session = Depends(get_db)):
    effective_date: date = ops.get_latest_mtr_diff_effective_date(db)
    return RedirectResponse("./" + effective_date.isoformat())
