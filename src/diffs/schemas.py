import datetime

from pydantic import BaseModel, Field

from mtr.schemas import MtrChunk
from utils.response_models import Error


class CrDiffError(Error):
    old: str
    new: str


class MtrDiffError(Error):
    effective_date: datetime.date


class CRDiffError(Error):
    old: str
    new: str


class CRDiffRule(BaseModel):
    ruleNum: str = Field(..., alias="ruleNumber")
    ruleText: str = Field(...)


class CRDiffItem(BaseModel):
    old: CRDiffRule | None
    new: CRDiffRule | None


class CRMoveItem(BaseModel):
    from_number: str = Field(..., alias="from")
    to_number: str = Field(..., alias="to")


class CrDiffMetadata(BaseModel):
    source_set: str = Field(..., alias="sourceSet")
    source_code: str = Field(..., alias="sourceCode")
    dest_set: str = Field(..., alias="destSet")
    dest_code: str = Field(..., alias="destCode")


class CRDiffNavigation(BaseModel):
    prev_source_code: str | None = Field(None, alias="prevSourceCode")
    next_dest_code: str | None = Field(None, alias="nextDestCode")


class CRDiff(CrDiffMetadata):
    creation_day: datetime.date = Field(..., alias="creationDay")
    changes: list[CRDiffItem] = Field(...)
    moves: list[CRMoveItem] = Field(description="List of moved rules")
    nav: CRDiffNavigation | None = Field(description="Navigational information.")


class PendingCRDiff(BaseModel):
    changes: list[CRDiffItem]
    source_set: str = Field(..., alias="sourceSet")


class PendingCRDiffResponse(BaseModel):
    data: PendingCRDiff


class MtrDiffItem(BaseModel):
    old: MtrChunk | None
    new: MtrChunk | None


class MtrDiff(BaseModel):
    effective_date: datetime.date = Field(
        ..., description="Effective date of the “new” document of this diff", alias="effectiveDate"
    )
    changes: list[MtrDiffItem] = Field(..., description="Ordered list of changes")
