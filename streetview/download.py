import itertools
import time
import concurrent.futures
from dataclasses import dataclass
from io import BytesIO
from typing import Generator, Tuple

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


def get_width_and_height_from_zoom(zoom: int) -> Tuple[int, int]:
    """
    Returns the width and height of a panorama at a given zoom level, depends on the
    zoom level.
    """
    return 2**zoom, 2 ** (zoom - 1)


def make_download_url(pano_id: str, zoom: int, x: int, y: int) -> str:
    """
    Returns the URL to download a tile.
    """
    return (
        "https://cbk0.google.com/cbk"
        f"?output=tile&panoid={pano_id}&zoom={zoom}&x={x}&y={y}"
    )


def fetch_panorama_tile(tile_info: TileInfo) -> Image.Image:
    """
    Tries to download a tile, returns a PIL Image.
    """
    while True:
        try:
            response = requests.get(tile_info.fileurl, stream=True)
            break
        except requests.ConnectionError:
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)

    return Image.open(BytesIO(response.content))


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


def iter_tiles(
    pano_id: str, zoom: int, multi_threaded: bool = False
) -> Generator[Tile, None, None]:
    if not multi_threaded:
        for info in iter_tile_info(pano_id, zoom):
            image = fetch_panorama_tile(info)
            yield Tile(x=info.x, y=info.y, image=image)
        return

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_tile = {
            executor.submit(fetch_panorama_tile, info): info
            for info in iter_tile_info(pano_id, zoom)
        }
        for future in concurrent.futures.as_completed(future_to_tile):
            info = future_to_tile[future]
            try:
                image = future.result()
            except Exception as exc:
                print(f"{info.fileurl} generated an exception: {exc}")
            else:
                yield Tile(x=info.x, y=info.y, image=image)


def get_panorama(
    pano_id: str, zoom: int = 5, multi_threaded: bool = False
) -> Image.Image:
    """
    Downloads a streetview panorama.
    Multi-threaded is a lot faster, but it's also a lot more likely to get you banned.
    """

    tile_width = 512
    tile_height = 512

    total_width, total_height = get_width_and_height_from_zoom(zoom)
    panorama = Image.new("RGB", (total_width * tile_width, total_height * tile_height))

    for tile in iter_tiles(pano_id=pano_id, zoom=zoom, multi_threaded=multi_threaded):
        panorama.paste(im=tile.image, box=(tile.x * tile_width, tile.y * tile_height))
        del tile

    return panorama
