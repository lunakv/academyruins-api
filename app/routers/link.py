from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from ..resources.cache import RedirectCache

router = APIRouter()
redirects = RedirectCache()


@router.get("/cr", status_code=307, responses={
    307: {"description": 'Redirects to an up-to-date TXT version of the Comprehensive rules.', 'content': None}})
def get_cr():
    return RedirectResponse(redirects.get('cr'))
