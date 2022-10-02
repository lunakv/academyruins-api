# Academy Ruins API
Programmatic resources for Magic: the Gathering rules documents.

## About
This API provides access to various versions of MTG rules documents (CR, MTR, IPG), both in their raw form and (for the CR) as a structured JSON. It also contains diffs of those documents, and links to the most up-to-date version of them.

It is used to power the [Academy Ruins](https://github.com/lunakv/academyruins) project and utilized by several other MTG-related sites and services.

## Setup
### Prerequisites
- Python 3.10 or later
- PostgreSQL 14

### Installation
0. (recommended) Set up a virtual Python environment for the repository.
1. Set up Postgres and create a user and database for your API.
2. (optional) Set up a [Pushover](https://pushover.net/) account and create an API token for the app.
3. `cp .env_EXAMPLE .env`
4. Adjust the values in your `.env` file according to your local configuration
5. Install [Poetry](https://python-poetry.org/), either globally or inside your venv.
6. (Inside your venv) run `poetry install`
7. (Inside your venv) run `./update_schema.sh` to load the current schema into the database.

### Run
`python devstart.py`

The API server will start on port 8000 by default.

### Containers
For production deployments, there's a prepared `Dockerfile` and `docker-compose.yml` file you can inspect and use to run the API fully contained in a Docker container. Note that if you're running Postgres in a container and want to use `psql` from the host machine, you have to map port 5432 to the host and specify the `--host localhost` flag in any `psql` command in order to connect successfully.

## Code Style
This project uses the [Black](https://black.readthedocs.io/en/stable/) code formatter. When working on code in this repository, it is recommended to set up a Black integration with your code editor. If your editor does not support Black, make sure to run `black .` before any commits to make sure all files are formatted correctly. 
## Documentation
The full API docs are available at https://api.academyruins.com/docs

## Data
All data used by the site, both raw and processed, is periodically backed up to public a [Backblaze B2](https://www.backblaze.com/b2/) (S3 compatible) bucket. If you need to access that data for some reason, you can send me a message through one of the channels specified [on the site](https://academyruins.com/about) and request access to the bucket. 
