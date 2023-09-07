FROM python:3.11

RUN mkdir -p /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install "poetry==1.6.1"
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

ADD photo_api /app/photo_api

EXPOSE 8000

CMD ["uvicorn", "photo_api.main:app",  "--host", "0.0.0.0"]
