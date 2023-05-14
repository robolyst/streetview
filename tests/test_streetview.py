import sys

import pytest

import streetview

SYDNEY = {
    "lat": -33.8796052,
    "lon": 151.1655341,
}


def get(recieved, expected):
    expected_panoids = [p["panoid"] for p in expected]
    return [r for r in recieved if r["panoid"] in expected_panoids]


@pytest.mark.vcr
def test_thatpanoids_request_returns_200():
    resp = streetview.panoids_request(**SYDNEY)
    assert resp.status_code == 200


@pytest.mark.vcr
def test_thatpanoids_request_returns_large_payload():
    resp = streetview.panoids_request(**SYDNEY)
    assert len(resp.text) > 1000


@pytest.mark.vcr
class TestPanoidsOnSydney:
    def setup_method(self):
        self.result = streetview.panoids(**SYDNEY)

    def test_that_there_is_at_least_one_item(self):
        assert len(self.result) >= 1

    def test_that_each_item_has_panoid(self):
        for panoid in self.result:
            assert "panoid" in panoid

    def test_that_each_item_has_lat(self):
        for panoid in self.result:
            assert "lat" in panoid

    def test_that_each_item_has_lon(self):
        for panoid in self.result:
            assert "lon" in panoid

    def test_that_there_are_the_expected_number_of_results(self):
        assert len(self.result) == 20

    def test_that_panoids_are_unique(self):
        panoids = [p["panoid"] for p in self.result]
        uniques = list(dict.fromkeys(panoids))
        assert len(panoids) == len(uniques)

    def test_that_panoid_exists(self):
        panoid = {
            "panoid": "F1dTjx_cF7_viUk4-3yruA",
            "lat": -33.87959459151072,
            "lon": 151.1654857862822,
            "year": 2014,
            "month": 5,
        }
        assert any([p == panoid for p in self.result])


# def test_():
#     resp = streetview.panoids_request(**SYDNEY)
#     result = streetview.extract_panoids(resp.text)

#     for p in result:
#         print(p['panoid'])

#     assert False
