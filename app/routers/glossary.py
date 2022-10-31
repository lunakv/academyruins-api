from typing import Union

from fastapi import APIRouter, Response, Path, Query
from fastapi.responses import FileResponse
from thefuzz import fuzz
from thefuzz import process

from ..resources import static_paths as paths
from ..resources.cache import GlossaryCache
from ..utils.models import GlossaryTerm, Error

router = APIRouter(tags=["Rules"])
glossary = GlossaryCache()


@router.get("/", summary="Glossary", response_model=dict[str, GlossaryTerm])
def get_glossary():
    """
    Get the full parsed glossary. Returns a dictionary of terms, where keys are lower-cased names of each glossary
    entry and the values contain the actual name of the entry and its content
    """
    return FileResponse(paths.glossary_dict)


@router.get(
    "/{term}",
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
