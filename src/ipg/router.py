import datetime
import re

from fastapi import APIRouter, Depends, Path, Response, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.db import get_db
from src.ipg import schemas, service
from src.openapi.strings import filesTag, ipgTag
from src.schemas import Error

router = APIRouter()


@router.get("/ipg", summary="Get Current IPG", response_model=schemas.Ipg, tags=[ipgTag.name])
def get_current_ipg(db: Session = Depends(get_db)):
    """Returns the latest available parsed version of the IPG"""
    ipg = service.get_current_ipg(db)
    return ipg


@router.get(
    "/ipg/section/{section}",
    response_model=list[schemas.IpgSegment],
    responses={404: {"model": schemas.SectionError}},
    tags=[ipgTag.name],
)
def get_section(section: int, db: Session = Depends(get_db)):
    """
    Returns an ordered list of subsections contained within a given section.

    Example: The response for section `1` is a list of subsections from "1. General Philosophy" to "1.5. Sets"
    """
    ipg = service.get_current_ipg(db)
    result = [s for s in ipg.sections if s.get("section") == section]
    if result:
        return result
    raise HTTPException(404, {"detail": "Section not found.", "section": section})


section_regex = r"^(\d+)\.?(\d*)"


@router.get(
    "/ipg/numbered/{section}",
    response_model=schemas.IpgSegment,
    responses={404: {"model": schemas.NumberedSectionError}},
    tags=[ipgTag.name],
)
def get_by_number(section: str = Path(pattern=section_regex), db: Session = Depends(get_db)):
    """
    Returns a single (sub)section based on its number. The `section` parameter can take on two forms:

    - A single number, possibly with a trailing dot (`1`, `3.`). In such cases, the returned segment is the beginning of
      the given section (e.g. `Tournament Errors`)
    - Two numbers separated by a dot (`1.4`). In such cases, the returned segment is the corresponding subsection.

    Segments that are not numbered, such as the Introduction, cannot be obtained with this endpoint.
    """
    section_parts = re.match(section_regex, section).groups()
    section_number = int(section_parts[0])
    subsection_number = int(section_parts[1]) if section_parts[1] else None

    ipg = service.get_current_ipg(db)
    for sec in ipg.sections:
        if sec.get("section") == section_number and sec.get("subsection") == subsection_number:
            return sec

    error_response = {"detail": "Section not found.", "section": section_number, "subsection": subsection_number}
    raise HTTPException(404, error_response)


@router.get(
    "/ipg/titled/{title}",
    response_model=schemas.IpgSegment,
    responses={404: {"model": schemas.TitleError}},
    tags=[ipgTag.name],
)
def get_by_title(title: str, db: Session = Depends(get_db)):
    """
    Returns a single (sub)section with a given title. The `title` parameter is case-insensitive and tolerant towards
    the kind of dash provided (e.g. `Game Play Error — Missed Trigger` can be specified using either an en-dash,
    and em-dash, or a hyphen), but otherwise the title of the searched segment must match exactly. For segments that are
    numbered, the numbers aren't considered a part of the title, and neither is the associated penalty.
    """
    title_l = title.lower().replace("\u2013", "-").replace("\u2014", "-")
    ipg = service.get_current_ipg(db)

    for sec in ipg.sections:
        if sec["title"].lower().replace("\u2013", "-").replace("\u2014", "-") == title_l:
            return sec

    raise HTTPException(404, {"detail": "Section not found.", "title": title})


@router.get(
    "/file/ipg/{date}",
    summary="Raw IPG by Date",
    responses={404: {"description": "No IPG with the associated date found", "model": Error}},
    tags=[filesTag.name],
)
def raw_ipg_by_date(
    response: Response, date: datetime.date = Path(description="Date of the IPG release"), db: Session = Depends(get_db)
):
    """
    Returns a raw PDF file of the Infraction Procedure Guide released at the specified date.

    The date must be specified in ISO 8601 format (YYYY-MM-DD) and must be the exact date associated with that
    document's release.
    """
    ipg = service.get_ipg_by_creation_date(db, date)
    if not ipg:
        response.status_code = 404
        return {"detail": "IPG not available for this date"}

    path = "src/static/raw_docs/ipg/" + ipg.file_name  # FIXME hardcoded path
    return FileResponse(path)


@router.get("/metadata/ipg", response_model=schemas.IpgMetadata, include_in_schema=False)
def ipg_metadata(db: Session = Depends(get_db)):
    meta = service.get_ipg_metadata(db)
    return {"data": meta}
