from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import operations as ops
from app.database.db import get_db

router = APIRouter()


@router.get("/", summary="Get Current MTR")
def get_current_mtr(db: Session = Depends(get_db)):
    """Returns the latest available parsed version of the MTR"""
    mtr = ops.get_current_mtr(db)
    return {"creation_day": mtr.creation_day, "content": mtr.sections}


@router.get("/section/{section}")
def get_section(section: int, response: Response, db: Session = Depends(get_db)):
    mtr = ops.get_current_mtr(db)
    result = [s for s in mtr.sections if s.get("section") == section]
    if len(result) == 1:
        return result[0]

    response.status_code = 404
    return {"detail": "Section not found.", "section": section}


@router.get("/subsection/{section}.{subsection}")
def get_subsection(section: int, subsection: int, response: Response, db: Session = Depends(get_db)):
    error_response = {"detail": "Section not found.", "section": section, "subsection": subsection}
    mtr = ops.get_current_mtr(db)
    section = [s for s in mtr.sections if s.get("section") == section]
    if len(section) != 1:
        response.status_code = 404
        return error_response

    subsection = [ss for ss in section[0]["subsections"] if ss["subsection"] == subsection]
    if len(section) != 1:
        response.status_code = 404
        return error_response

    return subsection


@router.get("/titled/{title}")
def get_by_title(title: str, response: Response, db: Session = Depends(get_db)):
    title_l = title.lower()
    mtr = ops.get_current_mtr(db)
    for section in mtr.sections:
        if section["title"].lower() == title_l:
            return section
        for subsection in section.get("subsections") or []:
            if subsection["title"].lower() == title_l:
                return subsection

    response.status_code = 404
    return {"detail": "Section not found.", "title": title}
