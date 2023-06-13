from io import BytesIO
from typing import Dict, Union

import requests
from PIL import Image
from pydantic import BaseModel


class Location(BaseModel):
    lat: float
    lng: float


class MetaData(BaseModel):
    date: str
    location: Location
    pano_id: str


def get_panorama_meta(pano_id: str, api_key: str) -> MetaData:
    """
    Returns a panorama's metadata.

    Quota: This function doesn't use up any quota or charge on your API_KEY.

    Endpoint documented at:
    https://developers.google.com/maps/documentation/streetview/metadata
    """
    url = (
        "https://maps.googleapis.com/maps/api/streetview/metadata"
        f"?pano={pano_id}&key={api_key}"
    )
    resp = requests.get(url)
    return MetaData(**resp.json())


def get_streetview(
    pano_id: str,
    api_key: str,
    width: int = 640,
    height: int = 640,
    heading: int = 0,
    fov: int = 120,
    pitch: int = 0,
) -> Image.Image:
    """
    Get an image using the official API. These are not panoramas.

    You can find instructions to obtain an API key here:
    https://developers.google.com/maps/documentation/streetview/

    Args:
        pano_id (str): The panorama id.
        heading (int): The heading of the photo. Each photo is taken with a 360
            camera. You need to specify a direction in degrees as the photo
            will only cover a partial region of the panorama. The recommended
            headings to use are 0, 90, 180, or 270.
        api_key (str): Your API key.
        width (int): Image width (max 640 for non-premium downloads).
        height (int): Image height (max 640 for non-premium downloads).
        fov (int): Image field-of-view.
        pitch (int): Image pitch.
    """

    url = "https://maps.googleapis.com/maps/api/streetview"
    params: Dict[str, Union[str, int]] = {
        "size": "%dx%d" % (width, height),
        "fov": fov,
        "pitch": pitch,
        "heading": heading,
        "pano": pano_id,
        "key": api_key,
    }

    response = requests.get(url, params=params, stream=True)
    img = Image.open(BytesIO(response.content))
    return img
