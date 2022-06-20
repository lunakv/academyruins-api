import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .resources import seeder
from .utils.scheduler import Scheduler
from .routers import admin, glossary, link, rule, diff, rawfile, metadata

logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)


@app.on_event("startup")
async def seed():
    await seeder.seed()

app.mount('/static', StaticFiles(directory="app/static"), name="static")
app.include_router(admin.router, prefix='/admin')
app.include_router(glossary.router, prefix='/glossary')
app.include_router(link.router, prefix='/link')
app.include_router(diff.router, prefix='/diff')
app.include_router(rawfile.router, prefix='/file')
app.include_router(metadata.router, prefix='/metadata')
app.include_router(rule.router)

Scheduler().start()


@app.get("/", include_in_schema=False, status_code=400)
def root():
    return {
        'details': 'This is the root of the Academy Ruins API. You can find the documentation at '
                   'https://api.academyruins.com/docs'}
