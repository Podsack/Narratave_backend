FROM python:3.11-alpine as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.5.1

RUN apk add --no-cache gcc libffi-dev musl-dev postgresql-dev
RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

COPY pyproject.toml poetry.lock README.md ./
RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin

COPY . ./narratave
RUN poetry build && /venv/bin/pip install dist/*.whl
RUN /venv/bin/python ./narratave/manage.py collectstatic -v 2 --noinput

FROM base as final

RUN apk add --no-cache libffi libpq ffmpeg
COPY --from=builder /venv /venv
COPY --from=builder /app/narratave /narratave

COPY docker-entrypoint.sh ./
EXPOSE 8000
RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT ["/bin/sh", "-c", "./docker-entrypoint.sh"]