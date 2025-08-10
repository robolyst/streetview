import hashlib
from io import BytesIO

from PIL import Image


def hash_image(image: Image.Image):
    """
    Returns the md5 hash of an image.
    """
    image_mock_file = BytesIO()
    image.save(image_mock_file, "jpeg")
    image_mock_file.seek(0)
    return hashlib.md5(image_mock_file.read()).hexdigest()
