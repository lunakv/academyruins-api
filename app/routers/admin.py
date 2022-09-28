from fastapi import APIRouter, BackgroundTasks, Response, Depends
import os

from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import operations as ops
from ..database.db import get_db
from ..parsing.refresh_docs import download_doc
from ..parsing.refresh_cr import refresh_cr

router = APIRouter(include_in_schema=False)


@router.get("/update-link/{doctype}")
async def update_cr(
    doctype: str, token: str, response: Response, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    doctype = doctype.lower()
    if token != os.environ["ADMIN_KEY"]:
        response.status_code = 403
        return {"detail": "Incorrect admin key"}

    new_link = ops.get_pending_redirect(db, doctype)
    if not new_link:
        response.status_code = 400
        return {"detail": f"No new {doctype} link is pending"}

    ops.apply_pending_redirect(db, doctype)
    db.commit()
    if doctype == "cr":
        background_tasks.add_task(refresh_cr, new_link)
    elif doctype == "mtr" or doctype == "ipg":
        background_tasks.add_task(download_doc, new_link, doctype)
    return {"new_link": new_link, "type": doctype}


class Confirm(BaseModel):
    name: str
    code: str


@router.post("/confirm/cr")
async def confirm_cr(body: Confirm, token: str, response: Response, db: Session = Depends(get_db)):
    if token != os.environ["ADMIN_KEY"]:  # TODO replace with better auth scheme
        response.status_code = 403
        return {"detail": "Incorrect admin key"}

    ops.apply_pending_cr_and_diff(db, body.code, body.name)
    db.commit()
    return {"detail": "success"}
