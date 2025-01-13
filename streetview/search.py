import json
import re
from typing import List, Optional

import requests
from pydantic import BaseModel
from requests.models import Response


class Panorama(BaseModel):
    pano_id: str
    lat: float
    lon: float
    heading: float
    pitch: Optional[float]
    roll: Optional[float]
    date: Optional[str]
    elevation: Optional[float]


def make_search_url(lat: float, lon: float) -> str:
    """
    Builds the URL of the script on Google's servers that returns the closest
    panoramas (ids) to a give GPS coordinate.
    """
    url = (
        "https://maps.googleapis.com/maps/api/js/"
        "GeoPhotoService.SingleImageSearch"
        "?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d50!3m10"
        "!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4"
        "!1e8!1e6!5m1!1e2!6m1!1e2"
        "&callback=callbackfunc"
    )
    return url.format(lat, lon)


def make_pano_url(pano_id: str) -> str:
    """Builds the URL of the script on Google's servers that returns the metadata 
    of a given panorama. Must be one of official Street View panoramas, which have
    a length of 22 characters."""

    url = (
        "https://www.google.com/maps/photometa/v1?"
        "pb=!1m4!1smaps_sv.tactile!11m2!2m1!1b1!2"
        "m2!1sen!2snz!3m3!1m2!1e2!2s{:0}!4m61!1e1"
        "!1e2!1e3!1e4!1e5!1e6!1e8!1e12!1e17!2m1!1"
        "e1!4m1!1i48!5m1!1e1!5m1!1e2!6m1!1e1!6m1!"
        "1e2!9m36!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3"
        "!1m3!1e3!2b1!3e2!1m3!1e3!2b0!3e3!1m3!1e8"
        "!2b0!3e3!1m3!1e1!2b0!3e3!1m3!1e4!2b0!3e3"
        "!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e3!11m2!"
        "3m1!4b1"
        
    )
    return url.format(pano_id)

def search_request(lat: float, lon: float) -> Response:
    """
    Gets the response of the script on Google's servers that returns the
    closest panoramas (ids) to a give GPS coordinate.
    """
    url = make_search_url(lat, lon)
    return requests.get(url)


def extract_panoramas(text: str) -> List[Panorama]:
    """
    Given a valid response from the panoids endpoint, return a list of all the
    panoids.
    """

    # The response is actually javascript code. It's a function with a single
    # input which is a huge deeply nested array of items.
    blob = re.findall(r"callbackfunc\( (.*) \)$", text)[0]
    data = json.loads(blob)

    if data == [[5, "generic", "Search returned no images."]]:
        return []

    subset = data[1][5][0]

    raw_panos = subset[3][0]

    if len(subset) < 9 or subset[8] is None:
        raw_dates = []
    else:
        raw_dates = subset[8]

    # For some reason, dates do not include a date for each panorama.
    # the n dates match the last n panos. Here we flip the arrays
    # so that the 0th pano aligns with the 0th date.
    raw_panos = raw_panos[::-1]
    raw_dates = raw_dates[::-1]

    dates = [f"{d[1][0]}-{d[1][1]:02d}" for d in raw_dates]

    return [
        Panorama(
            pano_id=pano[0][1],
            lat=pano[2][0][2],
            lon=pano[2][0][3],
            heading=pano[2][2][0],
            pitch=pano[2][2][1] if len(pano[2][2]) >= 2 else None,
            roll=pano[2][2][2] if len(pano[2][2]) >= 3 else None,
            date=dates[i] if i < len(dates) else None,
            elevation=pano[3][0] if len(pano) >= 4 else None,
        )
        for i, pano in enumerate(raw_panos)
    ]


def search_panoramas(lat: float, lon: float) -> List[Panorama]:
    """
    Gets the closest panoramas (ids) to the GPS coordinates.
    """

    resp = search_request(lat, lon)
    pans = extract_panoramas(resp.text)
    return pans


def parse_url(url: str) -> tuple[str, ...]:
    """
    extracts the lat, lon and pano_id from url
    """
    matches = re.search(
        r"\/@([-+]?[0-9]+[.]?[0-9]*),([-+]?[0-9]+[.]?[0-9]*).+!1s(.+)!2e", url
    )

    if matches:
        return matches.groups()

    return ("", "", "")


def search_panoramas_url(url: str) -> list[Panorama]:
    """
    Gets the closest panoramas (ids) to the GPS coordinates in the url.
    """
    lat, lon, _ = parse_url(url)
    return search_panoramas(float(lat), float(lon))


def search_panoramas_url_exact(url: str) -> Panorama | None:
    """
    Searches for exact panorama in url
    """
    _, _, id = parse_url(url)

    panos = search_panoramas_url(url)
    panos = [pano for pano in panos if pano.pano_id == id]

    return panos[0] if len(panos) > 0 else None


def get_panorama(pano_id: str) -> Panorama:
    """
    Gets a panorama by its id.
    """
    url = make_pano_url(pano_id)
    resp = requests.get(url)
    data = json.loads(resp.text.replace(")]}'", ""))

    dates = re.findall(r"([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]", resp.text)
    dates = [list(d)[1:] for d in dates]

    if len(dates) >= 1:
        dates = [[int(v) for v in d] for d in dates]
        dates = [d for d in dates if d[1] <= 12 and d[1] >= 1]
        dates = [f"{d[0]}-{d[1]:02d}" for d in dates]

    return Panorama(
        pano_id=pano_id,
        lat=data[1][0][5][0][3][0][0][2][0][2],
        lon=data[1][0][5][0][3][0][0][2][0][3],
        heading=data[1][0][5][0][1][2][0],
        pitch=data[1][0][5][0][1][2][1] if len(data[1][0][5][0][1][2]) >= 2 else None,
        roll=data[1][0][5][0][1][2][2] if len(data[1][0][5][0][1][2]) >= 2 else None,
        date=dates[-1] if len(dates) > 0 else None,
        elevation=data[1][4][0] if False else None,
    )