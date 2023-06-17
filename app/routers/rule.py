from typing import Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from thefuzz import fuzz, process

from app.openapi.no422 import no422

from ..database import operations as ops
from ..database.db import get_db
from ..resources import static_paths as paths
from ..resources.cache import GlossaryCache
from ..utils.keyword_def import get_best_rule
from ..utils.response_models import Error, Example, FullRule, GlossaryTerm, KeywordDict, Rule, ToCSection, TraceItem
from ..utils.trace import create_cr_trace

router = APIRouter()
glossary = GlossaryCache()


class RuleError(Error):
    ruleNumber: str


@router.get("", summary="All Rules", response_model=Dict[str, FullRule])
async def get_all_rules(db: Session = Depends(get_db)):
    """
    Get a dictionary of all rules, keyed by their rule numbers.

    Each value contains the rule's number, text, and list of examples (may be null), as well as a `fragment`,
    describing the part of the rule number after a comma, and `navigation`, which contains numbers of the previous
    and next rule in the document.
    """
    rules = ops.get_current_cr(db)
    return rules.data


@router.get("/keywords", summary="Keywords", response_model=KeywordDict)
def get_keywords():
    """
    Get a list of all keywords

    Returns an object with a list of all keyword abilities, keyword actions, and ability words. Variants of keyword
Openapi refactorOpenapi refactor    abilities (e.g. "partner with" or "friends forever") are not included. Keyword abilities and keyword actions are
    kept in their natural case, ability words are all lower-cased.
    """
    return FileResponse(paths.keyword_dict)


@router.get("/glossary", summary="Glossary", response_model=dict[str, GlossaryTerm])
def get_glossary():
    """
    Get the full parsed glossary. Returns a dictionary of terms, where keys are lower-cased names of each glossary
    entry and the values contain the actual name of the entry and its content
    """
    return FileResponse(paths.glossary_dict)


@router.get("/toc", summary="Table of Contents", response_model=list[ToCSection])
def get_table_of_contents(db: Session = Depends(get_db)):
    """
    Get the CR table of contents. The table of contents is an ordered list of sections. Each section has a number
    (`1`) and a title (`"Game Concepts"`), as well as a list of subsections. Each subsection has a number (`105`) and
    a title ( `"Colors"`).

    The table of contents includes only numbered sections in the CR. That means it doesn't contain entries for the
    introduction, the glossary, or the credits.
    """
    cr = ops.get_current_cr(db)
    return cr.toc


@router.get(
    "/glossary/{term}",
    summary="Glossary Term",
    response_model=Union[GlossaryTerm, Error],
    responses={200: {"model": GlossaryTerm}, 404: {"model": Error}},
)
def get_glossary_term(
    response: Response,
    term: str = Path(description="Searched term in the glossary"),
    exact: bool = Query(default=False, description="Force exact match (case-insensitive)"),
    unofficial: bool = Query(default=True, description="Include terms from the unofficial glossary"),
):
    """
    Get a single glossary term. Uses fuzzy matching to try and find the best match for the requested term,
    and assuming it finds a close enough match, returns it.

    You can use the `exact` query parameter to disable fuzzy matching and return only an exact match (ignoring case).
    The `unofficial` query parameter can be used to specify whether terms from the unofficial glossary are also
    included in the possible results.

    A successful response includes the actual name of the glossary entry and its content.
    """
    term = term.lower()

    if unofficial:
        searches = glossary.all_searches()
        getter = glossary.get_any
    else:
        searches = glossary.official_searches()
        getter = glossary.get

    if exact:
        entry = getter(term)
        found = entry is not None
    else:
        choice = process.extractOne(term, searches.keys(), scorer=fuzz.token_sort_ratio)
        found = choice[1] >= 60
        gloss_key = searches[choice[0]]
        entry = getter(gloss_key)

    if not found:
        response.status_code = 404
        return {"detail": "Entry not found."}

    return {"term": entry["term"], "definition": entry["definition"]}


@router.get("/unofficial-glossary", summary="Unofficial Glossary", response_model=dict[str, GlossaryTerm])
def get_unofficial():
    """
    Get the full unofficial glossary.

    There are terms that users might search for, but that don't have entries in the official CR glossary. Notably,
    individual ability words aren't referenced there. The API provides unofficial descriptions for such terms that
    can be returned by glossary searches.

    The dictionary has the same format as the official glossary. The definition of each entry in the unofficial
    glossary ends with the string `[Unofficial]`.
    """
    return FileResponse(path=paths.unofficial_glossary_dict)


@router.get(
    "/{rule_id}",
    summary="Rule",
    response_model=Union[Rule, RuleError],
    responses={
        404: {"description": "Rule was not found.", "model": RuleError},
        200: {"description": "The appropriate rule.", "model": Rule},
    },
)
async def get_rule(
    response: Response,
    rule_id: str = Path(description="Number of the rule you want to get"),
    exact_match: bool = Query(default=False, description="Enforce exact match."),
    db: Session = Depends(get_db),
):
    """
    Get the current text of a specific rule.

    Because this end point was designed to be human-friendly, responses for rules in the Keyword and Keyword Action
    sections may return a different rule than what was queried.

    *Example:* A user looking for the definition of defender might search for rule 702.3 (perhaps due to a glossary
    reference). That rule however simply says "Defender", which isn't particularly useful. To try and give a useful
    response, the API will look into the subrules to find one that actually provides a definition of that keyword.
    702.3a simply states defender is a static ability, which doesn't help much either, so the text of 702.3b will be
    what's actually returned by the call.

    To check what rule was actually returned, use the `ruleNumber` field of the response. To disable this behavior
    entirely, set the `exact_match` query parameter to `true`.
    """
    rule = ops.get_rule(db, rule_id)
    if not rule:
        response.status_code = 404
        return {"detail": "Rule not found", "ruleNumber": rule_id}

    if not exact_match:
        rule = await get_best_rule(db, rule_id)
    return {"ruleNumber": rule["ruleNumber"], "ruleText": rule["ruleText"]}


@router.get(
    "/example/{rule_id}",
    summary="Examples",
    response_model=Union[RuleError, Example],
    responses={
        404: {"description": "Rule was not found", "model": RuleError},
        200: {"description": "Examples for the given rule", "model": Example},
    },
)
@no422
async def get_examples(
    response: Response,
    rule_id: str = Path(description="Number of the rule you want to get"),
    db: Session = Depends(get_db),
):
    """
    Get all examples associated with a rule. Returns an array of examples, each *without* the prefix "Example: "

    If the specified rule exists, but has no associated examples, a 200 response is returned with a null `examples`
    field
    """
    rule = ops.get_rule(db, rule_id)
    if not rule:
        response.status_code = 404
        return {"detail": "Rule not found", "ruleNumber": rule_id}

    return {"ruleNumber": rule_id, "examples": rule["examples"]}


@router.get(
    "/trace/{rule_id}",
    summary="Trace",
    response_model=list[TraceItem],
    responses={
        404: {"description": "Rule was not found", "model": RuleError},
        200: {"description": "Full trace for the requested rule"},
    },
)
@no422
def get_trace(
    rule_id: str = Path(description="Current number of the rule you want to trace."),
    db: Session = Depends(get_db),
):
    """
    Get the trace of a rule.

    Given a current rule, its trace is a list (in reverse chronological order) of all changes that rule went through.
    Each change can correspond to one of several actions (denoted by the `action` field):
    - `created`: The rule was first created.
    - `moved`: The rule changed numbers, but its text staid the same.
    - `edited`: The rule changed text, but its number staid the same.
    - `replaced`: Both the rule number and the rule text changed.

    For all actions except `moved`, the change has `old` and `new` fields with the same format as
    those returned in the CR diffs. For `moved`, the `ruleText` of those fields is missing.

    Each change also contains a `diff` field containing information about the sets that are in the diff containing
    that change.
    """
    current_cr = ops.get_current_cr(db)
    current_rule = current_cr.data.get(rule_id)
    if not current_rule:
        raise HTTPException(404, {"detail": "Rule not found.", "ruleNumber": rule_id})

    return create_cr_trace(db, rule_id)
