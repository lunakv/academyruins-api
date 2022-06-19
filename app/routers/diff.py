import json
from typing import Union

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

    return StatusResponse({'diff': diff})


@router.get('/debug')
async def test():
    with open('./app/difftool/SNC-CLB.json', 'r') as file:
        diff = json.load(file)

    await db.upload_diff(diff)
    return {'yay': 'hooray'}


