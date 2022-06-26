from fastapi import APIRouter, Request, Path, Response
from starlette.responses import RedirectResponse

from ..utils import db
from ..utils.models import Error

router = APIRouter(tags=["Files"])


@router.get(
    "/cr/{set_code}",
    summary="Raw CR by Set Code",
    status_code=308,
    responses={308: {"content": None}, 404: {"description": "CR for the specified set code not found", "model": Error}},
)
async def raw_cr_by_set_code(
    request: Request,
    response: Response,
    set_code: str = Path(description="Code of the requested set (case insensitive)", min_length=3, max_length=5),
):
    """
    Redirects to a raw TXT file of the CR for the specified set.
    """
    file_name = await db.fetch_file_name(set_code.upper())
    if not file_name:
        response.status_code = 404
        return {"detail": "CR not available for this set"}

    path = request.url_for("static", path="/raw_docs/cr/" + file_name)
    return RedirectResponse(path, status_code=308)
