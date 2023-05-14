import sys
import streetview
import pytest


SYDNEY = {
    'lat': -33.8796052,
    'lon': 151.1655341,
}


def get(recieved, expected):
    expected_panoids = [p['panoid'] for p in expected]
    return [r for r in recieved if r['panoid'] in expected_panoids]


@pytest.mark.vcr
def test_that_panoids_data_returns_200():
    resp = streetview._panoids_data(**SYDNEY)
    assert resp.status_code == 200


@pytest.mark.vcr
def test_that_panoids_data_returns_large_payload():
    resp = streetview._panoids_data(**SYDNEY)
    assert len(resp.text) > 1000


@pytest.mark.vcr
class TestPanoidsOnSydney:

    def setup_method(self):
        self.result = streetview.panoids(**SYDNEY)
    
    def test_that_there_is_at_least_one_item(self):
        assert len(self.result) >= 1

    def test_that_each_item_has_panoid(self):
        for panoid in self.result:
            assert 'panoid' in panoid

    def test_that_each_item_has_lat(self):
        for panoid in self.result:
            assert 'lat' in panoid

    def test_that_each_item_has_lon(self):
        for panoid in self.result:
            assert 'lon' in panoid

