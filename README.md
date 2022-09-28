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
2. 
3. `cp .env_EXAMPLE .env`
4. (optional) Set up a [Pushover](https://pushover.net/) account and create an API token for the app.
5. Adjust the values in your `.env` file according to your local configuration
6. `pip install -r requirements.txt`
7. Inside your virtual environment, run `./update_schema.sh` to configure your database schema.

### Run
- `uvicorn app.main:app --reload`  
or
- `python devstart.py`

The API server will start on port 8000 by default.

### Docker
There's a prepared `Dockerfile` and `docker-compose.yml` file you can inspect and use to run the API fully contained in a Docker container. Note that if you're running Postgres in a container and want to use `psql` from the host machine, you have to map port 5432 to the host and specify the `--host localhost` flag in any `psql` command in order to connect successfully.

## Documentation
The full API docs are available at https://api.academyruins.com/docs

## Data
All data used by the site, both raw and processed, is periodically backed up to public a [Backblaze B2](https://www.backblaze.com/b2/) (S3 compatible) bucket. If you need to access that data for some reason, you can send me a message through one of the channels specified [on the site](https://academyruins.com/about) and request access to the bucket. 
