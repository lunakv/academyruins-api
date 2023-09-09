from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.openapi.no422 import no422

from ..database import operations as ops
from ..database.db import get_db
from ..utils.response_models import Error

router = APIRouter()


@router.get("/cr", status_code=307, summary="Link to CR", responses={307: {"content": None}})
def cr_link(db: Session = Depends(get_db)):
    """
    Redirects to an up-to-date TXT version of the Comprehensive Rules.
    """
    return RedirectResponse(ops.get_redirect(db, "cr"))


@router.get("/mtr", status_code=307, summary="Link to MTR", responses={307: {"content": None}})
async def mtr_link(db: Session = Depends(get_db)):
    """
    Redirects to an up-to-date PDF version of the Magic Tournament Rules.
    """
    return RedirectResponse(ops.get_redirect(db, "mtr"))


@router.get("/ipg", status_code=307, summary="Link to IPG", responses={307: {"content": None}})
async def ipg_link(db: Session = Depends(get_db)):
    """
    Redirects to an up-to-date PDF version of the Magic Infraction Procedure Guide
    """
    return RedirectResponse(ops.get_redirect(db, "ipg"))


@router.get("/jar", status_code=307, summary="Link to JAR", responses={307: {"content": None}})
async def jar_link(db: Session = Depends(get_db)):
    """
    Redirects to an up-to-date PDF version of the Judging at Regular REL document
    """
    return RedirectResponse(ops.get_redirect(db, "jar"))


class LinkError(Error):
    resource: str


@no422
@router.get(
    "/{resource}",
    status_code=307,
    summary="Other links",
    responses={307: {"content": None}, 404: {"description": "Link to resource does not exist.", "model": LinkError}},
)
async def other_link(resource: str, response: Response, db: Session = Depends(get_db)):
    """
    Catchall route for other unofficial or undocumented redirects (e.g. the AIPG).
    See <https://mtgdoc.link> for the full list of supported values.
    """
    url = ops.get_redirect(db, resource)
    if url:
        return RedirectResponse(url)
    response.status_code = 404
    return {"detail": "Not found", "resource": resource}
