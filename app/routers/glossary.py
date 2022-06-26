from typing import Union

from fastapi import APIRouter, Response, Path
from fastapi.responses import FileResponse
from thefuzz import fuzz
from thefuzz import process
from ..resources import static_paths as paths
from ..resources.cache import GlossaryCache
from ..utils.models import GlossaryTerm, Error
from ..utils.remove422 import no422

router = APIRouter(tags=["Rules"])
glossary = GlossaryCache()


@router.get("/", response_model=dict[str, GlossaryTerm])
def get_glossary():
    """
    Get the full parsed glossary. Returns a dictionary of terms, where keys are lower-cased names of each glossary
    entry and the values contain the actual name of the entry and its content
    """
    return FileResponse(paths.glossary_dict)


@router.get(
    "/{term}",
    response_model=Union[GlossaryTerm, Error],
    responses={200: {"model": GlossaryTerm}, 404: {"model": Error}},
)
@no422
def get_glossary_term(response: Response, term: str = Path(description="Searched term in the glossary")):
    """
    Get a single glossary term. Uses fuzzy matching to try and find the best match for the requested term,
    and assuming it finds a close enough match, returns it.

    A successful response includes the actual name of the glossary entry and its content.
    """
    all_searches = glossary.all_searches()
    choice = process.extractOne(term, all_searches.keys(), scorer=fuzz.token_sort_ratio)
    if choice[1] < 60:
        response.status_code = 404
        return {"detail": "Entry not found."}

    gloss_key = all_searches[choice[0]]
    entry = glossary.get_any(gloss_key)
    return {"term": entry["term"], "definition": entry["definition"]}
