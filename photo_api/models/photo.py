"""Photo model.""" ""
from uuid import UUID


class Photo:
    """Photo model."""

    id: UUID
    filename: str
    content: bytes

    def __init__(self, id: UUID, filename: str, content: bytes) -> None:
        """Create a photo object.

        Initialize a photo object with a uuid, filename and content.

        Args:
            id (UUID): The uuid of the photo.
            filename (str): The filename of the photo.
            content (bytes): The content of the photo.
        """
        self.id = id
        self.filename = filename
        self.content = content
