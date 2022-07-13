import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .resources import seeder
from .routers import admin, glossary, link, rule, diff, rawfile, metadata, pending
from .utils.remove422 import remove_422s
from .utils.scheduler import Scheduler

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

description = """This API provides information about Magic: the Gathering rules and policy documents. It was 
primarily created to serve the [Academy Ruins](https://academyruins.com) project and the [Fryatog]( 
https://github.com/Fryyyyy/Fryatog/) rules bot, but it has found other uses since. You can find the source for the 
project on [GitHub](https://github.com/lunakv/academyruins-api).
"""

app = FastAPI(
    title="Academy Ruins API",
    description=description,
    openapi_tags=[
        {"name": "Rules", "description": "Resources pertaining to the parsed representation of the current CR."},
        {
            "name": "Redirects",
            "description": "Simple links to the most current versions of the documents (as hosted by WotC).",
        },
        {"name": "Diffs"},
        {"name": "Files", "description": "Historical versions of the raw documents themselves."},
    ],
    redoc_url="/docs",
    docs_url=None,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(admin.router, prefix="/admin")
app.include_router(rule.router)
app.include_router(glossary.router, prefix="/glossary")
app.include_router(link.router, prefix="/link")
app.include_router(diff.router, prefix="/diff")
app.include_router(rawfile.router, prefix="/file")
app.include_router(metadata.router, prefix="/metadata")
app.include_router(pending.router, prefix="/pending")

app.openapi = remove_422s(app)
Scheduler().start()


@app.on_event("startup")
async def seed():
    await seeder.seed()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse({"detail": str(exc)}, status_code=422)


@app.get("/", include_in_schema=False, status_code=400)
def root():
    return {
        "detail": "This is the root of the Academy Ruins API. You can find the documentation at "
        "https://api.academyruins.com/docs"
    }
