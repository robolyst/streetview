import os

import pytest

from streetview import get_panorama_meta, get_streetview
from streetview.api import Location, MetaData
from streetview.utils import hash_image

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "NOKEY")


@pytest.mark.vcr(filter_query_parameters=["key"])
def test_readme_metadata_example():
    result = get_panorama_meta(
        pano_id="_R1mwpMkiqa2p0zp48EBJg",
        api_key=GOOGLE_MAPS_API_KEY,
    )
    expected = MetaData(
        date="2019-08",
        location=Location(lat=41.89820659475458, lng=12.47644649615282),
        pano_id="_R1mwpMkiqa2p0zp48EBJg",
        copyright="© Google",
    )
    assert result == expected


@pytest.mark.vcr(filter_query_parameters=["key"])
def test_get_streetview_returns_rbg_image():
    image = get_streetview(
        pano_id="_R1mwpMkiqa2p0zp48EBJg",
        api_key=GOOGLE_MAPS_API_KEY,
    )

    assert image.mode == "RGB"


@pytest.mark.vcr(filter_query_parameters=["key"])
def test_readme_basic_download_example():
    image = get_streetview(
        pano_id="z80QZ1_QgCbYwj7RrmlS0Q",
        api_key=GOOGLE_MAPS_API_KEY,
    )
    hash = hash_image(image)
    # image.save("test_readme_basic_download_example.jpg", "jpeg")
    assert hash == "61c4e54bbb0baff9fbdb669ddd856132"
