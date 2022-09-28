import datetime
from typing import Union

import pydantic
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


class CRDiffRule(BaseModel):
    ruleNum: str
    ruleText: str


class CRDiffItem(BaseModel):
    old: CRDiffRule | None
    new: CRDiffRule | None


class CRDiffNavItem(BaseModel):
    old: str
    new: str


class CRDiffNav(BaseModel):
    prev: CRDiffNavItem | None
    next: CRDiffNavItem | None


class CRDiff(BaseModel):
    creation_day: datetime.date
    changes: list[CRDiffItem]
    source_set: str
    dest_set: str
    nav: CRDiffNav


class PendingCRDiff(BaseModel):
    changes: list[CRDiffItem]
    source_set: str


class PendingCRDiffResponse(BaseModel):
    data: PendingCRDiff
