from enum import Enum

from pydantic import BaseModel, Field


class Error(BaseModel):
    detail: str = Field(..., description="Description of the error")


class FileFormat(str, Enum):
    """
    Returned file format
    """

    txt = "txt"
    pdf = "pdf"
    any = "any"
