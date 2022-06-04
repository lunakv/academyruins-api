from typing import Union
from pydantic import BaseModel


class BaseResponse(BaseModel):
    status: int


class ErrorResponse(BaseResponse):
    details: str


class RuleResponse(BaseResponse):
    ruleNumber: str
    ruleText: str


class ExampleResponse(BaseResponse):
    ruleNumber: str
    examples: Union[list[str], None]


class KeywordDictResponse(BaseResponse):
    keywordAbilities: list[str]
    keywordActions: list[str]
    abilityWords: list[str]

