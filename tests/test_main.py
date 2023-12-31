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
from psycopg import sql
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
POSTGRES_DB = os.getenv("POSTGRES_DB", "photo_api")
POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", "public")
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
        f"host={POSTGRES_HOST}"
        f" port={POSTGRES_PORT}"
        f" sslmode={POSTGRES_SSLMODE}"
        f" dbname={POSTGRES_DB}"
        f" user={POSTGRES_USER}"
        f" password={POSTGRES_PASSWORD}",
        autocommit=False,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(
                    sql.Identifier(POSTGRES_SCHEMA)
                )
            )
            cur.execute(
                sql.SQL(
                    "CREATE TABLE IF NOT EXISTS {}.photos "
                    "(id uuid PRIMARY KEY, filename VARCHAR(250), size INTEGER, photo BYTEA);"
                ).format(sql.Identifier(POSTGRES_SCHEMA)),
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
        files = {"file": ("img.png", data)}
        response = await client.post("/photos", files=files)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.headers["content-type"] == "application/json"
    assert type(response.json()) is dict
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
    assert type(response.json()) is list
    assert len(response.json()) == 1


@pytest.mark.anyio
async def test_get_photo_by_id(database, image_file) -> None:
    """Should return a photo with the given id."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/photos")
        photo_id = response.json()[0]["id"]
        response = await client.get(f"/photos/{photo_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"
    assert type(response.json()) is dict
    assert response.json()["id"] == photo_id
    assert response.json()["filename"] == "img.png"
    assert response.json()["size"] == len(open(image_file, "rb").read())


@pytest.mark.anyio
async def test_get_photo_download(database, image_file) -> None:
    """Should return a photo."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/photos")
        photo_id = response.json()[0]["id"]
        response = await client.get(f"/photos/{photo_id}/download")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "image/png"
    assert type(response.content) is bytes
    assert len(response.content) == len(open(image_file, "rb").read())
    assert response.content == open(image_file, "rb").read()


@pytest.mark.anyio
async def test_get_photo_not_found(database) -> None:
    """Should return 404 Not Found status code."""
    photo_id = uuid.uuid4()
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/photos/{photo_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.headers["content-type"] == "application/json"
    assert type(response.json()) is dict
    assert response.json()["detail"] == "Photo not found."
