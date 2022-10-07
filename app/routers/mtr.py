from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import operations as ops
from app.database.db import get_db
from app.utils.models import Error, MtrNumberedSection, MtrSubsection, MtrAuxiliarySection, Mtr

router = APIRouter()


@router.get("/", summary="Get Current MTR", response_model=Mtr)
def get_current_mtr(db: Session = Depends(get_db)):
    """Returns the latest available parsed version of the MTR"""
    mtr = ops.get_current_mtr(db)
    return {"creation_day": mtr.creation_day, "effective_date": mtr.effective_date, "content": mtr.sections}


class SectionError(Error):
    section: int


class SubsectionError(SectionError):
    subsection: int


class TitleError(Error):
    title: str


@router.get(
    "/section/{section}",
    response_model=MtrNumberedSection,
    responses={404: {"model": SectionError}},
)
def get_section(section: int, db: Session = Depends(get_db)):
    """Returns a single numbered section of the MTR with all its subsections"""
    mtr = ops.get_current_mtr(db)
    result = [s for s in mtr.sections if s.get("section") == section]
    if len(result) == 1:
        return result[0]

    raise HTTPException(404, {"detail": "Section not found.", "section": section})


@router.get(
    "/subsection/{section}.{subsection}",
    response_model=MtrSubsection,
    responses={404: {"model": SubsectionError}},
)
def get_subsection(section: int, subsection: int, db: Session = Depends(get_db)):
    """Returns a single subsection"""
    error_response = {"detail": "Section not found.", "section": section, "subsection": subsection}
    mtr = ops.get_current_mtr(db)
    section = [s for s in mtr.sections if s.get("section") == section]
    if len(section) != 1:
        raise HTTPException(404, error_response)

    subsection = [ss for ss in section[0]["subsections"] if ss["subsection"] == subsection]
    if len(section) != 1:
        raise HTTPException(404, error_response)

    return subsection[0]


@router.get(
    "/titled/{title}",
    response_model=Union[MtrSubsection, MtrNumberedSection, MtrAuxiliarySection],
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

    Note that the shape of the response returned by this route is dependent on the type of (sub)section found.
    """
    title_l = title.lower()
    mtr = ops.get_current_mtr(db)
    for section in mtr.sections:
        if section["title"].lower() == title_l:
            return section
        for subsection in section.get("subsections") or []:
            if subsection["title"].lower() == title_l:
                return subsection

    raise HTTPException(404, {"detail": "Section not found.", "title": title})
