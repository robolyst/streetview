import pytest

from streetview import get_panorama
from streetview.download import iter_tile_info, iter_tiles


def test_that_all_the_tiles_are_generated():
    tiles = list(iter_tile_info(pano_id="z80QZ1_QgCbYwj7RrmlS0Q"))
    assert len(tiles) == 26 * 13


@pytest.mark.vcr()
def test_that_first_tile_can_be_saved():
    tiles = iter_tiles(pano_id="z80QZ1_QgCbYwj7RrmlS0Q")
    tile = next(tiles)
    tile.image.save("image.jpg", "jpeg")
    next(tiles)


@pytest.mark.skip(reason="Takes a really long time.")
def test_that_panorama_downloads_successfully():
    image = get_panorama(pano_id="z80QZ1_QgCbYwj7RrmlS0Q")
    image.save("image.jpg", "jpeg")
