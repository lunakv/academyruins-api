from typing import Union
from pydantic import BaseModel


class Error(BaseModel):
    detail: str


class Rule(BaseModel):
    ruleNumber: str
    ruleText: str


class RuleNav(BaseModel):
    previousRule: Union[str, None]
    nextRule: Union[str, None]


class Example(BaseModel):
    ruleNumber: str
    examples: Union[list[str], None]


class FullRule(Rule, Example):
    fragment: str
    navigation: RuleNav


class KeywordDict(BaseModel):
    keywordAbilities: list[str]
    keywordActions: list[str]
    abilityWords: list[str]


class GlossaryTerm(BaseModel):
    term: str
    definition: str


