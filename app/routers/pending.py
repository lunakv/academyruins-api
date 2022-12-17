from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..database import operations as ops
from ..database.db import get_db
from ..database.models import PendingCrDiff
from ..utils.models import Error, MtrDiff, PendingCRDiffResponse

router = APIRouter(include_in_schema=False)


@router.get("/cr", response_model=Union[PendingCRDiffResponse, Error])
async def cr_preview(response: Response, db: Session = Depends(get_db)):
    diff: PendingCrDiff = ops.get_pending_cr_diff(db)
    if not diff:
        response.status_code = 404
        return {"detail": "No diffs are pending"}

    return {"data": {"changes": diff.changes, "source_set": diff.source.set_name}}


@router.get("/mtr", response_model=MtrDiff)
def mtr_preview(db: Session = Depends(get_db)):
    mtr = ops.get_pending_mtr_diff(db)
    if not mtr:
        raise HTTPException(404, "No diffs are pending")

    return {"effective_date": mtr.dest.effective_date, "changes": mtr.changes}
