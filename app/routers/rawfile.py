import datetime

from fastapi import APIRouter, Path, Response
from fastapi.responses import FileResponse

from ..utils import db
from ..utils.models import Error

router = APIRouter(tags=["Files"])


@router.get(
    "/cr/{set_code}",
    summary="Raw CR by Set Code",
    responses={404: {"description": "CR for the specified set code not found", "model": Error}},
)
async def raw_cr_by_set_code(
    response: Response,
    set_code: str = Path(description="Code of the requested set (case insensitive)", min_length=3, max_length=5),
):
    """
    Returns a raw TXT file of the CR for the specified set.
    """
    file_name = await db.fetch_cr_file_name(set_code.upper())
    if not file_name:
        response.status_code = 404
        return {"detail": "CR not available for this set"}

    path = "app/static/raw_docs/cr/" + file_name
    return FileResponse(path)


@router.get(
    "/ipg/{date}",
    summary="Raw IPG by Date",
    responses={404: {"description": "No IPG with the associated date found", "model": Error}},
)
async def raw_ipg_by_date(response: Response, date: datetime.date = Path(description="Date of the IPG release")):
    """
    Returns a raw PDF file of the Infraction Procedure Guide released at the specified date.

    The date must be specified in ISO 8601 format (YYYY-MM-DD) and must be the exact date associated with that
    document's release.
    """
    file_name = await db.fetch_ipg_file_name(date)
    if not file_name:
        response.status_code = 404
        return {"detail": "IPG not available for this date"}

    path = "app/static/raw_docs/ipg/" + file_name
    return FileResponse(path)


@router.get(
    "/mtr/{date}",
    summary="Raw MTR by Date",
    responses={404: {"description": "No MTR with the associated date found", "model": Error}},
)
async def raw_mtr_by_date(response: Response, date: datetime.date = Path(description="Date of the MTR release")):
    """
    Returns a raw PDF file of the Magic Tournament Rules released at the specified date.

    The date must be specified in ISO 8601 format (YYYY-MM-DD) and must be the exact date associated with that
    document's release.
    """
    file_name = await db.fetch_mtr_file_name(date)
    if not file_name:
        response.status_code = 404
        return {"detail": "MTR not available for this date"}

    path = "app/static/raw_docs/mtr/" + file_name
    return FileResponse(path)
