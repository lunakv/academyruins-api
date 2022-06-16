from fastapi import APIRouter
from fastapi import Response
import os
from ..utils import db
from ..utils.responses import StatusResponse, ErrorResponse

router = APIRouter()


@router.get("/update-cr", include_in_schema=False)
async def update_cr(token: str):
    if token != os.environ['ADMIN_KEY']:
        return ErrorResponse('Incorrect admin key', 403)
    pending = await db.get_pending('cr')
    if not pending:
        return ErrorResponse("No new CR link is pending.", 400)

    await db.update_from_pending('cr')
    return StatusResponse({"new_link": True})
