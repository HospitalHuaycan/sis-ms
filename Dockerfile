ARG UV_VERSION=latest
ARG VARIANT=3.13

FROM ghcr.io/astral-sh/uv:$UV_VERSION AS uv

FROM python:$VARIANT-bookworm AS build

COPY --from=uv /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.13 \
    UV_PROJECT_ENVIRONMENT=/app

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
        --locked \
        --no-dev \
        --no-install-project

FROM python:$VARIANT-slim

# Optional: add the application virtualenv to search path.
ENV PATH=/app/bin:$PATH

RUN groupadd -r app && \
    useradd -r -d /app -g app -N app
# Copy the pre-built `/app` directory to the runtime container
# and change the ownership to user app and group app in one step.
COPY --from=build --chown=app:app /app /app
WORKDIR /app
COPY ./app/ ./app/
COPY ./tools/ ./tools/
COPY ./alembic.ini .

USER app
EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0"]
