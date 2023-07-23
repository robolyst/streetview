import os

import pytest

from streetview import get_panorama_meta, search_panoramas

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", None)


SYDNEY = {
    "lat": -33.8796052,
    "lon": 151.1655341,
}

BELGRAVIA = {
    "lat": 51.4986562,
    "lon": -0.1570917,
}

MIDDLE_OF_OCEAN = {
    "lat": 28.092432,
    "lon": -34.399243,
}

TUNIS = {
    "lat": 36.8032829,
    "lon": 10.1808486,
}


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
            get_panorama_meta(
                pano_id=pano_id,
                api_key=GOOGLE_MAPS_API_KEY,
            ).date
            for pano_id in ids
        ]

        assert dates == meta_dates


@pytest.mark.vcr
class TestPanoidsOnSydney(GenericGetPanoidsTest):
    def setup_method(self):
        self.result = search_panoramas(**SYDNEY)

    def test_that_there_are_the_expected_number_of_results(self):
        assert len(self.result) == 20


@pytest.mark.vcr
class TestPanoidsOnBelgravia(GenericGetPanoidsTest):
    def setup_method(self):
        self.result = search_panoramas(**BELGRAVIA)

    def test_that_there_are_the_expected_number_of_results(self):
        assert len(self.result) == 43


@pytest.mark.vcr
def test_readme_search_example():
    from streetview import search_panoramas

    panos = search_panoramas(lat=41.8982208, lon=12.4764804)
    first = panos[0]
    print(first)

    result = str(first)
    expected = (
        "pano_id='_R1mwpMkiqa2p0zp48EBJg'"
        " lat=41.89820676786453 lon=12.47644220919742"
        " heading=0.8815613985061646 pitch=89.001953125 roll=0.1744659692049026"
        " date='2019-08'"
    )

    assert result == expected


@pytest.mark.vcr
def test_search_where_there_are_no_results():
    result = search_panoramas(**MIDDLE_OF_OCEAN)
    assert len(result) == 0


@pytest.mark.vcr
def test_search_where_there_are_no_dates():
    result = search_panoramas(**TUNIS)

    dates = [p.date for p in result]
    assert dates == [None] * len(dates)


def test_coordinates_with_missing_pitch():
    panos = search_panoramas(35.658353457849685, 139.6920989241623)
    is_pitch_none = [p.pitch is None for p in panos]
    assert any(is_pitch_none)


def test_coordinates_with_missing_roll():
    panos = search_panoramas(35.658353457849685, 139.6920989241623)
    is_roll_none = [p.roll is None for p in panos]
    assert any(is_roll_none)
