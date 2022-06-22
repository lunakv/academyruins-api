from fastapi import APIRouter
from ..utils import db
from ..utils.responses import StatusResponse

router = APIRouter()


@router.get('/cr')
async def cr_preview():
    changes = await db.fetch_pending_diff()
    status_code = 200 if changes else 404
    return StatusResponse({'data': changes}, status_code=status_code)
