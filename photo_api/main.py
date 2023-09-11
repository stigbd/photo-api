"""Photo API main module."""
import logging
from typing import Annotated, Any
from uuid import uuid4

from litestar import get, Litestar, MediaType, post, Response
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED

from .models import Photo
from .repository import add_photo, get_photo, get_photos


@get("/", status_code=HTTP_200_OK, content_media_type=MediaType.JSON)
async def hello_world_route() -> dict[str, str]:
    """A simple hello world route.

    Returns:
        dict[str, str]: A dict with a message key.
    """
    return {"message": "Hello World"}


@post(
    "photos",
    status_code=HTTP_201_CREATED,
)
async def post_photo_handler(
    data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
) -> Response:
    """Add a new photo.

    Args:
        data (UploadFile): The data from the request.

    Returns:
        Response: A response with location header.

    Raises:
        Exception: An exception
    """
    content = await data.read()
    filename = data.filename
    try:
        id = uuid4()
        photo: Photo = Photo(id, filename, content)
        id = add_photo(photo)
    except Exception as e:
        logging.exception(e)
        raise e
    return Response(
        content={"id": str(id)},
        headers={"Location": f"/photos/{str(id)}"},
    )


@get("/photos", status_code=HTTP_200_OK)
async def get_photos_handler() -> list[Photo]:
    """Get a list of photos.

    Returns:
        list: A dict with a message key.

    Raises:
        Exception: An exception
    """
    try:
        photos = get_photos()
    except Exception as e:
        logging.exception(e)
        raise e
    return photos


@get("/photos/{id:str}", status_code=HTTP_200_OK)
async def get_photo_handler(id: str) -> dict[str, Any]:
    """Get a single Photo.

    Args:
        id (str): The uuid of the photo.

    Returns:
        Photo: A photo with the given uuid.

    Raises:
        Exception: An exception
    """
    try:
        photo = get_photo(id)
    except Exception as e:
        logging.exception(e)
        raise e
    return photo.__dict__


app = Litestar(
    route_handlers=[
        hello_world_route,
        post_photo_handler,
        get_photos_handler,
        get_photo_handler,
    ]
)
