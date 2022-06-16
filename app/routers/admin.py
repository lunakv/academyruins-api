from fastapi import APIRouter
from fastapi import Response
import os
from ..resources.cache import RedirectCache
from ..utils.responses import StatusResponse, ErrorResponse

router = APIRouter()
redirects = RedirectCache()


@router.get("/update-cr", include_in_schema=False)
async def update_cr(token: str):
    if token != os.environ['ADMIN_KEY']:
        return ErrorResponse('Incorrect admin key', 403)
    new_link = await redirects.update_from_pending('cr')
    if new_link:
        return StatusResponse({"new_link": new_link})
    else:
        return ErrorResponse("No new CR link is pending.", 400)
