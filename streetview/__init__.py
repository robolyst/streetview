import itertools
import os
import re
import shutil
import time
from datetime import datetime
from io import BytesIO

import requests
from PIL import Image
from requests.models import Response


def make_panoids_url(lat: float, lon: float) -> str:
    """
    Builds the URL of the script on Google's servers that returns the closest
    panoramas (ids) to a give GPS coordinate.
    """
    url = "https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d50!3m10!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4!1e8!1e6!5m1!1e2!6m1!1e2&callback=_xdc_._v2mub5"
    return url.format(lat, lon)


def panoids_request(lat: float, lon: float) -> Response:
    """
    Gets the response of the script on Google's servers that returns the
    closest panoramas (ids) to a give GPS coordinate.
    """
    url = make_panoids_url(lat, lon)
    return requests.get(url)


def extract_panoids(text: str) -> list[dict]:
    """
    Given a valid response from the panoids endpoint, return a list of all the
    panoids.
    """

    pattern = r'\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)'

    pans = re.findall(pattern, text)
    pans = [
        {
            "panoid": p[0],
            "lat": float(p[1]),
            "lon": float(p[2]),
        }
        for p in pans
    ]
    return pans


def drop_duplicates(items, key):
    keys = [key(item) for item in items]
    return [
        item for i, item in enumerate(items) if key(item) not in keys[:i]
    ]


def panoids(lat, lon):
    """
    Gets the closest panoramas (ids) to the GPS coordinates.
    """

    resp = panoids_request(lat, lon)

    # Get all the panorama ids and coordinates
    # I think the latest panorama should be the first one. And the previous
    # successive ones ought to be in reverse order from bottom to top. The final
    # images don't seem to correspond to a particular year. So if there is one
    # image per year I expect them to be orded like:
    # 2015
    # XXXX
    # XXXX
    # 2012
    # 2013
    # 2014
    pans = extract_panoids(resp.text)
    pans = drop_duplicates(pans, key=lambda p: p['panoid'])

    # Get all the dates
    # The dates seem to be at the end of the file. They have a strange format but
    # are in the same order as the panoids except that the latest date is last
    # instead of first.
    dates = re.findall(r"([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]", resp.text)
    dates = [list(d)[1:] for d in dates]  # Convert to lists and drop the index

    if len(dates) > 0:
        # Convert all values to integers
        dates = [[int(v) for v in d] for d in dates]

        # Make sure the month value is between 1-12
        dates = [d for d in dates if d[1] <= 12 and d[1] >= 1]

        # The last date belongs to the first panorama
        year, month = dates.pop(-1)
        pans[0].update({"year": year, "month": month})

        # The dates then apply in reverse order to the bottom panoramas
        dates.reverse()
        for i, (year, month) in enumerate(dates):
            pans[-1 - i].update({"year": year, "month": month})

    # # Make the first value of the dates the index
    # if len(dates) > 0 and dates[-1][0] == '':
    #     dates[-1][0] = '0'
    # dates = [[int(v) for v in d] for d in dates]  # Convert all values to integers
    #
    # # Merge the dates into the panorama dictionaries
    # for i, year, month in dates:
    #     pans[i].update({'year': year, "month": month})

    # Sort the pans array
    def func(x):
        if "year" in x:
            return datetime(year=x["year"], month=x["month"], day=1)
        else:
            return datetime(year=3000, month=1, day=1)

    pans.sort(key=func)

    return pans


def tiles_info(panoid):
    """
    Generate a list of a panorama's tiles and their position.

    The format is (x, y, filename, fileurl)
    """

    image_url = (
        "https://cbk0.google.com/cbk?output=tile&panoid={0:}&zoom=5&x={1:}&y={2:}"
    )

    # The tiles positions
    coord = list(itertools.product(range(26), range(13)))

    tiles = [
        (x, y, "%s_%dx%d.jpg" % (panoid, x, y), image_url.format(panoid, x, y))
        for x, y in coord
    ]

    return tiles


def download_tiles(tiles, directory, disp=False):
    """
    Downloads all the tiles in a Google Stree View panorama into a directory.

    Params:
        tiles - the list of tiles. This is generated by tiles_info(panoid).
        directory - the directory to dump the tiles to.
    """

    for i, (x, y, fname, url) in enumerate(tiles):
        if disp and i % 20 == 0:
            print("Image %d (%d)" % (i, len(tiles)))

        # Try to download the image file
        while True:
            try:
                response = requests.get(url, stream=True)
                break
            except requests.ConnectionError:
                print("Connection error. Trying again in 2 seconds.")
                time.sleep(2)

        with open(directory + "/" + fname, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response


def stich_tiles(panoid, tiles, directory, final_directory):
    """
    Stiches all the tiles of a panorama together. The tiles are located in
    `directory'.
    """

    tile_width = 512
    tile_height = 512

    panorama = Image.new("RGB", (26 * tile_width, 13 * tile_height))

    for x, y, fname, url in tiles:
        fname = directory + "/" + fname
        tile = Image.open(fname)

        panorama.paste(im=tile, box=(x * tile_width, y * tile_height))

        del tile

    #        print fname

    panorama.save(final_directory + ("/%s.jpg" % panoid))
    del panorama


def delete_tiles(tiles, directory):
    for x, y, fname, url in tiles:
        os.remove(directory + "/" + fname)


def api_download(
    panoid,
    heading,
    flat_dir,
    key,
    width=640,
    height=640,
    fov=120,
    pitch=0,
    extension="jpg",
    year=2017,
    fname=None,
):
    """
    Download an image using the official API. These are not panoramas.

    Params:
        :panoid: the panorama id
        :heading: the heading of the photo. Each photo is taken with a 360
            camera. You need to specify a direction in degrees as the photo
            will only cover a partial region of the panorama. The recommended
            headings to use are 0, 90, 180, or 270.
        :flat_dir: the direction to save the image to.
        :key: your API key.
        :width: downloaded image width (max 640 for non-premium downloads).
        :height: downloaded image height (max 640 for non-premium downloads).
        :fov: image field-of-view.
        :image_format: desired image format.
        :fname: file name

    You can find instructions to obtain an API key here: https://developers.google.com/maps/documentation/streetview/
    """
    if not fname:
        fname = "%s_%s_%s" % (year, panoid, str(heading))
    image_format = extension if extension != "jpg" else "jpeg"

    url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        # maximum permitted size for free calls
        "size": "%dx%d" % (width, height),
        "fov": fov,
        "pitch": pitch,
        "heading": heading,
        "pano": panoid,
        "key": key,
    }

    response = requests.get(url, params=params, stream=True)
    try:
        img = Image.open(BytesIO(response.content))
        filename = "%s/%s.%s" % (flat_dir, fname, extension)
        img.save(filename, image_format)
    except:
        print("Image not found")
        filename = None
    del response
    return filename


def download_flats(
    panoid,
    flat_dir,
    key,
    width=400,
    height=300,
    fov=120,
    pitch=0,
    extension="jpg",
    year=2017,
):
    for heading in [0, 90, 180, 270]:
        api_download(
            panoid, heading, flat_dir, key, width, height, fov, pitch, extension, year
        )
