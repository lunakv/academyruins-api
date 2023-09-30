from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ResponseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class Error(BaseModel):
    detail: str = Field(..., description="Description of the error")


class FileFormat(str, Enum):
    """
    Returned file format
    """

    txt = "txt"
    pdf = "pdf"
    any = "any"
