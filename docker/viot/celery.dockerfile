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
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

WORKDIR $PYSETUP_PATH
COPY ${PROJECT_DIR}/pyproject.toml ${PROJECT_DIR}/poetry.lock ./
RUN poetry install --without dev,test


FROM python-base AS production

# https://stackoverflow.com/questions/44605117/oserror-errno-13-permission-denied-when-initializing-celery-in-docker
RUN ln -s /run/shm /dev/shm


COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY ${PROJECT_DIR}/app /code/app

RUN mkdir -p /code/app/logs
COPY ${PROJECT_DIR}/scripts/start-celery.sh /code/celery-entrypoint.sh

WORKDIR /code

RUN chown -R viot:viot /code
USER viot

EXPOSE 8555

CMD ["./celery-entrypoint.sh"]
