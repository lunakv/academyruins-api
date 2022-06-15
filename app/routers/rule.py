from fastapi import APIRouter, Response
from fastapi.responses import FileResponse
from typing import Union

from ..parsing.keyword_def import get_best_rule
from ..utils.models import Rule, Error, Example, KeywordDict
from ..resources.cache import RulesCache
from ..resources import static_paths as paths
from ..utils.responses import StatusResponse, ErrorResponse

router = APIRouter()
rules = RulesCache()


@router.get("/rule/{rule_id}", response_model=Union[Rule, Error], responses={
    404: {"description": "Rule was not found", "model": Error},
    200: {"description": "The appropriate rule."}})
def get_rule(rule_id: str):
    if not rules.has(rule_id):
        return ErrorResponse('Rule not found', 404, {'ruleNumber': rule_id})

    rule = get_best_rule(rule_id)
    return StatusResponse({'ruleNumber': rule['ruleNumber'], 'ruleText': rule['ruleText']})


@router.get("/example/{rule_id}", response_model=Union[Example, Error])
def get_example(rule_id: str):
    if not rules.has(rule_id):
        return ErrorResponse('Rule not found', status_code=404)

    return StatusResponse({'ruleNumber': rule_id, 'examples': rules.get(rule_id)['examples']})


@router.get("/allrules", response_model=list[Rule])
def get_all_rules():
    return FileResponse(paths.rules_dict)


@router.get("/keywords", response_model=KeywordDict)
def get_keywords():
    return FileResponse(paths.keyword_dict)



