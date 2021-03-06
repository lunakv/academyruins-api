import datetime
import re
from enum import Enum
from typing import Union

from fastapi import APIRouter, Path, Response, Query
from fastapi.responses import FileResponse

from ..utils import db
from ..utils.models import Error

router = APIRouter(tags=["Files"])


class Format(str, Enum):
    """
    Returned file format
    """

    txt = "txt"
    pdf = "pdf"
    any = "any"


@router.get(
    "/cr/{set_code}",
    summary="Raw CR by Set Code",
    responses={404: {"description": "CR for the specified set code not found", "model": Error}},
)
async def raw_cr_by_set_code(
    response: Response,
    set_code: str = Path(description="Code of the requested set (case insensitive)", min_length=3, max_length=5),
    format: Union[Format, None] = Query(default=Format.any),
):
    """
    Returns a raw file of the CR for the specified set. Most of the results will be UTF-8 encoded TXT files,
    but for some historic sets only a PDF version of the rulebook is available. To ensure only a specific format is
    returned, set the `format` query parameter. If set to a value besides `any`, files of other formats are treated
    as though they don't exist.
    """
    file_name = await db.fetch_cr_file_name(set_code.upper())
    if not file_name:
        response.status_code = 404
        return {"detail": "CR not available for this set"}

    if format != Format.any and not re.search(r"\." + format + "$", file_name):
        response.status_code = 404
        return {"detail": "CR for this set not available in specified format"}

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
