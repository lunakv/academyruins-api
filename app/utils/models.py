from typing import Union
from pydantic import BaseModel


class StatusModel(BaseModel):
    status: int


class Error(StatusModel):
    details: str


class Rule(StatusModel):
    ruleNumber: str
    ruleText: str


class Example(StatusModel):
    ruleNumber: str
    examples: Union[list[str], None]


class KeywordDict(StatusModel):
    keywordAbilities: list[str]
    keywordActions: list[str]
    abilityWords: list[str]

