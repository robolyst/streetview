import hashlib
from io import BytesIO

import pytest
import requests
from PIL import Image

from streetview import get_panorama
from streetview.download import (
    get_width_and_height_from_zoom,
    iter_tile_info,
    iter_tiles,
    make_download_url,
)

# This MD5 was retrieved empirically by downloading tile with bad coordinates
BAD_TILE_MD5 = "be32aa9ed3880664433199f9e0615cd6"


def get_tile_md5_from_url(pano_id: str, zoom: int, x: int, y: int):
    """
    Returns the md5 hash of a tile from url
    """
    url = make_download_url(pano_id=pano_id, zoom=zoom, x=x, y=y)
    response = requests.get(url, stream=True)
    image = Image.open(BytesIO(response.content))

    image_file = BytesIO()
    image.save(image_file, "jpeg")
    image_file.seek(0)
    return hashlib.md5(image_file.read()).hexdigest()


@pytest.mark.parametrize("zoom", [1, 2, 3, 4, 5, 6, 7])
def test_width_and_height_from_zoom_is_correct(zoom: int):
    width, height = get_width_and_height_from_zoom(zoom)

    # Try to fetch one more tile than the width and height and verify we get a bad tile
    out_of_bound_width_md5 = get_tile_md5_from_url(
        pano_id="z80QZ1_QgCbYwj7RrmlS0Q", zoom=zoom, x=width + 1, y=height
    )
    assert out_of_bound_width_md5 == BAD_TILE_MD5

    out_of_bound_height_md5 = get_tile_md5_from_url(
        pano_id="z80QZ1_QgCbYwj7RrmlS0Q", zoom=zoom, x=width, y=height + 1
    )
    assert out_of_bound_height_md5 == BAD_TILE_MD5


@pytest.mark.parametrize("zoom", [1, 2, 3, 4, 5, 6, 7])
def test_that_all_the_tiles_are_generated(zoom: int):
    tiles = list(iter_tile_info(pano_id="z80QZ1_QgCbYwj7RrmlS0Q", zoom=zoom))
    width, height = get_width_and_height_from_zoom(zoom)
    assert len(tiles) == width * height


@pytest.mark.vcr()
def test_that_first_tile_can_be_saved():
    tiles = iter_tiles(pano_id="z80QZ1_QgCbYwj7RrmlS0Q", zoom=1)
    tile = next(tiles)
    tile.image.save("image.jpg", "jpeg")
    next(tiles)


def test_that_panorama_downloads_successfully():
    image = get_panorama(pano_id="z80QZ1_QgCbYwj7RrmlS0Q", zoom=1)
    image.save("image.jpg", "jpeg")
