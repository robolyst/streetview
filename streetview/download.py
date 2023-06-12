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


def get_width_and_height_from_zoom(zoom: int) -> (int, int):
    """
    Returns the width and height of a panorama at a given zoom level, depends on the zoom level.
    """
    return 2**zoom, 2 ** (zoom - 1)


def make_download_url(pano_id: str, zoom: int, x: int, y: int) -> str:
    """
    Returns the URL to download a tile.
    """
    return f"https://cbk0.google.com/cbk?output=tile&panoid={pano_id}&zoom={zoom}&x={x}&y={y}"


def iter_tile_info(pano_id: str, zoom: int) -> Generator[TileInfo, None, None]:
    """
    Generate a list of a panorama's tiles and their position.
    """
    width, height = get_width_and_height_from_zoom(zoom)
    for x, y in itertools.product(range(width), range(height)):
        yield TileInfo(
            x=x,
            y=y,
            fileurl=make_download_url(pano_id=pano_id, zoom=zoom, x=x, y=y),
        )


def iter_tiles(pano_id: str, zoom: int) -> Generator[Tile, None, None]:
    for info in iter_tile_info(pano_id, zoom):
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


def get_panorama(pano_id: str, zoom: int) -> Image.Image:
    """
    Downloads a streetview panorama.
    """

    tile_width = 512
    tile_height = 512

    total_width, total_height = get_width_and_height_from_zoom(zoom)
    panorama = Image.new("RGB", (total_width * tile_width, total_height * tile_height))

    for tile in iter_tiles(pano_id=pano_id, zoom=zoom):
        panorama.paste(im=tile.image, box=(tile.x * tile_width, tile.y * tile_height))
        del tile

    return panorama
