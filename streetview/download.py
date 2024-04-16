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
    pano_id: str,
    zoom: int = 5,
    multi_threaded: bool = False,
    crop_bottom_right_border: bool = False,
) -> Image.Image:
    """
    Downloads a streetview panorama.
    Multi-threaded is a lot faster, but it's also a lot more likely to get you banned.
    Crop border will remove the black border at the bottom and right of the panorama.
    """

    tile_width = 512
    tile_height = 512

    total_width, total_height = get_width_and_height_from_zoom(zoom)
    panorama = Image.new("RGB", (total_width * tile_width, total_height * tile_height))

    for tile in iter_tiles(pano_id=pano_id, zoom=zoom, multi_threaded=multi_threaded):
        panorama.paste(im=tile.image, box=(tile.x * tile_width, tile.y * tile_height))
        del tile

    if crop_bottom_right_border:
        # Crop the black border at the bottom and right of the panorama
        # This is a common issue with user-contributed panoramas
        # The dimensions of the panorama are not always correct / multiple of 512
        panorama = crop_bottom_and_right_black_border(panorama)

    return panorama


def crop_bottom_and_right_black_border(img: Image.Image):
    """
    Crop the black border at the bottom and right of the panorama.
    The implementation is not perfect, but it works for most cases.
    """
    (width, height) = img.size
    bw_img = img.convert("L")
    black_luminance = 4

    # Find the bottom of the panorama
    pixel_cursor = (0, height - 1)
    valid_max_y = height - 1
    while pixel_cursor[0] < width and pixel_cursor[1] >= 0:
        pixel_color = bw_img.getpixel(pixel_cursor)

        if pixel_color > black_luminance:
            # Found a non-black pixel
            # Double check if all the pixels below this one are black
            all_pixels_below = list(
                bw_img.crop((0, pixel_cursor[1] + 1, width, height)).getdata()
            )
            all_black = True
            for pixel in all_pixels_below:
                if pixel > black_luminance:
                    all_black = False

            if all_black:
                valid_max_y = pixel_cursor[1]
                break
            else:
                # A false positive, probably the actual valid bottom pixel is very close to black
                # Reset the cursor to the next vertical line to the right
                pixel_cursor = (pixel_cursor[0] + 1, height - 1)

        else:
            pixel_cursor = (pixel_cursor[0], pixel_cursor[1] - 1)

    # Find the right of the panorama
    pixel_cursor = (width - 1, 0)
    valid_max_x = width - 1
    while pixel_cursor[1] < height and pixel_cursor[0] >= 0:
        pixel_color = bw_img.getpixel(pixel_cursor)

        if pixel_color > black_luminance:
            # Found a non-black pixel
            # Double check if all the pixels to the right of this one are black
            all_pixels_to_the_right = list(
                bw_img.crop((pixel_cursor[0] + 1, 0, width, height)).getdata()
            )
            all_black = True
            for pixel in all_pixels_to_the_right:
                if pixel > black_luminance:
                    all_black = False
            if all_black:
                valid_max_x = pixel_cursor[0]
                break
            else:
                # A false positive, probably the actual valid right pixel is very close to black
                # Reset the cursor to the next horizontal line below
                pixel_cursor = (width - 1, pixel_cursor[1] + 1)

        else:
            pixel_cursor = (pixel_cursor[0] - 1, pixel_cursor[1])

    valid_height = valid_max_y + 1
    valid_width = valid_max_x + 1

    if valid_height == height and valid_width == width:
        # No black border found
        return img

    print(
        f"Found black border. Cropping from {width}x{height} to {valid_width}x{valid_height}"
    )
    return img.crop((0, 0, valid_width, valid_height))
