FROM python:3.11-alpine

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1s

# install linux dependencies 
# these may vary by project
# this list is relatively lightweight
# and needed
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev gcc python3-dev musl-dev \
    && apk del build-deps \
    && apk --no-cache add musl-dev linux-headers g++

# install poetry to manage python dependencies
RUN curl -sSL https://install.python-poetry.org | python3 -

# install python dependencies
COPY ./pyproject.toml .
COPY ./poetry.lock .
RUN pip install --user poetry
ENV PATH="${PATH}:/root/.local/bin"
RUN poetry install --no-interaction --no-ansi
# copy project
COPY . .
# run at port 8000
EXPOSE 8000

# Command to run
CMD ["sh", "-c", "poetry shell --no-interaction && python manage.py runserver 0.0.0.0:8000"]