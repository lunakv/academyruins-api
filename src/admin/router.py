from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import HttpUrl, field_validator
from sqlalchemy.orm import Session

from src.admin import service
from src.admin.auth import require_admin
from src.db import get_db
from src.diffs import service as diff_service
from src.extractor.cr.refresh_cr import refresh_cr
from src.extractor.ipg.refresh_ipg import refresh_ipg
from src.extractor.mtr.refresh_mtr import refresh_mtr
from src.link.service import set_pending_redirect
from src.schemas import ResponseModel

router = APIRouter(include_in_schema=False, dependencies=[Depends(require_admin)])


class Link(ResponseModel):
    link: HttpUrl


@router.get("/admin/links")
def get_links(db: Session = Depends(get_db)):
    return {"data": [{"resource": r.resource, "link": r.link} for r in service.get_redirects(db)]}


@router.put("/admin/links/{resource}")
def edit_link(resource: str, body: Link, db: Session = Depends(get_db)):
    service.set_redirect(db, resource.lower(), str(body.link))
    db.commit()
    return {"detail": "success"}


@router.get("/admin/pending-links")
def get_pending_links(db: Session = Depends(get_db)):
    return {"data": [{"resource": r.resource, "link": r.link} for r in service.get_pending_redirects(db)]}


@router.put("/admin/pending-links/{resource}")
def edit_pending_link(resource: str, body: Link, db: Session = Depends(get_db)):
    set_pending_redirect(db, resource.lower(), str(body.link))
    db.commit()
    return {"detail": "success"}


@router.post("/admin/pending-links/{resource}/confirm")
def confirm_pending_link(resource: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    resource = resource.lower()
    new_link = service.apply_pending_redirect(db, resource)
    if not new_link:
        raise HTTPException(400, f"No new {resource} link is pending")

    db.commit()
    if resource == "cr":
        background_tasks.add_task(refresh_cr, new_link)
    elif resource == "mtr":
        background_tasks.add_task(refresh_mtr, new_link)
    elif resource == "ipg":
        background_tasks.add_task(refresh_ipg, new_link)
    return {"new_link": new_link, "type": resource}


@router.get("/admin/pending-diffs")
def get_pending_diffs(db: Session = Depends(get_db)):
    cr = diff_service.get_pending_cr_diff(db)
    mtr = diff_service.get_pending_mtr_diff(db)
    return {
        "cr": cr
        and {
            "creationDay": cr.creation_day,
            "sourceSet": cr.source.set_name,
            "sourceCode": cr.source.set_code,
            "changeCount": len(cr.changes or []),
            "moveCount": len(cr.moves or []),
        },
        "mtr": mtr
        and {
            "creationDay": mtr.dest.creation_day,
            "effectiveDate": mtr.dest.effective_date,
            "changeCount": len(mtr.changes or []),
        },
    }


class Confirm(ResponseModel):
    name: str
    code: str
    bulletin: HttpUrl | None = None

    @field_validator("bulletin", mode="before")
    @classmethod
    def empty_bulletin_to_none(cls, value):
        # the confirm form sends an empty string when no bulletin is given
        return value or None


@router.post("/admin/confirm/cr")
def confirm_cr(body: Confirm, db: Session = Depends(get_db)):
    bulletin = str(body.bulletin) if body.bulletin else None
    service.apply_pending_cr_and_diff(db, body.code.upper(), body.name, bulletin)
    db.commit()
    return {"detail": "success"}


class ConfirmMtr(ResponseModel):
    effective_date: date | None = None


@router.post("/admin/confirm/mtr")
def confirm_mtr(body: ConfirmMtr | None = None, db: Session = Depends(get_db)):
    service.apply_pending_mtr_and_diff(db, body and body.effective_date)
    db.commit()
    return {"detail": "success"}
