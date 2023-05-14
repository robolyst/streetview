import itertools
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Generator

import requests
from PIL import Image


@dataclass
class TileInfo:
    x: int
    y: int
    fileurl: str


@dataclass
class Tile:
    x: int
    y: int
    image: Image.Image


def iter_tile_info(pano_id: str) -> Generator[TileInfo, None, None]:
    """
    Generate a list of a panorama's tiles and their position.
    """

    image_url = (
        "https://cbk0.google.com/cbk?output=tile&panoid={0:}&zoom=5&x={1:}&y={2:}"
    )

    for x, y in itertools.product(range(26), range(13)):
        yield TileInfo(
            x=x,
            y=y,
            fileurl=image_url.format(pano_id, x, y),
        )


def iter_tiles(pano_id: str) -> Generator[Tile, None, None]:
    for info in iter_tile_info(pano_id):
        # Try to download the image file
        while True:
            try:
                response = requests.get(info.fileurl, stream=True)
                break
            except requests.ConnectionError:
                print("Connection error. Trying again in 2 seconds.")
                time.sleep(2)

        image = Image.open(BytesIO(response.content))

        yield Tile(x=info.x, y=info.y, image=image)

        del response
        del image


def get_panorama(pano_id: str) -> Image.Image:
    """
    Downloads a streetview panorama.
    """

    tile_width = 512
    tile_height = 512

    panorama = Image.new("RGB", (26 * tile_width, 13 * tile_height))

    for tile in iter_tiles(pano_id=pano_id):
        panorama.paste(im=tile.image, box=(tile.x * tile_width, tile.y * tile_height))
        del tile

    return panorama
