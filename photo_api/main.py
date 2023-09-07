"""Photo API main module."""
from litestar import get, Litestar


@get("/")
async def hello_world() -> dict[str, str]:
    """A simple hello world route.

    Returns:
        dict[str, str]: A dict with a message key.
    """
    return {"message": "Hello World"}


app = Litestar(route_handlers=[hello_world])
