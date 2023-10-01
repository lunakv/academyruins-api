import datetime

from pydantic import Field

from src.mtr.schemas import MtrChunk
from src.schemas import Error, ResponseModel


class CrDiffError(Error):
    old: str
    new: str


class MtrDiffError(Error):
    effective_date: datetime.date


class CRDiffError(Error):
    old: str | None = None
    new: str | None = None


class CRDiffRule(ResponseModel):
    ruleNum: str = Field(..., alias="ruleNumber")
    ruleText: str = Field(...)


class CRDiffItem(ResponseModel):
    old: CRDiffRule | None = None
    new: CRDiffRule | None = None


class CRMoveItem(ResponseModel):
    from_number: str = Field(..., alias="from")
    to_number: str = Field(..., alias="to")


class CrDiffMetadata(ResponseModel):
    source_set: str = Field(..., alias="sourceSet")
    source_code: str = Field(..., alias="sourceCode")
    dest_set: str = Field(..., alias="destSet")
    dest_code: str = Field(..., alias="destCode")


class CRDiffNavigation(ResponseModel):
    prev_source_code: str | None = Field(None, alias="prevSourceCode")
    next_dest_code: str | None = Field(None, alias="nextDestCode")


class CRDiff(CrDiffMetadata):
    creation_day: datetime.date = Field(..., alias="creationDay")
    changes: list[CRDiffItem] = Field(...)
    moves: list[CRMoveItem] = Field([], description="List of moved rules")
    nav: CRDiffNavigation | None = Field(None, description="Navigational information.")


class PendingCRDiff(ResponseModel):
    changes: list[CRDiffItem]
    source_set: str = Field(..., alias="sourceSet")


class PendingCRDiffResponse(ResponseModel):
    data: PendingCRDiff


class MtrDiffItem(ResponseModel):
    old: MtrChunk | None = None
    new: MtrChunk | None = None


class MtrDiff(ResponseModel):
    effective_date: datetime.date = Field(
        ..., description="Effective date of the “new” document of this diff", alias="effectiveDate"
    )
    changes: list[MtrDiffItem] = Field(..., description="Ordered list of changes")


class MtrDiffMetadataItem(ResponseModel):
    effective_date: datetime.date = Field(alias="effectiveDate")
