from fastapi import APIRouter, BackgroundTasks
import os

from pydantic import BaseModel

from ..utils import db
from ..parsing.refresh_cr import refresh_cr
from ..utils.responses import StatusResponse, ErrorResponse

router = APIRouter(include_in_schema=False)


@router.get("/update-cr")
async def update_cr(token: str, background_tasks: BackgroundTasks):
    if token != os.environ['ADMIN_KEY']:
        return ErrorResponse('Incorrect admin key', 403)
    new_link = await db.get_pending('cr')
    if not new_link:
        return ErrorResponse("No new CR link is pending.", 400)

    await db.update_from_pending('cr')
    background_tasks.add_task(refresh_cr, new_link)
    return StatusResponse({"new_link": new_link})


class Confirm(BaseModel):
    name: str
    code: str


@router.post("/confirm/cr")
async def confirm_cr(body: Confirm, token: str):
    if token != os.environ['ADMIN_KEY']:  # TODO replace with better auth scheme
        return ErrorResponse('Incorrect admin key', 403)

    await db.confirm_pending_cr_and_diff(body.code, body.name)
    return StatusResponse({'details': 'success'})
