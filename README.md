# photo_api

A small experiemental project to learn about storing and retrieving images from a database.

## Usage

```zsh
% curl -X POST -F "file=@/path/to/image.jpg" http://localhost:8000/photo
```

## Development

### Prerequisites

- [Python 3.11](https://www.python.org/downloads/)
- [poetry](https://python-poetry.org/docs/#installation)
- [nox](https://nox.thea.codes/en/stable/installation.html)
- [nox-poetry](https://pypi.org/project/nox-poetry/)

### Getting Started

To run it locally in your virtual development environment, run the following commands:

```zsh
% poetry install
% poetry run uvicorn photo_api.main:app --reload
```

To run it locally in a Docker container, run the following commands:

```zsh
% docker build -t photo_api .
% docker run -p 8000:8000 photo_api
```

Or in docker compose with a postgres database and [adminer](https://www.adminer.org/)):

```zsh
% docker compose up
```

### Running the linters, checkers and tests

```zsh
% nox
```
