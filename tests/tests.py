import sys
import nose
import streetview


def test__panoids_data():

	lat = -33.8796052
	lon = 151.1655341

	resp = streetview._panoids_data(lat, lon)

	assert resp.status_code == 200
	assert len(resp.text) > 10000


def test_extract_correct_panoid_and_dates():

    lat = -33.8772851
    lon = 151.1680999
    info = streetview.panoids(lat, lon)

    expected = [
        {
            'lat': -33.87727680526863,
            'panoid': 'QXWvZA0iAkym7rIeepaXIQ',
            'year': 2007,
            'lon': 151.1681359973246,
            'month': 11,
        },
        {
            'lat': -33.87728318904757,
            'panoid': 'KbLn6JUJgGEH5PlS2PqEdQ',
            'year': 2009,
            'lon': 151.1681276444272,
            'month': 12,
        },
        {
            'lat': -33.87729666809455,
            'panoid': u'guCayngEMaMhtYbOQBEarw',
            'year': 2013,
            'lon': 151.1681253013978,
            'month': 7,
        },
        {
            'lat': -33.87728463529014,
            'panoid': u'8rdET7t9bgxsrWc8kiFjvg',
            'year': 2014,
            'lon': 151.1681354882824,
            'month': 4,
        }
    ]

    for example in expected:
        assert example in info


def test_extract_correct_panoid_and_dates_2():

    lat = 52.4031729
    lon = -1.5491263
    info = streetview.panoids(lat, lon)

    expected = [
        {
            'lat': 52.40319991049719,
            'panoid': '0Ij4F_ykgshzUeJggW2NlA',
            'year': 2011,
            'lon': -1.54904573705366,
            'month': 10
        },
        {
            'lat': 52.40287421994784,
            'panoid': 'l6t7Rc6N0n6fYGgqaIzP5Q',
            'year': 2012,
            'lon': -1.548772355568133,
            'month': 10
        },
        {
            'lat': 52.4032176345565,
            'panoid': '4gUuu4pwq8geBLhJ2wsj9w',
            'year': 2014,
            'lon': -1.549038183459658,
            'month': 7
        },
        {
            'lat': 52.40322165054555,
            'panoid': 'w2m5nxl6kXKcgJOLyHFZIg',
            'year': 2016,
            'lon': -1.549027980885967,
            'month': 7
        },
        {
            'lat': 52.403219719,
            'panoid': 'RuvqiuaangWgwxK7_jZ3qA',
            'year': 2017,
            'lon': -1.549030487,
            'month': 4
        },
    ]

    for example in expected:
        assert example in info
