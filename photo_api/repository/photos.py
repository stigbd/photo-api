"""This module contains functions for adding and getting photos from the database."""
import os
from uuid import UUID

import psycopg

from ..models import Photo

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_SSLMODE = os.getenv("POSTGRES_SSLMODE", "prefer")
POSTGRES_DB = os.getenv("POSTGRES_DB", "digital-rutebok")
POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", "rutebok")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "example")


async def add_photo(photo: Photo) -> UUID:
    """Add a photo to the database.

    Args:
        photo (Photo): A photo object.

    Returns:
        UUID: The uuid of the photo added.

    Raises:
        Exception: An exception
    """
    async with await psycopg.AsyncConnection.connect(
        f"host={POSTGRES_HOST}"
        f" port={POSTGRES_PORT}"
        f" sslmode={POSTGRES_SSLMODE}"
        f" dbname={POSTGRES_DB}"
        f" user={POSTGRES_USER}"
        f" password={POSTGRES_PASSWORD}",
        autocommit=False,
    ) as aconn:
        async with aconn.cursor() as cur:
            try:
                await cur.execute("CREATE SCHEMA IF NOT EXISTS rutebok;")
                await cur.execute(
                    (
                        "CREATE TABLE IF NOT EXISTS rutebok.photos "
                        "(id uuid PRIMARY KEY, filename VARCHAR(250), photo BYTEA);"
                    )
                )
            except Exception as e:
                raise e
            try:
                await cur.execute(
                    "INSERT INTO rutebok.photos (id, filename, photo) VALUES(%s, %s, %s)",
                    (photo.id, photo.filename, photo.content),
                )
            except Exception as e:
                raise e
            return photo.id


async def get_photos() -> list:
    """Get photos from the database.

    Returns:
        list: A list of photos.

    Raises:
        Exception: An exception
    """
    async with await psycopg.AsyncConnection.connect(
        f"host={POSTGRES_HOST}"
        f" port={POSTGRES_PORT}"
        f" sslmode={POSTGRES_SSLMODE}"
        f" dbname={POSTGRES_DB}"
        f" user={POSTGRES_USER}"
        f" password={POSTGRES_PASSWORD}",
        autocommit=False,
    ) as aconn:
        async with aconn.cursor() as cur:
            try:
                await cur.execute("CREATE SCHEMA IF NOT EXISTS rutebok;")
                await cur.execute(
                    (
                        "CREATE TABLE IF NOT EXISTS rutebok.photos "
                        "(id uuid PRIMARY KEY, filename VARCHAR(250), photo BYTEA);"
                    )
                )
            except Exception as e:
                raise e
            try:
                await cur.execute("SELECT * FROM rutebok.photos;")
                _result = await cur.fetchall()
                result = []
                for row in _result:
                    result.append(Photo(id=row[0], filename=row[1], content=row[2]))
                return result
            except Exception as e:
                raise e


async def get_photo(id: str) -> Photo | None:
    """Get a photo from the database.

    Args:
        id (str): The uuid of the photo.

    Returns:
        Photo: A photo with the given id.

    Raises:
        Exception: An exception
    """
    async with await psycopg.AsyncConnection.connect(
        f"host={POSTGRES_HOST}"
        f" port={POSTGRES_PORT}"
        f" sslmode={POSTGRES_SSLMODE}"
        f" dbname={POSTGRES_DB}"
        f" user={POSTGRES_USER}"
        f" password={POSTGRES_PASSWORD}",
        autocommit=False,
    ) as aconn:
        async with aconn.cursor() as cur:
            try:
                await cur.execute("CREATE SCHEMA IF NOT EXISTS rutebok;")
                await cur.execute(
                    (
                        "CREATE TABLE IF NOT EXISTS rutebok.photos "
                        "(id uuid PRIMARY KEY, filename VARCHAR(250), photo BYTEA);"
                    )
                )
            except Exception as e:
                raise e
            try:
                await cur.execute("SELECT * FROM rutebok.photos WHERE id = %s;", (id,))
                result = await cur.fetchone()
            except Exception as e:
                raise e

            return (
                Photo(id=result[0], filename=result[1], content=result[2])
                if result
                else None
            )
