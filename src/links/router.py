from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from openapi.strings import redirectTag
from src.openapi.no422 import no422

from links import service
from db import get_db
from schemas import Error

router = APIRouter(tags=[redirectTag.name])


@router.get("/link/cr", status_code=307, summary="Link to CR", responses={307: {"content": None}})
def cr_link(db: Session = Depends(get_db)):
    """
    Redirects to an up-to-date TXT version of the Comprehensive Rules.
    """
    return RedirectResponse(service.get_redirect(db, "cr"))


@router.get("/link/mtr", status_code=307, summary="Link to MTR", responses={307: {"content": None}})
def mtr_link(db: Session = Depends(get_db)):
    """
    Redirects to an up-to-date PDF version of the Magic Tournament Rules.
    """
    return RedirectResponse(service.get_redirect(db, "mtr"))


@router.get("/link/ipg", status_code=307, summary="Link to IPG", responses={307: {"content": None}})
def ipg_link(db: Session = Depends(get_db)):
    """
    Redirects to an up-to-date PDF version of the Magic Infraction Procedure Guide
    """
    return RedirectResponse(service.get_redirect(db, "ipg"))


@router.get("/link/jar", status_code=307, summary="Link to JAR", responses={307: {"content": None}})
def jar_link(db: Session = Depends(get_db)):
    """
    Redirects to an up-to-date PDF version of the Judging at Regular REL document
    """
    return RedirectResponse(service.get_redirect(db, "jar"))


class LinkError(Error):
    resource: str


@no422
@router.get(
    "/link/{resource}",
    status_code=307,
    summary="Other links",
    responses={307: {"content": None}, 404: {"description": "Link to resource does not exist.", "model": LinkError}},
)
def other_link(resource: str, response: Response, db: Session = Depends(get_db)):
    """
    Catchall route for other unofficial or undocumented redirects (e.g. the AIPG).
    See <https://mtgdoc.link> for the full list of supported values.
    """
    url = service.get_redirect(db, resource)
    if url:
        return RedirectResponse(url)
    response.status_code = 404
    return {"detail": "Not found", "resource": resource}
