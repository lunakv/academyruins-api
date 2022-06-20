from fastapi import APIRouter
from ..utils import db
from ..utils.responses import ErrorResponse, StatusResponse

router = APIRouter()


@router.get('/cr')
async def cr_metadata():
    meta = await db.fetch_cr_metadata()
    if not meta:
        meta = []

    for row in meta:
        row['creation_day'] = row['creation_day'].isoformat()
    return StatusResponse({'data': meta})
