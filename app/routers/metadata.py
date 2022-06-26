from fastapi import APIRouter
from ..utils import db


router = APIRouter(include_in_schema=False)


@router.get("/cr")
async def cr_metadata():
    meta = await db.fetch_cr_metadata()
    if not meta:
        meta = []

    return {"data": meta}


@router.get("/cr-diffs")
async def cr_diff_metadata():
    meta = await db.fetch_cr_diff_metadata()
    if not meta:
        meta = []

    return {"data": meta}


@router.get("/mtr")
async def mtr_metadata():
    meta = await db.fetch_mtr_metadata()
    if not meta:
        meta = []

    return {"data": meta}


@router.get("/ipg")
async def mtr_metadata():
    meta = await db.fetch_ipg_metadata()
    if not meta:
        meta = []

    return {"data": meta}
