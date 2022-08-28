from typing import Union

from fastapi import APIRouter, Response, Path
from fastapi.responses import RedirectResponse

from ..utils import db
from ..utils.models import Error, CRDiff

router = APIRouter(tags=["Diffs"])


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
    diff = await db.fetch_diff(old, new)
    if diff is None:
        response.status_code = 404
        return {
            "detail": "No diff between these set codes found",
            "old": old,
            "new": new,
        }

    nav = {
        "next": await db.fetch_diff_codes(new, None),
        "prev": await db.fetch_diff_codes(None, old),
    }
    diff["nav"] = nav

    return diff


@router.get("/cr/latest", status_code=307, summary="Latest CR diff", responses={307: {"content": None}})
async def latest_cr_diff():
    """
    Redirects to the latest CR diff available
    """
    codes = await db.fetch_latest_diff_code()
    return RedirectResponse(f'{codes["old"]}-{codes["new"]}')
