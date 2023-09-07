"""Test module for main.py."""
from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient
import pytest

from photo_api.main import app


@pytest.mark.asyncio
async def test_hello_world() -> None:
    """Test hello world route."""
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/")
        assert response.status_code == HTTP_200_OK
        assert response.json() == {"message": "Hello World"}
