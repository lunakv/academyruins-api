from fastapi import APIRouter
from fastapi.responses import FileResponse

from src.resources import static_paths as paths
from src.utils.response_models import GlossaryTerm

router = APIRouter()


@router.get("/", summary="Unofficial Glossary", response_model=dict[str, GlossaryTerm])
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
