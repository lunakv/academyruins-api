import datetime
from typing import Union

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass


class Error(BaseModel):
    detail: str = Field(..., description="Description of the error")


class Rule(BaseModel):
    ruleNumber: str = Field(..., description='"Number" of this rule (e.g. `"104.3a"`')
    ruleText: str = Field(..., description="Full text of the rule")


class RuleNav(BaseModel):
    previousRule: str | None = Field(
        None, description="Number of the (sub)rule immediately preceding this one in the CR, if such a rule exists"
    )
    nextRule: str | None = Field(
        None, description="Number of the (sub)rule immediately following this one in the CR, if such a rule exists"
    )


class Example(BaseModel):
    ruleNumber: str = Field(..., description="Number of the rule whose examples are returned")
    examples: list[str] | None = Field(
        None, description="Ordered list of examples listed under said rule, each *without* the prefix `Example: `"
    )


class FullRule(Rule, Example):
    fragment: str = Field(..., description="Part of this rule's number after the dot (e.g. `3a` for rule `104.3a`")
    navigation: RuleNav = Field(..., description="Links to neighboring rules")


class KeywordDict(BaseModel):
    keywordAbilities: list[str] = Field(..., description="List of keyword abilities, in title case")
    keywordActions: list[str] = Field(..., description="List of keyword actions, in title case")
    abilityWords: list[str] = Field(..., description="List of ability words, in lower case")


class GlossaryTerm(BaseModel):
    term: str = Field(..., description="The actual name of this glossary entry")
    definition: str = Field(..., description="The contents of this glossary entry")


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


@dataclass
class MtrChunk:
    section: int | None = Field(
        None, description="Number of the section this subsection is under (e.g. `2` for subsection 2.3)"
    )
    subsection: int | None = Field(
        None, description="Number of this (sub)section within its section (e.g. `3` for subsection 2.3)"
    )
    title: str = Field(
        ..., description="Title of this subsection, without either of its numbers (e.g. `Tournament Mechanics`)"
    )
    content: str | None = Field(..., description="The text inside this subsection (without the title or either number)")

@dataclass
class Mtr:
    effective_date: datetime.date = Field(..., description="The day when this document started being applicable")
    content: list[MtrChunk] = Field(
        ..., description="Ordered list of all (sub)sections within this document, excluding any appendices"
    )
