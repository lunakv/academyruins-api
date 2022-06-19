from fastapi import APIRouter, BackgroundTasks
import os
from ..utils import db
from ..parsing.refresh_cr import refresh_cr
from ..utils.responses import StatusResponse, ErrorResponse

router = APIRouter()


@router.get("/update-cr", include_in_schema=False)
async def update_cr(token: str, background_tasks: BackgroundTasks):
    if token != os.environ['ADMIN_KEY']:
        return ErrorResponse('Incorrect admin key', 403)
    new_link = await db.get_pending('cr')
    if not new_link:
        return ErrorResponse("No new CR link is pending.", 400)

    await db.update_from_pending('cr')
    background_tasks.add_task(refresh_cr, new_link)  # TODO add diff + check before publish
    return StatusResponse({"new_link": new_link})
