import datetime
from enum import Enum

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass


class Config:
    orm_mode = True
    allow_population_by_field_name = True


@dataclass
class Error(BaseModel):
    detail: str = Field(..., description="Description of the error")


@dataclass(config=Config)
class Rule:
    ruleNumber: str = Field(..., description='"Number" of this rule (e.g. `"104.3a"`')
    ruleText: str = Field(..., description="Full text of the rule")


@dataclass(config=Config)
class RuleNav:
    previousRule: str | None = Field(
        None, description="Number of the (sub)rule immediately preceding this one in the CR, if such a rule exists"
    )
    nextRule: str | None = Field(
        None, description="Number of the (sub)rule immediately following this one in the CR, if such a rule exists"
    )


@dataclass(config=Config)
class Example:
    ruleNumber: str = Field(..., description="Number of the rule whose examples are returned")
    examples: list[str] | None = Field(
        None, description="Ordered list of examples listed under said rule, each *without* the prefix `Example: `"
    )


class FullRule(Rule, Example):
    fragment: str = Field(..., description="Part of this rule's number after the dot (e.g. `3a` for rule `104.3a`")
    navigation: RuleNav = Field(..., description="Links to neighboring rules")


@dataclass(config=Config)
class KeywordDict:
    keywordAbilities: list[str] = Field(..., description="List of keyword abilities, in title case")
    keywordActions: list[str] = Field(..., description="List of keyword actions, in title case")
    abilityWords: list[str] = Field(..., description="List of ability words, in lower case")


@dataclass(config=Config)
class GlossaryTerm:
    term: str = Field(..., description="The actual name of this glossary entry")
    definition: str = Field(..., description="The contents of this glossary entry")


@dataclass(config=Config)
class ToCSubsection:
    number: int
    title: str


@dataclass(config=Config)
class ToCSection:
    number: int
    title: str
    subsections: list[ToCSubsection]


@dataclass(config=Config)
class CRDiffRule:
    ruleNum: str = Field(..., alias="ruleNumber")
    ruleText: str = Field(...)


@dataclass(config=Config)
class CRDiffItem(BaseModel):
    old: CRDiffRule | None
    new: CRDiffRule | None


@dataclass(config=Config)
class CRMoveItem:
    from_number: str = Field(..., alias="from")
    to_number: str = Field(..., alias="to")


@dataclass(config=Config)
class CRDiffMetadata:
    source_set: str = Field(..., alias="sourceSet")
    source_code: str = Field(..., alias="sourceCode")
    dest_set: str = Field(..., alias="destSet")
    dest_code: str = Field(..., alias="destCode")


@dataclass(config=Config)
class CRDiffNavigation:
    prev_source_code: str | None = Field(None, alias="prevSourceCode")
    next_dest_code: str | None = Field(None, alias="nextDestCode")


@dataclass(config=Config)
class CRDiff(CRDiffMetadata):
    creation_day: datetime.date = Field(..., alias="creationDay")
    changes: list[CRDiffItem] = Field(...)
    moves: list[CRMoveItem] = Field(description="List of moved rules")
    nav: CRDiffNavigation | None = Field(description="Navigational information.")


@dataclass(config=Config)
class PendingCRDiff:
    changes: list[CRDiffItem]
    source_set: str = Field(..., alias="sourceSet")


class PendingCRDiffResponse(BaseModel):
    data: PendingCRDiff


@dataclass(config=Config)
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
    content: str | None = Field(
        None, description="The text inside this subsection (without the title or either number)"
    )


@dataclass(config=Config)
class Mtr:
    effective_date: datetime.date = Field(
        ..., description="The day when this document started being applicable", alias="effectiveDate"
    )
    sections: list[MtrChunk] = Field(
        ...,
        description="Ordered list of all (sub)sections within this document, excluding any appendices",
        alias="content",
    )


@dataclass(config=Config)
class MtrDiffItem:
    old: MtrChunk | None
    new: MtrChunk | None


@dataclass(config=Config)
class MtrDiff:
    effective_date: datetime.date = Field(
        ..., description="Effective date of the “new” document of this diff", alias="effectiveDate"
    )
    changes: list[MtrDiffItem] = Field(..., description="Ordered list of changes")


@dataclass(config=Config)
class PolicyMetadataItem:
    creation_day: datetime.date = Field(..., alias="creationDay")


@dataclass(config=Config)
class PolicyMetadata:
    data: list[PolicyMetadataItem]


@dataclass(config=Config)
class MtrDiffMetadataItem:
    effective_date: datetime.date = Field(..., alias="effectiveDate")


class TraceItemAction(str, Enum):
    created = "created"
    edited = "edited"
    replaced = "replaced"
    moved = "moved"


@dataclass(config=Config)
class DiffSetCodes:
    sourceCode: str
    destCode: str


@dataclass(config=Config)
class TraceDiffRule:
    ruleNum: str = Field(..., alias="ruleNumber")
    ruleText: str | None = Field(None)


@dataclass(config=Config)
class TraceItem:
    action: TraceItemAction
    old: TraceDiffRule | None
    new: TraceDiffRule
    diff: CRDiffMetadata
