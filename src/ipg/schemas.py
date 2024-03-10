import datetime
from enum import Enum

from pydantic import Field

from src.schemas import ResponseModel, Error


class SectionError(Error):
    section: int


class NumberedSectionError(Error):
    section: str


class TitleError(Error):
    title: str


class Penalty(str, Enum):
    noPenalty = "No Penalty"
    warning = "Warning"
    gameLoss = "Game Loss"
    matchLoss = "Match Loss"
    disqualification = "Disqualification"


class IpgSegment(ResponseModel):
    section: int | None = Field(
        None,
        description="Number of the section this segment belongs to (e.g. `2` for subsection 2.3). Can be missing for "
        "unnumbered sections.",
    )
    subsection: int | None = Field(
        None,
        description="Number of the subsection this segment belongs to (e.g. `3` for subsection 2.3). Can be missing for"
        " unnumbered sections and for top-level sections (e.g. `1.`).",
    )
    penalty: Penalty | None = Field(
        None,
        description="On a subsection dedicated to an infraction, the received penalty. A missing value denotes a part "
        "that does not concern a specific infraction (e.g. “General Philosophy”), *not* an infraction that receives "
        "No Penalty.",
    )
    title: str = Field(
        ...,
        description="Title of this segment, without either of its numbers or the penalty (e.g. `Game Play Errors`).",
    )
    content: str | None = Field(
        None, description="The text inside this segment (without anything included in other fields)."
    )


class Ipg(ResponseModel):
    effective_date: datetime.date = Field(
        ..., description="The day when this document started being applicable", alias="effectiveDate"
    )
    sections: list[IpgSegment] = Field(
        ...,
        description="Ordered list of all (sub)sections within this document, excluding any appendices",
        alias="content",
    )


class IpgMetadataItem(ResponseModel):
    creation_day: datetime.date = Field(..., alias="creationDay")


class IpgMetadata(ResponseModel):
    data: list[IpgMetadataItem]
