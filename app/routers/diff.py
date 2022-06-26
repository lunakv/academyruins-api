import json
from fastapi.responses import RedirectResponse

from ..utils import db
from ..utils.models import Error

from ..parsing.refresh_cr import refresh_cr
from fastapi import APIRouter, BackgroundTasks, Response

from ..utils.remove422 import no422

router = APIRouter()


@router.get('/cr/{old}-{new}')
@no422
async def cr_diff(old: str, new: str, response: Response):
    old = old.upper()
    new = new.upper()

    diff = await db.fetch_diff(old, new)
    if diff is None:
        response.status_code = 404
        return {"detail": "No diff between these set codes found", "old": old, "new": new}

    nav = {'next': await db.fetch_diff_codes(new, None), 'prev': await db.fetch_diff_codes(None, old)}
    diff['nav'] = nav

    return diff


@router.get('/cr/latest', status_code=307, responses={
    307: {"description": "Redirects to the latest CR diff in the database", "content": None}
})
async def latest_cr_diff():
    codes = await db.fetch_latest_diff_code()
    return RedirectResponse(f'{codes["old"]}-{codes["new"]}')
