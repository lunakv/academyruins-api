import datetime
import os

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.db import get_db
from src.ipg import schemas, service
from src.openapi.strings import filesTag
from src.resources import static_paths as paths
from src.schemas import Error

router = APIRouter()


@router.get(
    "/file/ipg/{date}",
    summary="Raw IPG by Date",
    responses={404: {"description": "No IPG with the associated date found", "model": Error}},
    tags=[filesTag.name],
)
def raw_ipg_by_date(
    date: datetime.date = Path(description="Date of the IPG release"), db: Session = Depends(get_db)
):
    """
    Returns a raw PDF file of the Infraction Procedure Guide released at the specified date.

    The date must be specified in ISO 8601 format (YYYY-MM-DD) and must be the exact date associated with that
    document's release.
    """
    ipg = service.get_ipg_by_creation_date(db, date)
    if not ipg:
        raise HTTPException(404, {"detail": "IPG not available for this date"})

    path = os.path.join(paths.ipg_dir, ipg.file_name)
    return FileResponse(path)


@router.get("/metadata/ipg", response_model=schemas.IpgMetadata, include_in_schema=False)
def ipg_metadata(db: Session = Depends(get_db)):
    meta = service.get_ipg_metadata(db)
    return {"data": meta}
