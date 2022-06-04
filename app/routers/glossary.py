from fastapi import APIRouter, Response
from fastapi.responses import FileResponse
from thefuzz import fuzz
from thefuzz import process
from ..resources import static_paths as paths
from ..resources.cache import GlossaryCache

router = APIRouter()
glossary = GlossaryCache()


@router.get("/")
def get_glossary():
    return FileResponse(paths.glossary_dict)


@router.get("/{term}")
def get_glossary_term(term: str, response: Response):
    all_searches = glossary.all_searches()
    choice = process.extractOne(term, all_searches.keys(), scorer=fuzz.token_sort_ratio)
    if choice[1] < 60:
        response.status_code = 404
        return {"status": 404, "details": "Entry not found."}

    gloss_key = all_searches[choice[0]]
    entry = glossary.get_any(gloss_key)
    return {"status": 200, "term": entry['term'], 'definition': entry['definition']}
