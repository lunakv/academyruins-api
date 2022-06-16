from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from ..utils import db

router = APIRouter()


@router.get("/cr", status_code=307, responses={
    307: {"description": 'Redirects to an up-to-date TXT version of the Comprehensive rules.', 'content': None}})
async def get_cr():
    return RedirectResponse(await db.get_redirect('cr'))
