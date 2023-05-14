import os

import pytest

import streetview
import streetview.api
import streetview.search

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", None)


SYDNEY = {
    "lat": -33.8796052,
    "lon": 151.1655341,
}

BELGRAVIA = {
    "lat": 51.4986562,
    "lon": -0.1570917,
}


@pytest.mark.vcr
def test_thatsearch_request_returns_200():
    resp = streetview.search.search_request(**SYDNEY)
    assert resp.status_code == 200


@pytest.mark.vcr
def test_thatsearch_request_returns_large_payload():
    resp = streetview.search.search_request(**SYDNEY)
    assert len(resp.text) > 1000


class GenericGetPanoidsTest:
    def setup_method(self):
        raise NotImplementedError()

    def test_that_there_is_at_least_one_item(self):
        assert len(self.result) >= 1

    def test_that_panoids_are_unique(self):
        panoids = [p.pano_id for p in self.result]
        uniques = list(dict.fromkeys(panoids))
        assert len(panoids) == len(uniques)

    @pytest.mark.vcr(filter_query_parameters=["key"])
    def test_that_dates_are_correct(self):
        ids = [p.pano_id for p in self.result if p.date is not None]
        dates = [p.date for p in self.result if p.date is not None]
        meta_dates = [
            streetview.api.get_pano_metadata(
                panoid=panoid,
                api_key=GOOGLE_MAPS_API_KEY,
            ).date
            for panoid in ids
        ]

        assert dates == meta_dates


@pytest.mark.vcr
class TestPanoidsOnSydney(GenericGetPanoidsTest):
    def setup_method(self):
        self.result = streetview.search_panoramas(**SYDNEY)

    def test_that_there_are_the_expected_number_of_results(self):
        assert len(self.result) == 20


@pytest.mark.vcr
class TestPanoidsOnBelgravia(GenericGetPanoidsTest):
    def setup_method(self):
        self.result = streetview.search_panoramas(**BELGRAVIA)

    def test_that_there_are_the_expected_number_of_results(self):
        assert len(self.result) == 43
