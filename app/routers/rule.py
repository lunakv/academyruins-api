from fastapi import APIRouter, Response, Path, Query, Depends
from fastapi.responses import FileResponse
from typing import Union, Dict
from sqlalchemy.orm import Session

from ..database import operations as ops
from ..database.db import get_db
from ..parsing.keyword_def import get_best_rule
from ..utils.models import Rule, Error, Example, KeywordDict, FullRule
from ..resources import static_paths as paths
from ..utils.remove422 import no422

router = APIRouter()


class RuleError(Error):
    ruleNumber: str


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


@router.get("/", summary="All Rules", response_model=Dict[str, FullRule])
async def get_all_rules(db: Session = Depends(get_db)):
    """
    Get a dictionary of all rules, keyed by their rule numbers.

    Each value contains the rule's number, text, and list of examples (may be null), as well as a `fragment`,
    describing the part of the rule number after a comma, and `navigation`, which contains numbers of the previous
    and next rule in the document.
    """
    rules = ops.get_current_cr(db)
    return rules


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


@router.get("/keywords", summary="Keywords", response_model=KeywordDict)
def get_keywords():
    """
    Get a list of all keywords

    Returns an object with a list of all keyword abilities, keyword actions, and ability words. Variants of keyword
    abilities (e.g. "partner with" or "friends forever") are not included. Keyword abilities and keyword actions are
    kept in their natural case, ability words are all lower-cased.
    """
    return FileResponse(paths.keyword_dict)
