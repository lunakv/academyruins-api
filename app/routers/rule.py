from fastapi import APIRouter, Response
from fastapi.responses import FileResponse
from typing import Union, Dict

from ..parsing.keyword_def import get_best_rule
from ..utils.models import Rule, FullRuleBase, Error, Example, KeywordDict
from ..resources import static_paths as paths
from ..utils import db
from ..utils.responses import StatusResponse, ErrorResponse

router = APIRouter()


@router.get("/rule/{rule_id}", response_model=Union[Rule, Error], responses={
    404: {"description": "Rule was not found", "model": Error},
    200: {"description": "The appropriate rule."}})
async def get_rule(rule_id: str):
    rule = await db.fetch_rule(rule_id)
    if not rule:
        return ErrorResponse('Rule not found', 404, {'ruleNumber': rule_id})

    rule = await get_best_rule(rule_id)
    return StatusResponse({'ruleNumber': rule['ruleNumber'], 'ruleText': rule['ruleText']})


@router.get("/example/{rule_id}", response_model=Union[Example, Error])
async def get_example(rule_id: str):
    rule = await db.fetch_rule(rule_id)
    if not rule:
        return ErrorResponse('Rule not found', status_code=404)

    return StatusResponse({'ruleNumber': rule_id, 'examples': rule['examples']})


@router.get("/allrules", response_model=Dict[str, FullRuleBase])
async def get_all_rules():
    return await db.fetch_all_rules()


@router.get("/keywords", response_model=KeywordDict)
def get_keywords():
    return FileResponse(paths.keyword_dict)



