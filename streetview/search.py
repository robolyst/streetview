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
