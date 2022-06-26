from fastapi import APIRouter, BackgroundTasks, Response
import os

from pydantic import BaseModel

from ..utils import db
from ..parsing.refresh_cr import refresh_cr

router = APIRouter(include_in_schema=False)


@router.get("/update-cr")
async def update_cr(token: str, response: Response, background_tasks: BackgroundTasks):
    if token != os.environ['ADMIN_KEY']:
        response.status_code = 403
        return {"detail": "Incorrect admin key"}
    new_link = await db.get_pending('cr')
    if not new_link:
        response.status_code = 400
        return {"detail": "No new CR link is pending"}

    await db.update_from_pending('cr')
    background_tasks.add_task(refresh_cr, new_link)
    return {"new_link": new_link}


class Confirm(BaseModel):
    name: str
    code: str


@router.post("/confirm/cr")
async def confirm_cr(body: Confirm, token: str, response: Response):
    if token != os.environ['ADMIN_KEY']:  # TODO replace with better auth scheme
        response.status_code = 403
        return {"detail": 'Incorrect admin key'}
    await db.confirm_pending_cr_and_diff(body.code, body.name)
    return {'detail': 'success'}
