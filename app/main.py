import logging
from typing import Set

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .resources import seeder
from .utils.remove422 import remove_422s
from .utils.scheduler import Scheduler
from .routers import admin, glossary, link, rule, diff, rawfile, metadata, pending

logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

description = """
This API provides information about rules resources for Magic: the Gathering. It was primarily created to serve the 
[Academy Ruins](https://academyruins.com) project and the [Fryatog](https://github.com/Fryyyyy/Fryatog/) rules bot,
but it has found other uses since.
"""

app = FastAPI(
    title="Academy Ruins API",
    description=description,
    openapi_tags=[
        {"name": "Rules", "description": "Resources pertaining to the parsed representation of the current CR."}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)


app.mount('/static', StaticFiles(directory="app/static"), name="static")
app.include_router(admin.router, prefix='/admin')
app.include_router(glossary.router, prefix='/glossary')
app.include_router(link.router, prefix='/link')
app.include_router(diff.router, prefix='/diff')
app.include_router(rawfile.router, prefix='/file')
app.include_router(metadata.router, prefix='/metadata')
app.include_router(pending.router, prefix='/pending')
app.include_router(rule.router)

app.openapi = remove_422s(app)
Scheduler().start()


@app.on_event("startup")
async def seed():
    await seeder.seed()
    print('x')


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse({"detail": str(exc)}, status_code=422)


@app.get("/", include_in_schema=False, status_code=400)
def root():
    return {
        'detail': 'This is the root of the Academy Ruins API. You can find the documentation at '
                  'https://api.academyruins.com/docs'}
