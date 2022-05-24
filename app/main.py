from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import json
import static_paths as paths

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

@app.get("/rule/{rule_id}")
def get_rule(rule_id: str, response: Response):
    if rule_id not in rules_dict:
        response.status_code = 404
        return { 'status': 404, 'ruleNumber': rule_id, 'message': 'Rule not found' }
    
    return { 'status': 200, 'ruleNumber': rule_id, 'ruleText': rules_dict[rule_id]['ruleText'] }

@app.get("/example/{rule_id}")
def get_example(rule_id:str, response: Response):
    if rule_id not in rules_dict:
        response.status_code = 404
        return { 'status': 404, 'ruleNumber': rule_id, 'message': 'Rule not found' }
    
    return { 'status': 200, 'ruleNumber': rule_id, 'examples': rules_dict[rule_id]['examples'] }

@app.get("/allrules")
def get_all_rules():
    return FileResponse(paths.rules_dict)

@app.get("/keywords")
def get_keywords():
    return FileResponse(paths.keyword_dict)

@app.get("/link/cr")
def get_cr():
    return RedirectResponse(redirect_dict['cr'])
