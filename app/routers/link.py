from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from ..utils import db

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
