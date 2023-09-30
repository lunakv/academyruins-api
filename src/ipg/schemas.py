import datetime

from pydantic import Field

from schemas import ResponseModel


class IpgMetadataItem(ResponseModel):
    creation_day: datetime.date = Field(..., alias="creationDay")


class IpgMetadata(ResponseModel):
    data: list[IpgMetadataItem]
