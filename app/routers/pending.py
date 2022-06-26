from fastapi import APIRouter, Response
from ..utils import db

router = APIRouter(include_in_schema=False)


@router.get('/cr')
async def cr_preview(response: Response):
    changes = await db.fetch_pending_diff()
    if not changes:
        response.status_code = 404
        return {"detail": "No diffs are pending"}

    return {'data': changes}
