import datetime

from pydantic import BaseModel, Field


class IpgMetadataItem(BaseModel):
    creation_day: datetime.date = Field(..., alias="creationDay")


class IpgMetadata(BaseModel):
    data: list[IpgMetadataItem]
