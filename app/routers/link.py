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
