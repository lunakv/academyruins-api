import datetime

from fastapi import APIRouter, Response, Path, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from db import get_db
from ipg import service, schemas
from openapi.strings import filesTag
from schemas import Error

router = APIRouter()


@router.get(
    "/file/ipg/{date}",
    summary="Raw IPG by Date",
    responses={404: {"description": "No IPG with the associated date found", "model": Error}},
    tags=[filesTag.name],
)
def raw_ipg_by_date(
    response: Response, date: datetime.date = Path(description="Date of the IPG release"), db: Session = Depends(get_db)
):
    """
    Returns a raw PDF file of the Infraction Procedure Guide released at the specified date.

    The date must be specified in ISO 8601 format (YYYY-MM-DD) and must be the exact date associated with that
    document's release.
    """
    ipg = service.get_ipg_by_creation_date(db, date)
    if not ipg:
        response.status_code = 404
        return {"detail": "IPG not available for this date"}

    path = "src/static/raw_docs/ipg/" + ipg.file_name  # FIXME hardcoded path
    return FileResponse(path)


@router.get("/metadata/ipg", response_model=schemas.IpgMetadata, include_in_schema=False)
def ipg_metadata(db: Session = Depends(get_db)):
    meta = service.get_ipg_metadata(db)
    return {"data": meta}
