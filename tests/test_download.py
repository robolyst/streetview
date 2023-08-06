import pytest

from streetview import get_panorama
from streetview.download import (
    get_width_and_height_from_zoom,
    iter_tile_info,
    iter_tiles,
)


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
