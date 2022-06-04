from fastapi import APIRouter, Response
from fastapi.responses import FileResponse
from typing import Union

from ..parsing.keyword_def import get_best_rule
from ..utils.models import RuleResponse, ErrorResponse, ExampleResponse, KeywordDictResponse
from ..resources.cache import RulesCache
from ..resources import static_paths as paths

router = APIRouter()
rules = RulesCache()


@router.get("/rule/{rule_id}", response_model=Union[RuleResponse, ErrorResponse], responses={
    404: {"description": "Rule was not found", "model": ErrorResponse},
    200: {"description": "The appropriate rule."}})
def get_rule(rule_id: str, response: Response):
    if not rules.has(rule_id):
        response.status_code = 404
        return {'status': 404, 'ruleNumber': rule_id, 'details': 'Rule not found'}

    rule = get_best_rule(rule_id)
    return {'status': 200, 'ruleNumber': rule['ruleNumber'], 'ruleText': rule['ruleText']}


@router.get("/example/{rule_id}", response_model=Union[ExampleResponse, ErrorResponse])
def get_example(rule_id: str, response: Response):
    if not rules.has(rule_id):
        response.status_code = 404
        return {'status': 404, 'details': 'Rule not found'}

    return {'status': 200, 'ruleNumber': rule_id, 'examples': rules.get(rule_id)['examples']}


@router.get("/allrules", response_model=list[RuleResponse])
def get_all_rules():
    return FileResponse(paths.rules_dict)


@router.get("/keywords", response_model=KeywordDictResponse)
def get_keywords():
    return FileResponse(paths.keyword_dict)



