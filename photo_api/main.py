"""Photo API main module."""
import logging
from typing import Any
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status, UploadFile
from fastapi.responses import JSONResponse, Response

from .models import Photo, PhotoOut
from .repository import add_photo, get_photo, get_photos

app = FastAPI(debug=True)


@app.get("/")
async def hello_world_route() -> dict[str, str]:
    """A simple hello world route.

    Returns:
        dict[str, str]: A dict with a message key.
    """
    return {"message": "Hello World"}


@app.post("/photos")
async def post_photo_handler(
    file: UploadFile, status_code: int = status.HTTP_201_CREATED
) -> JSONResponse:
    """Add a new photo.

    Args:
        file (UploadFile): The file from the request.
        status_code (int): The status code. Defaults to status.HTTP_201_CREATED.

    Returns:
        JSONResponse: A response with location header.

    Raises:
        Exception: An exception
    """
    content = await file.read()
    filename = file.filename if file.filename else ""
    try:
        id = uuid4()
        photo: Photo = Photo(id=id, filename=filename, content=content)
        id = await add_photo(photo)
    except Exception as e:
        logging.exception(e)
        raise e
    return JSONResponse(
        status_code=status_code,
        content={"id": str(id)},
        headers={"Location": f"/photos/{str(id)}"},
    )


@app.get(
    "/photos",
    response_model=list[PhotoOut],
    status_code=status.HTTP_200_OK,
)
async def get_photos_handler() -> list[PhotoOut]:
    """Get a list of photos.

    Returns:
        list: A dict with a message key.

    Raises:
        Exception: An exception
    """
    try:
        photos = await get_photos()
    except Exception as e:
        logging.exception(e)
        raise e
    return photos


@app.get("/photos/{id:str}", response_model=PhotoOut, status_code=status.HTTP_200_OK)
async def get_photo_handler(id: str) -> Any:
    """Get a single Photo.

    Args:
        id (str): The uuid of the photo.

    Returns:
        Any: A photo with the given uuid.

    Raises:
        HTTPException: If the photo is not found.
        Exception: An exception
    """
    try:
        UUID(id, version=4)
        photo = await get_photo(id)
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found.")
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid uuid in path parameter."
        ) from e
    except Exception as e:
        logging.exception(e)
        raise e from e
    return photo


@app.get(
    "/photos/{id:str}/download",
    response_class=Response,
    status_code=status.HTTP_200_OK,
)
async def get_photo_download_handler(id: str) -> Response:
    """Get a single Photo.

    Args:
        id (str): The uuid of the photo.

    Returns:
        Response: A file with the given photo.

    Raises:
        HTTPException: If the photo is not found.
        Exception: An exception
    """
    try:
        UUID(id, version=4)
        photo = await get_photo(id)
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid uuid in path parameter."
        ) from e
    except Exception as e:
        logging.exception(e)
        raise e

    return Response(
        content=photo.content,
        media_type="image/png",
    )
