from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union
from thefuzz import fuzz
from thefuzz import process

import re
import json
import static_paths as paths
from extract_cr import keyword_regex, keyword_action_regex

with open(paths.rules_dict, 'r') as rules_file:
    rules_dict = json.load(rules_file)
with open(paths.redirects, 'r') as redirect_file:
    redirect_dict = json.load(redirect_file)
with open(paths.glossary_dict, 'r') as glossary_file:
    glossary_dict = json.load(glossary_file)
with open(paths.unofficial_glossary_dict, 'r') as un_gloss_file:
    unofficial_glossary_dict = json.load(un_gloss_file)

glossary_searches = {}
all_glossary_searches = {}
splits = []
for key in glossary_dict:
    search_term = key.replace(' (obsolete)', '')
    glossary_searches[search_term] = (key, glossary_dict)
    search_split = search_term.split(', ')
    if len(search_split) > 1:
        for elem in search_split:
            splits.append((elem, key))
for split in splits:
    if split[0] not in glossary_dict:
        glossary_searches[split[0]] = (split[1], glossary_dict)

all_glossary_searches = glossary_searches.copy()
for key in unofficial_glossary_dict:
    all_glossary_searches[key] = (key, unofficial_glossary_dict)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)


class Error(BaseModel):
    status: int
    details: str


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
    # is just rule definition (ends with a number) - we want subrules
    definition = r'.*\d$'

    def should_skip(subrule):
        # is just a single sentence (only one comma) and includes "is a(n)"
        single_sentence = r'^([^.]*\bis an?\b[^.]*\.)$'
        # should be skipped because reasons
        exceptions = ['702.57a', '702.22b']
        return re.match(single_sentence, subrule['ruleText']) or re.match(definition, subrule['ruleNumber']) or subrule[
            'ruleNumber'] in exceptions

    while should_skip(rule):
        next_rule = rule['navigation']['nextRule']
        if not next_rule:
            break
        next_rule = rules_dict[next_rule]
        if re.match(definition, next_rule['ruleNumber']):
            break
        rule = next_rule
    return rule


@app.get("/rule/{rule_id}", response_model=Union[Rule, Error], responses={
    404: {"description": "Rule was not found", "model": Error},
    200: {"description": "The appropriate rule."}})
def get_rule(rule_id: str, response: Response):
    if rule_id not in rules_dict:
        response.status_code = 404
        return {'status': 404, 'ruleNumber': rule_id, 'details': 'Rule not found'}

    if re.fullmatch(keyword_action_regex, rule_id):
        rule_id += 'a'
    rule = rules_dict[rule_id]
    if re.fullmatch(keyword_regex, rule_id):
        print('matches', rule_id)
        rule = get_best_keyword_subrule(rule)
    return {'status': 200, 'ruleNumber': rule['ruleNumber'], 'ruleText': rule['ruleText']}


@app.get("/example/{rule_id}", response_model=Union[Example, Error])
def get_example(rule_id: str, response: Response):
    if rule_id not in rules_dict:
        response.status_code = 404
        return {'status': 404, 'details': 'Rule not found'}

    return {'status': 200, 'ruleNumber': rule_id, 'examples': rules_dict[rule_id]['examples']}


@app.get("/allrules", response_model=list[Rule])
def get_all_rules():
    return FileResponse(paths.rules_dict)


@app.get("/keywords", response_model=KeywordList)
def get_keywords():
    return FileResponse(paths.keyword_dict)


@app.get("/link/cr", status_code=307, responses={
    307: {"description": 'Redirects to an up-to-date TXT version of the Comprehensive rules.', 'content': None}})
def get_cr():
    return RedirectResponse(redirect_dict['cr'])


@app.get("/glossary")
def get_glossary():
    return FileResponse(paths.glossary_dict)


@app.get("/glossary/{term}")
def get_glossary_term(term: str, response: Response):
    choice = process.extractOne(term, all_glossary_searches.keys(), scorer=fuzz.token_sort_ratio)
    if choice[1] < 60:
        response.status_code = 404
        return {"status": 404, "details": "Entry not found."}

    gloss_key, dictionary = all_glossary_searches[choice[0]]
    entry = dictionary[gloss_key]
    return {"status": 200, "term": entry['term'], 'definition': entry['definition']}


@app.get("/", include_in_schema=False)
def root(response: Response):
    response.status_code = 400
    return {'status': 400,
            'details': 'This is the root of the Academy Ruins API. You can find the documentation at '
                       'https://api.academyruins.com/docs'}
