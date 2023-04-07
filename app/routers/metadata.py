from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import operations as ops
from ..database.db import get_db
from ..database.models import Ipg, Mtr
from ..utils.models import MtrDiffMetadataItem, PolicyMetadata

router = APIRouter(include_in_schema=False)


@router.get("/cr")
async def cr_metadata(db: Session = Depends(get_db)):
    meta = ops.get_cr_metadata(db)

    if meta:
        ret = [{"creationDay": d, "setCode": c, "setName": n} for d, c, n in meta]
    else:
        ret = []

    return {"data": ret}


@router.get("/cr-diffs")
async def cr_diff_metadata(db: Session = Depends(get_db)):
    meta = ops.get_cr_diff_metadata(db)

    if meta:
        ret = [
            {"creationDay": d, "sourceCode": sc, "destCode": dc, "destName": n, "bulletinUrl": b}
            for d, sc, dc, n, b in meta
        ]
    else:
        ret = []

    return {"data": ret}


@router.get("/mtr", response_model=PolicyMetadata)
async def mtr_metadata(db: Session = Depends(get_db)):
    meta = ops.get_creation_dates(db, Mtr)
    return {"data": meta}


@router.get("/ipg", response_model=PolicyMetadata)
async def ipg_metadata(db: Session = Depends(get_db)):
    meta = ops.get_creation_dates(db, Ipg)
    return {"data": meta}


@router.get("/mtr-diffs", response_model=list[MtrDiffMetadataItem])
def mtr_diff_metadata(db: Session = Depends(get_db)):
    meta = ops.get_mtr_diff_metadata(db)
    return meta
