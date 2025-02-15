from enum import Enum

from pydantic import Field

from src.diffs.schemas import CrDiffMetadata
from src.schemas import Error, ResponseModel


class RuleError(Error):
    ruleNumber: str


class Rule(ResponseModel):
    ruleNumber: str = Field(..., description='"Number" of this rule (e.g. `"104.3a"`')
    ruleText: str = Field(..., description="Full text of the rule")


class RuleNav(ResponseModel):
    previousRule: str | None = Field(
        None, description="Number of the (sub)rule immediately preceding this one in the CR, if such a rule exists"
    )
    nextRule: str | None = Field(
        None, description="Number of the (sub)rule immediately following this one in the CR, if such a rule exists"
    )


class Example(ResponseModel):
    ruleNumber: str = Field(..., description="Number of the rule whose examples are returned")
    examples: list[str] | None = Field(
        None, description="Ordered list of examples listed under said rule, each *without* the prefix `Example: `"
    )


class FullRule(Rule, Example):
    fragment: str = Field(..., description="Part of this rule's number after the dot (e.g. `3a` for rule `104.3a`")
    navigation: RuleNav = Field(..., description="Links to neighboring rules")


class KeywordDict(ResponseModel):
    keywordAbilities: list[str] = Field(..., description="List of keyword abilities, in title case")
    keywordActions: list[str] = Field(..., description="List of keyword actions, in title case")
    abilityWords: list[str] = Field(..., description="List of ability words, in lower case")


class GlossaryTerm(ResponseModel):
    term: str = Field(..., description="The actual name of this glossary entry")
    definition: str = Field(..., description="The contents of this glossary entry")


class ToCSubsection(ResponseModel):
    number: int
    title: str


class ToCSection(ResponseModel):
    number: int
    title: str
    subsections: list[ToCSubsection]


class TraceItemAction(str, Enum):
    created = "created"
    edited = "edited"
    replaced = "replaced"
    moved = "moved"


class TraceDiffRule(ResponseModel):
    ruleNum: str = Field(..., alias="ruleNumber")
    ruleText: str | None = Field(None)


class TraceItem(ResponseModel):
    action: TraceItemAction
    old: TraceDiffRule | None = None
    new: TraceDiffRule
    diff: CrDiffMetadata


class Trace(ResponseModel):
    ruleNumber: str = Field(..., description="Number of the rule for which the trace was generated.")
    items: list[TraceItem] = Field(..., description="List of changes made to the rule, in reverse chronological order.")
