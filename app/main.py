from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union

import re
import json
import static_paths as paths
from extract_cr import keyword_regex, keyword_action_regex

rules_dict = {}
redirect_dict = {}
with open(paths.rules_dict, 'r') as rules_file:
    rules_dict = json.load(rules_file)
with open(paths.redirects, 'r') as redirect_file:
    redirect_dict = json.load(redirect_file)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

class Rule(BaseModel):
    status: int = 200
    ruleNumber: str
    ruleText: str

class Example(BaseModel):
    status: int = 200
    ruleNumber: str
    examples: Union[list[str], None]

class KeywordList(BaseModel):
    keywordAbilities: list[str]
    keywordActions: list[str]
    abilityWords: list[str]

def get_best_keyword_subrule(rule):
    single_word_or_sentence = r'^(\w*|[^.]*\.)$'
    exceptions = ['702.57a', '702.22b']
    while re.match(single_word_or_sentence, rule['ruleText']) or rule['ruleNumber'] in exceptions:
        next_rule = rule['navigation']['nextRule']
        if not next_rule: break
        next_rule = rules_dict[next_rule]
        if re.match(r'^\d$', next_rule['fragment']): break
        rule = next_rule
    return rule

@app.get("/rule/{rule_id}", response_model=Rule, responses={
    404: {"description": "Rule was not found"},
    200: {"description": "The appropriate rule." }})
def get_rule(rule_id: str, response: Response):
    if rule_id not in rules_dict:
        response.status_code = 404
        return { 'status': 404, 'ruleNumber': rule_id, 'message': 'Rule not found' }
    
    if re.fullmatch(keyword_action_regex, rule_id):
        rule_id += 'a'
    rule = rules_dict[rule_id]
    if re.fullmatch(keyword_regex, rule_id):
        rule = get_best_keyword_subrule(rule)
    return { 'status': 200, 'ruleNumber': rule['ruleNumber'], 'ruleText': rule['ruleText'] }

@app.get("/example/{rule_id}", response_model=Example)
def get_example(rule_id:str, response: Response):
    if rule_id not in rules_dict:
        response.status_code = 404
        return { 'status': 404, 'ruleNumber': rule_id, 'message': 'Rule not found' }
    
    return { 'status': 200, 'ruleNumber': rule_id, 'examples': rules_dict[rule_id]['examples'] }

@app.get("/allrules", response_model=list[Rule])
def get_all_rules():
    return FileResponse(paths.rules_dict)

@app.get("/keywords", response_model=KeywordList)
def get_keywords():
    return FileResponse(paths.keyword_dict)

@app.get("/link/cr", status_code=307, responses={ 307: {"description": 'Redirects to an up-to-date TXT version of the Comprehensive rules.', 'content': None } })
def get_cr():
    return RedirectResponse(redirect_dict['cr'])

@app.get("/", include_in_schema=False)
def root(response: Response):
    response.status_code = 400
    return { 'status': 400, 'details': 'This is the root of the Academy Ruins API. You can find the documentation at https://api.academyruins.com/docs' }
