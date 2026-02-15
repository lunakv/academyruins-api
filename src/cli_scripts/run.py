from typing import Annotated, Union

import typer
import uvicorn
from dotenv import load_dotenv

app = typer.Typer()


@app.command()
def run(
    port: int = 8000,
    host: str = "localhost",
    reload: Annotated[
        bool, typer.Option(help="Whether the server should automatically restart on file change.")
    ] = False,
):
    """
    Start the API web server.
    """
    uvicorn.run("src.main:app", port=port, host=host, reload=reload)


@app.command()
def bootstrap():
    """
    Bootstrap the database from scratch. Downloads and parses the current
    CR, MTR, and IPG from WotC and seeds the database. Idempotent — skips
    if data already exists.
    """
    from src.cli_scripts.bootstrap import bootstrap as do_bootstrap

    do_bootstrap()


@app.callback()
def options(
    envfile: Annotated[
        Union[str, None], typer.Option(help="Optional location of a .env file that should be loaded")
    ] = None
):
    if envfile:
        load_dotenv(dotenv_path=envfile)


if __name__ == "__main__":
    app()
