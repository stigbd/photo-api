"""Photo API main module."""
import logging

from litestar import get, Litestar, post
from litestar.status_codes import HTTP_200_OK

from .photos import add_photos, get_photos


@get("/")
async def hello_world_route() -> dict[str, str]:
    """A simple hello world route.

    Returns:
        dict[str, str]: A dict with a message key.
    """
    return {"message": "Hello World"}


@post("photos", status_code=HTTP_200_OK)
async def add_photos_route() -> dict[str, int]:
    """A simple hello world route.

    Returns:
        dict[str, str]: A dict with a message key.

    Raises:
        Exception: An exception
    """
    try:
        id = add_photos()
    except Exception as e:
        logging.error(e)
        raise e
    return {"id": id}


@get("photos", status_code=HTTP_200_OK)
async def get_photos_route() -> list:
    """A simple hello world route.

    Returns:
        list: A dict with a message key.

    Raises:
        Exception: An exception
    """
    try:
        photos = get_photos()
    except Exception as e:
        logging.error(e)
        raise e
    return photos


app = Litestar(route_handlers=[hello_world_route, add_photos_route, get_photos_route])
