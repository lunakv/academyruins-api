from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import operations as ops
from src.database.db import get_db
from src.utils.response_models import Error, Mtr, MtrChunk

router = APIRouter()


@router.get("/", summary="Get Current MTR", response_model=Mtr)
def get_current_mtr(db: Session = Depends(get_db)):
    """Returns the latest available parsed version of the MTR"""
    mtr = ops.get_current_mtr(db)
    return mtr


class SectionError(Error):
    section: int


class SubsectionError(SectionError):
    subsection: int


class TitleError(Error):
    title: str


@router.get(
    "/section/{section}",
    response_model=list[MtrChunk],
    responses={404: {"model": SectionError}},
)
def get_section(section: int, db: Session = Depends(get_db)):
    """
    Returns an ordered list of subsections contained within a given section.
    The first item in this list will describe the section’s title.
    """
    mtr = ops.get_current_mtr(db)
    result = [s for s in mtr.sections if s.get("section") == section]
    if len(result):
        return result

    raise HTTPException(404, {"detail": "Section not found.", "section": section})


@router.get(
    "/subsection/{section}.{subsection}",
    response_model=MtrChunk,
    responses={404: {"model": SubsectionError}},
)
def get_subsection(section: int, subsection: int, db: Session = Depends(get_db)):
    """Returns a single subsection"""
    error_response = {"detail": "Section not found.", "section": section, "subsection": subsection}
    mtr = ops.get_current_mtr(db)
    section = [s for s in mtr.sections if s.get("section") == section and s.get("subsection") == subsection]
    if len(section) != 1:
        raise HTTPException(404, error_response)

    return section[0]


@router.get(
    "/titled/{title}",
    response_model=MtrChunk,
    responses={
        404: {"model": TitleError},
    },
    summary="Get (Sub)section by Title",
)
def get_by_title(title: str, db: Session = Depends(get_db)):
    """
    Returns a (sub)section with a corresponding title. The `title` path parameter is case-insensitive,
    but otherwise must exactly match the (sub)section's title. If a numbered (sub)section is searched, its number
    isn't considered part of its title.
    """
    title_l = title.lower()
    mtr = ops.get_current_mtr(db)
    for section in mtr.sections:
        if section["title"].lower() == title_l:
            return section

    raise HTTPException(404, {"detail": "Section not found.", "title": title})
