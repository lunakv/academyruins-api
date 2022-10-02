FROM python:3.10

# Configure Poetry
ENV POETRY_VERSION=1.2.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Install poetry
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /code

# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-cache --witout dev


# Run app
COPY ./app /code/app
CMD ["poetry", "run", "uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
