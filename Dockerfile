FROM python:3.14

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_NO_CACHE=1

WORKDIR /code

# Install dependencies
COPY uv.lock pyproject.toml ./
RUN uv sync --locked --no-dev --no-install-project

# Run app
COPY src /code/src
CMD ["uv", "run", "--no-sync", "uvicorn", "src.main:app", "--proxy-headers", "--forwarded-allow-ips=*", "--host", "0.0.0.0", "--port", "80"]
