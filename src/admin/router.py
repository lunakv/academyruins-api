import os

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.admin import service
from src.db import get_db
from src.extractor.cr.refresh_cr import refresh_cr
from src.extractor.ipg.refresh_ipg import refresh_ipg
from src.extractor.mtr.refresh_mtr import refresh_mtr
from src.schemas import ResponseModel

router = APIRouter(include_in_schema=False)

_bearer = HTTPBearer()


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(_bearer)):
    if credentials.credentials != os.environ["ADMIN_KEY"]:
        raise HTTPException(403, "Incorrect admin key")


@router.get("/admin/update-link/{doctype}", dependencies=[Depends(verify_admin_token)])
def update_cr(doctype: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    doctype = doctype.lower()

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


@router.post("/admin/confirm/cr", dependencies=[Depends(verify_admin_token)])
def confirm_cr(body: Confirm, db: Session = Depends(get_db)):
    service.apply_pending_cr_and_diff(db, body.code, body.name)
    db.commit()
    return {"detail": "success"}


@router.post("/admin/confirm/mtr", dependencies=[Depends(verify_admin_token)])
def confirm_mtr(db: Session = Depends(get_db)):
    service.apply_pending_mtr_and_diff(db)
    db.commit()
    return {"detail": "success"}
