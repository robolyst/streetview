import os

import pytest

from streetview import (
    get_panorama_meta,
    search_panoramas,
    search_panoramas_url,
    search_panoramas_url_exact,
)
from streetview.search import Panorama

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "NOKEY")


SYDNEY = {
    "lat": -33.8796052,
    "lon": 151.1655341,
    "result_count": 20,
}

BELGRAVIA = {
    "lat": 51.4986562,
    "lon": -0.1570917,
    "result_count": 40,
}

MIDDLE_OF_OCEAN = {
    "lat": 28.092432,
    "lon": -34.399243,
}

TUNIS = {
    "lat": 36.8032829,
    "lon": 10.1808486,
}


@pytest.mark.vcr
@pytest.mark.parametrize("location", [SYDNEY, BELGRAVIA])
class TestPanodsOnLocations:
    """Test panoramas in specific locations."""

    @pytest.fixture(scope="function", autouse=True)
    def setup_method(self, location: dict):
        lat = location["lat"]
        lon = location["lon"]

        self.result_count = location["result_count"]
        self.result = search_panoramas(lat, lon)

    def test_that_there_is_at_least_one_item(self):
        assert len(self.result) >= 1

    def test_that_there_are_the_expected_number_of_results(self):
        assert len(self.result) == self.result_count

    def test_that_panoids_are_unique(self):
        panoids = [p.pano_id for p in self.result]
        uniques = list(dict.fromkeys(panoids))
        assert len(panoids) == len(uniques)

    @pytest.mark.vcr(filter_query_parameters=["key"])
    def test_that_dates_are_correct(self):
        ids = [p.pano_id for p in self.result if p.date is not None]
        dates = [p.date for p in self.result if p.date is not None]
        meta_dates = [
            get_panorama_meta(
                pano_id=pano_id,
                api_key=GOOGLE_MAPS_API_KEY,
            ).date
            for pano_id in ids
        ]

        assert dates == meta_dates


@pytest.mark.vcr
def test_readme_search_example():
    result = search_panoramas(lat=41.8982208, lon=12.4764804)[0]
    expected = Panorama(
        pano_id="_R1mwpMkiqa2p0zp48EBJg",
        lat=41.89820676786453,
        lon=12.47644220919742,
        heading=0.8815613985061646,
        pitch=89.001953125,
        roll=0.1744659692049026,
        date="2019-08",
        elevation=None,
    )
    assert result == expected


@pytest.mark.vcr
def test_search_where_there_are_no_results():
    result = search_panoramas(**MIDDLE_OF_OCEAN)
    assert len(result) == 0


@pytest.mark.vcr
def test_search_where_there_are_no_dates():
    result = search_panoramas(**TUNIS)

    dates = [p.date for p in result if p.date is not None]
    assert len(dates) == 0


@pytest.mark.vcr
def test_search_panoramas_url():
    panos = search_panoramas_url(
        "https://www.google.com/maps/@40.6982454,-73.980301,3a,84.9y,36.94h,99.2t"
        "/data=!3m6!1e1!3m4!1sp-EPpErUWv2pjDvUC3N6rQ!2e0!7i16384!8i8192?entry=ttu"
    )
    result = panos[0]
    expected = Panorama(
        pano_id="Jx-mUVj7jGZDYBvpfjD7Ng",
        lat=40.69822471286,
        lon=-73.98031354290725,
        heading=275.2777404785156,
        pitch=90.3123550415039,
        roll=358.1669006347656,
        date="2009-04",
        elevation=None,
    )
    assert result == expected


@pytest.mark.vcr
def test_search_panoramas_url_exact():
    result = search_panoramas_url_exact(
        "https://www.google.com/maps/@40.6982454,-73.980301,3a,84.9y,36.94h,99.2t"
        "/data=!3m6!1e1!3m4!1sp-EPpErUWv2pjDvUC3N6rQ!2e0!7i16384!8i8192?entry=ttu"
    )
    expected = Panorama(
        pano_id="p-EPpErUWv2pjDvUC3N6rQ",
        lat=40.69824541519994,
        lon=-73.9803009883494,
        heading=272.77001953125,
        pitch=89.0201187133789,
        roll=0.1823771148920059,
        date="2022-07",
        elevation=None,
    )
    assert result == expected
