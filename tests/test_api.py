import os

import pytest

from streetview import get_streetview

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", None)


@pytest.mark.vcr(filter_query_parameters=["key"])
def test_readme_metadata_example():
    from streetview import get_panorama_meta

    meta = get_panorama_meta(
        pano_id="_R1mwpMkiqa2p0zp48EBJg", api_key=GOOGLE_MAPS_API_KEY
    )
    print(meta)

    result = str(meta)
    expected = (
        "date='2019-08'"
        " location=Location(lat=41.89820659475458, lng=12.47644649615282)"
        " pano_id='_R1mwpMkiqa2p0zp48EBJg'"
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
    from streetview import get_streetview

    image = get_streetview(
        pano_id="z80QZ1_QgCbYwj7RrmlS0Q",
        api_key=GOOGLE_MAPS_API_KEY,
    )

    image.save("image.jpg", "jpeg")
