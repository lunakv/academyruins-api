from typing import Union

from fastapi import APIRouter, Depends, Path, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import operations as ops
from ..database.db import get_db
from ..utils.models import CRDiff, Error

router = APIRouter()


class DiffError(Error):
    old: str
    new: str


@router.get(
    "/cr/{old}-{new}",
    summary="CR diff",
    response_model=Union[DiffError, CRDiff],
    responses={200: {"model": CRDiff}, 404: {"model": DiffError}},
)
async def cr_diff(
    response: Response,
    old: str = Path(description="Set code of the old set.", min_length=3, max_length=5),
    new: str = Path(description="Set code of the new set", min_length=3, max_length=5),
    db: Session = Depends(get_db),
):
    """
    Returns a diff of the CR between the two specified sets. Diffs only exist for neighboring CR releases. The path
    parameters are **not** case sensitive.

    The `changes` property is an ordered array of diff items, with each item consisting of the `old` and `new`
    versions of a rule. If a new rule is added, `old` is `null`. If an old rule is deleted, `new` is `null`.
    Otherwise, the differing parts of the `ruleText` string are wrapped between "<<<<" and ">>>>". Rules with
    identical text but changed rule number aren't part of this array, and neither are rules whose only change in text
    was a reference to a renumbered rule.

    `source_set` and `dest_set` contain full names of the sets being diffed, and the `nav` property stores set codes
    of diffs immediately preceding/following this one
    """
    old = old.upper()
    new = new.upper()
    diff = ops.get_diff(db, old, new)
    if diff is None:
        response.status_code = 404
        return {
            "detail": "No diff between these set codes found",
            "old": old,
            "new": new,
        }

    def format_nav(codes):
        if not codes:
            return None
        return {"old": codes[0], "new": codes[1]}

    nav = {
        "next": format_nav(ops.get_cr_diff_codes(db, new, None)),
        "prev": format_nav(ops.get_cr_diff_codes(db, None, old)),
    }

    return {
        "creation_day": diff.creation_day,
        "changes": diff.changes,
        "source_set": diff.source.set_name,
        "dest_set": diff.dest.set_name,
        "nav": nav,
    }


@router.get("/cr/latest", status_code=307, summary="Latest CR diff", responses={307: {"content": None}})
async def latest_cr_diff(db: Session = Depends(get_db)):
    """
    Redirects to the latest CR diff available
    """
    old, new = ops.get_latest_cr_diff_code(db)
    return RedirectResponse(f"{old}-{new}")
