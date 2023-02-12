# Academy Ruins API
Programmatic resources for Magic: the Gathering rules documents.

## About
This API provides access to various versions of MTG rules documents (CR, MTR, IPG), both in their raw form and (for the CR) as a structured JSON. It also contains diffs of those documents, and links to the most up-to-date version of them.

It is used to power the [Academy Ruins](https://github.com/lunakv/academyruins) project and utilized by several other MTG-related sites and services.

## Setup
### Prerequisites
- Python 3.10 or later
- PostgreSQL 14
- (optional) [Pushover](https://pushover.net/) account

### Installation
1. Install the [Poetry](https://python-poetry.org/docs/#installation) package manager
2. `poetry install`
3. Start Postgres and create a user and database for your API.
4. `cp .env_EXAMPLE .env`
5. Adjust the values in your `.env` file according to your local configuration
6. `poetry run ./update_schema.sh` to load the current schema into the database.

### Run
`poetry run python devstart.py`

The API server will start on port 8000 by default.

### Containers
For production deployments, there's a prepared `Dockerfile` and `docker-compose.yml` file you can inspect and use to run the API fully contained in a Docker container. Note that if you're running Postgres in a container and want to use `psql` from the host machine, you have to map port 5432 to the host and specify the `--host localhost` flag in any `psql` command in order to connect successfully.

## Documentation
The full API docs are available at https://api.academyruins.com/docs

## Data
All data used by the site, both raw and processed, is periodically backed up to public a [Backblaze B2](https://www.backblaze.com/b2/) (S3 compatible) bucket. You can view the contents of this bucket at <https://backup.academyruins.com> If you need bulk/programatic access to that data for some reason, send me a message through one of the channels specified [on the site](https://academyruins.com/about). 
