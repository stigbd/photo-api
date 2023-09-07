"""This module contains functions for adding and getting photos from the database."""
import psycopg


def add_photos() -> int:
    """Add photos to the database.

    Returns:
        int: The id of the photo added.

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
                    "CREATE TABLE IF NOT EXISTS rutebok.photos (id serial PRIMARY KEY, photo BYTEA);"
                )
            except Exception as e:
                raise e
            try:
                photo = open("test_photos/test_photo.jpg", "rb").read()
                cur.execute(
                    "INSERT INTO rutebok.photos (id, photo) VALUES(%s, %s)",
                    (1, photo),
                )
            except Exception as e:
                raise e
            return 1


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
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS rutebok.photos (id serial PRIMARY KEY, photo BYTEA);"
                )
            except Exception as e:
                raise e
            try:
                cur.execute("SELECT * FROM rutebok.photos;")
                result = cur.fetchall()
                return result
            except Exception as e:
                raise e
