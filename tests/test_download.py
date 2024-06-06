import hashlib
from io import BytesIO

import pytest
from PIL import Image

from streetview import get_panorama
from streetview.download import (
    TileInfo,
    fetch_panorama_tile,
    get_width_and_height_from_zoom,
    iter_tile_info,
    iter_tiles,
    make_download_url,
)
from streetview.tool import crop_bottom_and_right_black_border

# This MD5 was retrieved empirically by downloading tile with bad coordinates
BAD_TILE_MD5 = "be32aa9ed3880664433199f9e0615cd6"


def hash_tile(tile: Image.Image):
    """
    Returns the md5 hash of a tile
    """
    tile_mock_file = BytesIO()
    tile.save(tile_mock_file, "jpeg")
    tile_mock_file.seek(0)
    return hashlib.md5(tile_mock_file.read()).hexdigest()


@pytest.mark.parametrize("zoom", [1, 2, 3, 4, 5, 6, 7])
@pytest.mark.vcr()
def test_width_from_zoom_is_correct(zoom: int):
    width, height = get_width_and_height_from_zoom(zoom)

    # Try to fetch one more tile than the width and height and verify we get a bad tile
    out_of_bound_width_tile_info = TileInfo(
        x=width + 1,
        y=height,
        fileurl=make_download_url(
            pano_id="z80QZ1_QgCbYwj7RrmlS0Q", zoom=zoom, x=width + 1, y=height
        ),
    )
    out_of_bound_tile = fetch_panorama_tile(out_of_bound_width_tile_info)
    assert hash_tile(out_of_bound_tile) == BAD_TILE_MD5


@pytest.mark.parametrize("zoom", [1, 2, 3, 4, 5, 6, 7])
@pytest.mark.vcr()
def test_height_from_zoom_is_correct(zoom: int):
    width, height = get_width_and_height_from_zoom(zoom)

    # Try to fetch one more tile than the width and height and verify we get a bad tile
    out_of_bound_height_tile_info = TileInfo(
        x=width,
        y=height + 1,
        fileurl=make_download_url(
            pano_id="z80QZ1_QgCbYwj7RrmlS0Q", zoom=zoom, x=width, y=height + 1
        ),
    )
    out_of_bound_tile = fetch_panorama_tile(out_of_bound_height_tile_info)
    assert hash_tile(out_of_bound_tile) == BAD_TILE_MD5


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


@pytest.mark.vcr()
def test_that_panorama_downloads_successfully():
    image = get_panorama(pano_id="z80QZ1_QgCbYwj7RrmlS0Q", zoom=1)
    image.save("image.jpg", "jpeg")


@pytest.mark.vcr()
def test_that_panorama_downloads_successfully_multi_threaded():
    image = get_panorama(pano_id="z80QZ1_QgCbYwj7RrmlS0Q", zoom=1, multi_threaded=True)
    image.save("image.jpg", "jpeg")


@pytest.mark.vcr()
def test_that_panorama_downloads_successfully_crop_bottom_right_border():
    # this pano_id has a black border on the bottom right
    pano_id = "EVGmA-L6LuI_7-elZaDq1g"
    for i in range(1, 6):
        image = get_panorama(pano_id=pano_id, zoom=i)
        image = crop_bottom_and_right_black_border(image)
        image.save(f"image-z{i}.jpg", "jpeg")
