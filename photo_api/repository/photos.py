"""This module contains functions for adding and getting photos from the database."""
from uuid import UUID

import psycopg

from ..models import Photo


def add_photo(photo: Photo) -> UUID:
    """Add a photo to the database.

    Args:
        photo (Photo): A photo object.

    Returns:
        UUID: The uuid of the photo added.

    Raises:
        Exception: An exception
    """
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
            try:
                cur.execute("CREATE SCHEMA IF NOT EXISTS rutebok;")
                cur.execute(
                    (
                        "CREATE TABLE IF NOT EXISTS rutebok.photos "
                        "(id uuid PRIMARY KEY, filename VARCHAR(250), photo BYTEA);"
                    )
                )
            except Exception as e:
                raise e
            try:
                cur.execute(
                    "INSERT INTO rutebok.photos (id, filename, photo) VALUES(%s, %s, %s)",
                    (photo.id, photo.filename, photo.content),
                )
            except Exception as e:
                raise e
            return photo.id


def get_photos() -> list:
    """Get photos from the database.

    Returns:
        list: A list of photos.

    Raises:
        Exception: An exception
    """
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
            try:
                cur.execute("CREATE SCHEMA IF NOT EXISTS rutebok;")
                cur.execute("CREATE SCHEMA IF NOT EXISTS rutebok;")
                cur.execute(
                    (
                        "CREATE TABLE IF NOT EXISTS rutebok.photos "
                        "(id uuid PRIMARY KEY, filename VARCHAR(250), photo BYTEA);"
                    )
                )
            except Exception as e:
                raise e
            try:
                cur.execute("SELECT * FROM rutebok.photos;")
                result = cur.fetchall()
                return result
            except Exception as e:
                raise e


def get_photo(id: str) -> Photo | None:
    """Get a photo from the database.

    Args:
        id (str): The uuid of the photo.

    Returns:
        Photo: A photo with the given id.

    Raises:
        Exception: An exception
    """
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
            try:
                cur.execute("CREATE SCHEMA IF NOT EXISTS rutebok;")
                cur.execute("CREATE SCHEMA IF NOT EXISTS rutebok;")
                cur.execute(
                    (
                        "CREATE TABLE IF NOT EXISTS rutebok.photos "
                        "(id uuid PRIMARY KEY, filename VARCHAR(250), photo BYTEA);"
                    )
                )
            except Exception as e:
                raise e
            try:
                cur.execute("SELECT * FROM rutebok.photos WHERE id = %s;", (id,))
                result = cur.fetchone()
            except Exception as e:
                raise e

            return (
                Photo(id=result[0], filename=result[1], content=result[2])
                if result
                else None
            )
