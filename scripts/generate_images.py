import os
from pathlib import Path


def generate_image(path: str, i: int) -> None:
    """Return a temporary folder with an image file.

    Returns:
        pathlib.Path: The path to the image file.
    """
    import random as r
    from PIL import Image

    fn = os.path.join(path, f"img_{i+1}.png")
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


if __name__ == "__main__":
    path = "test-images"
    Path(path).mkdir(parents=False, exist_ok=True)
    for i in range(10):
        generate_image(path, i)
