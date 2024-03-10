import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.db import get_db
from src.mtr import schemas, service
from src.openapi.strings import filesTag, mtrTag
from src.schemas import Error

router = APIRouter()


@router.get("/mtr", summary="Get Current MTR", response_model=schemas.Mtr, tags=[mtrTag.name])
def get_current_mtr(db: Session = Depends(get_db)):
    """Returns the latest available parsed version of the MTR"""
    mtr = service.get_current_mtr(db)
    return mtr


@router.get(
    "/mtr/section/{section}",
    response_model=list[schemas.MtrSegment],
    responses={404: {"model": schemas.SectionError}},
    tags=[mtrTag.name],
)
def get_section(section: int, db: Session = Depends(get_db)):
    """
    Returns an ordered list of subsections contained within a given section.
    The first item in this list will describe the section’s title.
    """
    mtr = service.get_current_mtr(db)
    result = [s for s in mtr.sections if s.get("section") == section]
    if len(result):
        return result

    raise HTTPException(404, {"detail": "Section not found.", "section": section})


@router.get(
    "/mtr/subsection/{section}.{subsection}",
    response_model=schemas.MtrSegment,
    responses={404: {"model": schemas.SubsectionError}},
    tags=[mtrTag.name],
)
def get_subsection(section: int, subsection: int, db: Session = Depends(get_db)):
    """Returns a single subsection"""
    mtr = service.get_current_mtr(db)
    for sec in mtr.sections:
        if sec.get("section") == section and sec.get("subsection") == subsection:
            return sec

    error_response = {"detail": "Section not found.", "section": section, "subsection": subsection}
    raise HTTPException(404, error_response)


@router.get(
    "/mtr/titled/{title}",
    response_model=schemas.MtrSegment,
    responses={
        404: {"model": schemas.TitleError},
    },
    summary="Get (Sub)section by Title",
    tags=[mtrTag.name],
)
def get_by_title(title: str, db: Session = Depends(get_db)):
    """
    Returns a (sub)section with a corresponding title. The `title` path parameter is case-insensitive,
    but otherwise must exactly match the (sub)section's title. If a numbered (sub)section is searched, its number
    isn't considered part of its title.
    """
    title_l = title.lower()
    mtr = service.get_current_mtr(db)
    for section in mtr.sections:
        if section["title"].lower() == title_l:
            return section

    raise HTTPException(404, {"detail": "Section not found.", "title": title})


@router.get(
    "/file/mtr/{date}",
    summary="Raw MTR by Date",
    responses={404: {"description": "No MTR with the associated date found", "model": Error}},
    tags=[filesTag.name],
)
def raw_mtr_by_date(
    response: Response, date: datetime.date = Path(description="Date of the MTR release"), db: Session = Depends(get_db)
):
    """
    Returns a raw PDF file of the Magic Tournament Rules released at the specified date.

    The date must be specified in ISO 8601 format (YYYY-MM-DD) and must be the exact date associated with that
    document's release.
    """
    mtr = service.get_mtr_by_date(db, date)
    if not mtr:
        response.status_code = 404
        return {"detail": "MTR not available for this date"}

    path = "src/static/raw_docs/mtr/" + mtr.file_name  # FIXME hardcoded path
    return FileResponse(path)


@router.get("/metadata/mtr", include_in_schema=False, response_model=schemas.MtrMetadata)
def mtr_metadata(db: Session = Depends(get_db)):
    meta = service.get_mtr_metadata(db)
    return {"data": meta}
