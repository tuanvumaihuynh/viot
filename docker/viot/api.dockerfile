# https://github.com/orgs/python-poetry/discussions/1879
FROM python:3.11-slim-bullseye AS python-base

ARG PROJECT_DIR=./src/viot-api

RUN groupadd -r viot && useradd -r -m -g viot viot

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    POETRY_VERSION=1.8.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


FROM python-base AS builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

WORKDIR $PYSETUP_PATH
COPY ${PROJECT_DIR}/pyproject.toml ${PROJECT_DIR}/poetry.lock ./
RUN poetry install --without worker,dev,test


FROM python-base AS production

WORKDIR /code
# Fixing when run pytest
RUN chown -R viot:viot /code

COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY ${PROJECT_DIR}/app /code/app

# Add alembic for migrations
COPY ${PROJECT_DIR}/alembic.ini /code

ENV PYTHONPATH=':$PYTHONPATH:.'

USER viot

CMD ["python", "app/main.py"]
