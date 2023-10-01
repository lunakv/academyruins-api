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
