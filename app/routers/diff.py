import json
from fastapi.responses import RedirectResponse

from ..utils import db

from ..utils.responses import ErrorResponse, StatusResponse
from fastapi import APIRouter

router = APIRouter()


@router.get('/cr/{old}-{new}')
async def cr_diff(old: str, new: str):
    old = old.upper()
    new = new.upper()

    diff = await db.fetch_diff(old, new)
    if diff is None:
        return ErrorResponse("No diff between these set codes found.", 404, {old: old, new: new})

    nav = {'next': await db.fetch_diff_codes(new, None), 'prev': await db.fetch_diff_codes(None, old)}
    diff['nav'] = nav
    # for some reason date objects aren't getting serialized? not sure what's up with that
    diff['creation_day'] = diff['creation_day'].isoformat()
    del diff['id']
    return StatusResponse(diff)


@router.get('/cr/latest')
async def latest_cr_diff():
    codes = await db.fetch_latest_diff_code()
    if codes is None:
        return ErrorResponse("No diff found", 404)
    return RedirectResponse(f'{codes["old"]}-{codes["new"]}')


@router.get('/debug')
async def test():
    with open('./app/difftool/SNC-CLB.json', 'r') as file:
        diff = json.load(file)

    await db.upload_diff(diff)
    return {'yay': 'hooray'}


