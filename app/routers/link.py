from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse
from ..utils import db
from ..utils.models import Error
from ..utils.remove422 import no422

router = APIRouter(tags=["Redirects"])


@router.get("/cr", status_code=307, summary="Link to CR", responses={307: {"content": None}})
async def cr_link():
    """
    Redirects to an up-to-date TXT version of the Comprehensive Rules.
    """
    return RedirectResponse(await db.get_redirect("cr"))


@router.get("/mtr", status_code=307, summary="Link to MTR", responses={307: {"content": None}})
async def mtr_link():
    """
    Redirects to an up-to-date PDF version of the Magic Tournament Rules.
    """
    return RedirectResponse(await db.get_redirect("mtr"))


@router.get("/ipg", status_code=307, summary="Link to IPG", responses={307: {"content": None}})
async def ipg_link():
    """
    Redirects to an up-to-date PDF version of the Magic Infraction Procedure Guide
    """
    return RedirectResponse(await db.get_redirect("ipg"))


@router.get("/jar", status_code=307, summary="Link to JAR", responses={307: {"content": None}})
async def jar_link():
    """
    Redirects to an up-to-date PDF version of the Judging at Regular REL document
    """
    return RedirectResponse(await db.get_redirect("jar"))


class LinkError(Error):
    resource: str


@no422
@router.get(
    "/{resource}",
    status_code=307,
    summary="Other links",
    responses={307: {"content": None}, 404: {"description": "Link to resource does not exist.", "model": LinkError}},
)
async def other_link(resource: str, response: Response):
    """
    Catchall route for other unofficial or undocumented redirects (e.g. the AIPG).
    See <https://mtgdoc.link> for the full list of supported values.
    """
    url = await db.get_redirect(resource)
    if url:
        return RedirectResponse(url)
    response.status_code = 404
    return {"detail": "Not found", "resource": resource}
