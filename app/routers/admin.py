from fastapi import APIRouter
from fastapi import Response
import os
from ..resources.cache import RedirectCache

router = APIRouter()
redirects = RedirectCache()


@router.get("/update-cr", include_in_schema=False)
def update_cr(token: str, response: Response):
    if token != os.environ['ADMIN_KEY']:
        response.status_code = 403
        return {"status": 403, "details": "Incorrect admin key."}
    new_link = redirects.update_from_pending('cr')
    if new_link:
        return {"status": 200, "new_link": new_link}
    else:
        response.status_code = 400
        return {"status": 400, "details": "No new CR link is pending."}
