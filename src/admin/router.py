import os

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from src.admin import service
from src.db import get_db
from src.extractor.cr.refresh_cr import refresh_cr
from src.extractor.ipg.refresh_ipg import refresh_ipg
from src.extractor.mtr.refresh_mtr import refresh_mtr
from src.schemas import ResponseModel

router = APIRouter(include_in_schema=False)


@router.get("/admin/update-link/{doctype}")
def update_cr(
    doctype: str, token: str, response: Response, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    doctype = doctype.lower()
    if token != os.environ["ADMIN_KEY"]:
        response.status_code = 403
        return {"detail": "Incorrect admin key"}

    new_link = service.apply_pending_redirect(db, doctype)
    if not new_link:
        raise HTTPException(400, f"No new {doctype} link is pending")

    db.commit()
    if doctype == "cr":
        background_tasks.add_task(refresh_cr, new_link)
    elif doctype == "mtr":
        background_tasks.add_task(refresh_mtr, new_link)
    elif doctype == "ipg":
        background_tasks.add_task(refresh_ipg, new_link)
    return {"new_link": new_link, "type": doctype}


class Confirm(ResponseModel):
    name: str
    code: str


@router.post("/admin/confirm/cr")
def confirm_cr(body: Confirm, token: str, response: Response, db: Session = Depends(get_db)):
    if token != os.environ["ADMIN_KEY"]:  # TODO replace with better auth scheme
        response.status_code = 403
        return {"detail": "Incorrect admin key"}

    service.apply_pending_cr_and_diff(db, body.code, body.name)
    db.commit()
    return {"detail": "success"}


@router.post("/admin/confirm/mtr")
def confirm_mtr(token: str, db: Session = Depends(get_db)):
    if token != os.environ["ADMIN_KEY"]:
        raise HTTPException(403, "Incorrect admin key")
    service.apply_pending_mtr_and_diff(db)
    db.commit()
    return {"detail": "success"}


@router.post("/admin/confirm/ipg")
def confirm_ipg(token: str, db: Session = Depends(get_db)):
    if token != os.environ["ADMIN_KEY"]:
        raise HTTPException(403, "Incorrect admin key")
    service.apply_pending_ipg_and_diff(db)
    db.commit()
    return {"detail": "success"}
