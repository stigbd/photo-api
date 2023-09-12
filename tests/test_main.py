"""Test module for main.py."""
import os
import pathlib
import time
from typing import Any, Generator
import uuid

import docker
from fastapi import status
from httpx import AsyncClient
import psycopg
import pytest

from photo_api.main import app


@pytest.fixture
def anyio_backend() -> str:
    """Use anyio as the async backend.

    Returns:
        str: The async backend.
    """
    return "asyncio"


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_SSLMODE = os.getenv("POSTGRES_SSLMODE", "prefer")
POSTGRES_DB = os.getenv("POSTGRES_DB", "digital-rutebok")
POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", "rutebok")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "example")


@pytest.fixture(scope="session")
def image_file(tmp_path_factory) -> pathlib.Path:
    """Return a temporary folder with an image file.

    Returns:
        pathlib.Path: The path to the image file.
    """
    import random as r
    from PIL import Image

    fn = tmp_path_factory.mktemp("data") / "img.png"
    im = Image.new("RGB", (100, 100))
    pixels = im.load()
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            pixels[x, y] = (
                r.randint(0, 255),  # noqa: S311
                r.randint(0, 255),  # noqa: S311
                r.randint(0, 255),  # noqa: S311
            )
    im.save(fn)
    return fn


@pytest.fixture(scope="session")
def psql_docker() -> Generator:
    """Start a postgres docker container."""
    client = docker.from_env()
    container = client.containers.run(
        image="postgres:latest",
        auto_remove=True,
        environment=dict(
            POSTGRES_PASSWORD=POSTGRES_PASSWORD,
            POSTGRES_USER=POSTGRES_USER,
            POSTGRES_DB=POSTGRES_DB,
        ),
        name="test_postgres",
        ports={"5432/tcp": ("127.0.0.1", POSTGRES_PORT)},
        detach=True,
        remove=True,
    )

    # Wait for the container to start
    # (actually I use more complex check to wait for container to start but it doesn't really matter)
    time.sleep(5)

    yield

    container.stop()


@pytest.fixture(scope="session")
def database(psql_docker: Generator) -> Any:
    """Create a database."""
    with psycopg.connect(
        "host=localhost"
        " port=5432"
        " sslmode=prefer"
        " dbname=digital-rutebok"
        " user=postgres"
        " password=example",
        autocommit=False,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS rutebok;")
            cur.execute(
                (
                    "CREATE TABLE IF NOT EXISTS rutebok.photos "
                    "(id uuid PRIMARY KEY, filename VARCHAR(250), photo BYTEA);"
                )
            )


@pytest.mark.anyio
async def test_hello_world(database) -> None:
    """Test hello world route."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World"}


@pytest.mark.anyio
async def test_post_photos(database, image_file) -> None:
    """Should return status 201 and the id in location header."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        with open(image_file, "rb") as image:
            data = image.read()
        response = await client.post("/photos", files={"file": data})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.headers["content-type"] == "application/json"
    assert type(response.json()) == dict
    assert "id" in response.json()
    assert "Location" in response.headers
    assert response.headers["Location"] == f"/photos/{response.json()['id']}"


@pytest.mark.anyio
async def test_get_photos(database) -> None:
    """Should return a list of photos."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/photos")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"
    assert type(response.json()) == list
    assert len(response.json()) == 1


@pytest.mark.anyio
async def test_get_photo(database) -> None:
    """Should return a photo."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/photos")
        photo_id = response.json()[0]["id"]
        response = await client.get(f"/photos/{photo_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"
    assert type(response.json()) == dict


@pytest.mark.anyio
async def test_get_photo_download(database, image_file) -> None:
    """Should return a photo."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/photos")
        photo_id = response.json()[0]["id"]
        response = await client.get(f"/photos/{photo_id}/download")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "image/png"
    assert type(response.content) == bytes
    assert len(response.content) == len(open(image_file, "rb").read())


@pytest.mark.anyio
async def test_get_photo_not_found(database) -> None:
    """Should return 404 Not Found status code."""
    photo_id = uuid.uuid4()
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/photos/{photo_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.headers["content-type"] == "application/json"
    assert type(response.json()) == dict
    assert response.json()["detail"] == "Photo not found"
