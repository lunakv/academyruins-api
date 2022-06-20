from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse

from ..utils import db
from ..utils.responses import ErrorResponse

router = APIRouter()


@router.get('/cr/{set_code}')
async def raw_cr_by_set_code(set_code: str, request: Request):
    file_name = await db.fetch_file_name(set_code)
    if not file_name:
        return ErrorResponse('CR document not available for this set', 404, {'set': set_code})

    path = request.url_for('static', path='/raw_docs/cr/'+file_name)
    return RedirectResponse(path, status_code=308)

