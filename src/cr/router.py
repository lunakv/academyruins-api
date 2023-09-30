import re
from typing import Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from thefuzz import fuzz, process

from cr import schemas, service
from db import get_db
from openapi.no422 import no422
from openapi.strings import crTag, filesTag
from resources import static_paths as paths
from resources.cache import GlossaryCache
from schemas import Error, FileFormat
from utils.keyword_def import get_best_rule

router = APIRouter(tags=[crTag.name])
glossary = GlossaryCache()


@router.get("/cr", summary="All Rules", response_model=Dict[str, schemas.FullRule])
def get_all_rules(db: Session = Depends(get_db)):
    """
    Get a dictionary of all rules, keyed by their rule numbers.

    Each value contains the rule's number, text, and list of examples (may be null), as well as a `fragment`,
    describing the part of the rule number after a comma, and `navigation`, which contains numbers of the previous
    and next rule in the document.
    """
    rules = service.get_latest_cr(db)
    return rules.data


@router.get("/cr/keywords", summary="Keywords", response_model=schemas.KeywordDict)
def get_keywords():
    """
    Get a list of all keywords

    Returns an object with a list of all keyword abilities, keyword actions, and ability words. Variants of keyword
    abilities (e.g. "partner with" or "friends forever") are not included. Keyword abilities and keyword actions are
    kept in their natural case, ability words are all lower-cased.
    """
    return FileResponse(paths.keyword_dict)


@router.get("/cr/glossary", summary="Glossary", response_model=dict[str, schemas.GlossaryTerm])
def get_glossary():
    """
    Get the full parsed glossary. Returns a dictionary of terms, where keys are lower-cased names of each glossary
    entry and the values contain the actual name of the entry and its content
    """
    return FileResponse(paths.glossary_dict)


@router.get("/cr/toc", summary="Table of Contents", response_model=list[schemas.ToCSection])
def get_table_of_contents(db: Session = Depends(get_db)):
    """
    Get the CR table of contents. The table of contents is an ordered list of sections. Each section has a number
    (`1`) and a title (`"Game Concepts"`), as well as a list of subsections. Each subsection has a number (`105`) and
    a title ( `"Colors"`).

    The table of contents includes only numbered sections in the CR. That means it doesn't contain entries for the
    introduction, the glossary, or the credits.
    """
    cr = service.get_latest_cr(db)
    return cr.toc


@router.get(
    "/cr/glossary/{term}",
    summary="Glossary Term",
    response_model=Union[schemas.GlossaryTerm, Error],
    responses={200: {"model": schemas.GlossaryTerm}, 404: {"model": Error}},
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


@router.get("/cr/unofficial-glossary", summary="Unofficial Glossary", response_model=dict[str, schemas.GlossaryTerm])
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
    "/cr/{rule_id}",
    summary="Rule",
    response_model=Union[schemas.Rule, schemas.RuleError],
    responses={
        404: {"description": "Rule was not found.", "model": schemas.RuleError},
        200: {"description": "The appropriate rule.", "model": schemas.Rule},
    },
)
def get_rule(
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
    rule = service.get_rule(db, rule_id)
    if not rule:
        response.status_code = 404
        return {"detail": "Rule not found", "ruleNumber": rule_id}

    if not exact_match:
        rule = get_best_rule(db, rule_id)
    return {"ruleNumber": rule["ruleNumber"], "ruleText": rule["ruleText"]}


@router.get(
    "/cr/example/{rule_id}",
    summary="Examples",
    response_model=Union[schemas.RuleError, schemas.Example],
    responses={
        404: {"description": "Rule was not found", "model": schemas.RuleError},
        200: {"description": "Examples for the given rule", "model": schemas.Example},
    },
)
@no422
def get_examples(
    response: Response,
    rule_id: str = Path(description="Number of the rule you want to get"),
    db: Session = Depends(get_db),
):
    """
    Get all examples associated with a rule. Returns an array of examples, each *without* the prefix "Example: "

    If the specified rule exists, but has no associated examples, a 200 response is returned with a null `examples`
    field
    """
    rule = service.get_rule(db, rule_id)
    if not rule:
        response.status_code = 404
        return {"detail": "Rule not found", "ruleNumber": rule_id}

    return {"ruleNumber": rule_id, "examples": rule["examples"]}


@router.get(
    "/cr/trace/{rule_id}",
    summary="Trace",
    response_model=list[schemas.TraceItem],
    responses={
        404: {"description": "Rule was not found", "model": schemas.RuleError},
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
    current_cr = service.get_latest_cr(db)
    current_rule = current_cr.data.get(rule_id)
    if not current_rule:
        raise HTTPException(404, {"detail": "Rule not found.", "ruleNumber": rule_id})

    trace = service.get_cr_trace(db, rule_id)
    return trace


@router.get("/file/cr", summary="Raw Latest CR", tags=[filesTag.name])
def raw_latest_cr(db: Session = Depends(get_db)):
    """
    Returns the raw text of the latest CR. This route is similar to the `/link/cr` route, with three main differences:
    1. This route returns a response directly rather than a redirect to WotC servers.
    2. The response of this route is guaranteed to be in UTF-8 (see also
    [Response Encoding and Formatting](#section/Response-Encoding-and-Formatting)).
    3. This route updates only once the latest CR diff is prepared and published, so it may be slightly delayed compared
    to the redirect.

    If you need the data directly from WotC and/or want to get updates as fast as possible, use `/link/cr`. If you don't
    mind possibly waiting a short while, and you don't want to deal with manually figuring out the response format, this
    route may be better suited for you.
    """
    cr = service.get_latest_cr(db)
    file_name = cr.file_name
    path = "src/static/raw_docs/cr/" + file_name  # FIXME hardcoded path
    return FileResponse(path)


@router.get(
    "/file/cr/{set_code}",
    summary="Raw CR by Set Code",
    responses={404: {"description": "CR for the specified set code not found", "model": Error}},
    tags=[filesTag.name],
)
def raw_cr_by_set_code(
    response: Response,
    set_code: str = Path(description="Code of the requested set (case insensitive)", min_length=3, max_length=5),
    format: Union[FileFormat, None] = Query(default=FileFormat.any),
    db: Session = Depends(get_db),
):
    """
    Returns a raw file of the CR for the specified set. Most of the results will be UTF-8 encoded TXT files,
    but for some historic sets only a PDF version of the rulebook is available. To ensure only a specific format is
    returned, set the `format` query parameter. If set to a value besides `any`, files of other formats are treated
    as though they don't exist.
    """
    cr = service.get_cr_by_set_code(db, set_code.upper())
    if not cr:
        response.status_code = 404
        return {"detail": "CR not available for this set"}

    if format != FileFormat.any and not re.search(r"\." + format + "$", cr.file_name):
        response.status_code = 404
        return {"detail": "CR for this set not available in specified format"}

    path = "src/static/raw_docs/cr/" + cr.file_name  # FIXME hardcoded path
    return FileResponse(path)


@router.get("/metadata/cr", include_in_schema=False)
def cr_metadata(db: Session = Depends(get_db)):
    meta = service.get_cr_metadata(db)

    if meta:
        ret = [{"creationDay": d, "setCode": c, "setName": n} for d, c, n in meta]
    else:
        ret = []

    return {"data": ret}
