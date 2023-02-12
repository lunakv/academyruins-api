from typing import Union

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..database import operations as ops
from ..database.db import get_db
from ..database.models import PendingCrDiff
from ..utils.models import Error, PendingCRDiffResponse

router = APIRouter(include_in_schema=False)


@router.get("/cr", response_model=Union[PendingCRDiffResponse, Error])
async def cr_preview(response: Response, db: Session = Depends(get_db)):
    diff: PendingCrDiff = ops.get_pending_cr_diff(db)
    if not diff:
        response.status_code = 404
        return {"detail": "No diffs are pending"}

    return {"data": {"changes": diff.changes, "source_set": diff.source.set_name}}
