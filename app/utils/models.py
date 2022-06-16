from typing import Union
from pydantic import BaseModel


class StatusModel(BaseModel):
    status: int


class Error(StatusModel):
    details: str


class RuleBase(BaseModel):
    ruleNumber: str
    ruleText: str


class RuleNav(BaseModel):
    previousRule: Union[str, None]
    nextRule: Union[str, None]


class FullRuleBase(RuleBase):
    examples: Union[list[str], None]
    fragment: str
    navigation: RuleNav


class Rule(StatusModel, RuleBase):
    pass


class Example(StatusModel):
    ruleNumber: str
    examples: Union[list[str], None]


class KeywordDict(StatusModel):
    keywordAbilities: list[str]
    keywordActions: list[str]
    abilityWords: list[str]

