import datetime

from pydantic import Field

from src.schemas import Error, ResponseModel


class SectionError(Error):
    section: int


class SubsectionError(SectionError):
    subsection: int


class TitleError(Error):
    title: str


class MtrChunk(ResponseModel):
    section: int | None = Field(
        None, description="Number of the section this subsection is under (e.g. `2` for subsection 2.3)"
    )
    subsection: int | None = Field(
        None, description="Number of this (sub)section within its section (e.g. `3` for subsection 2.3)"
    )
    title: str = Field(
        ..., description="Title of this subsection, without either of its numbers (e.g. `Tournament Mechanics`)"
    )
    content: str | None = Field(
        None, description="The text inside this subsection (without the title or either number)"
    )


class Mtr(ResponseModel):
    effective_date: datetime.date = Field(
        ..., description="The day when this document started being applicable", alias="effectiveDate"
    )
    sections: list[MtrChunk] = Field(
        ...,
        description="Ordered list of all (sub)sections within this document, excluding any appendices",
        alias="content",
    )


class MtrMetadataItem(ResponseModel):
    creation_day: datetime.date = Field(..., alias="creationDay")


class MtrMetadata(ResponseModel):
    data: list[MtrMetadataItem]
