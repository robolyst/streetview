"""Unit tests for streetview"""
# pylint:disable=invalid-name

import os
import json

import streetview

TESTDIR = os.path.dirname(__file__)


def isclose(a, b, rel_tol=1e-06, abs_tol=0.0):
    """Approximate comparison of floating point numbers

    :param a:
    :param b:
    :param rel_tol:
    :param abs_tol:
    """
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def aeq(a, b):
    """Test for approximate equality

    :param a:
    :param b:
    """
    assert isclose(a, b), "failed isclose({},{})".format(a, b)


def get(recieved, expected):
    """Check that each exppected panoid was received

    :param recieved:
    :param expected:
    """
    expected_panoids = [p['panoid'] for p in expected]
    return [r for r in recieved if r['panoid'] in expected_panoids]


def test__panoids_data():
    """Test streetview._panoids_data"""

    lat = -33.8796052
    lon = 151.1655341

    # pylint:disable=protected-access
    resp = streetview._panoids_data(lat, lon)

    assert resp.status_code == 200, "Exected staus code 200, received {}".format(resp.status_code)
    assert len(resp.text) > 10000, "Response too short"


def test_panoids_sydney():
    """test_panoids_sydney"""

    lat = -33.8843298
    lon = 151.1666392
    info = streetview.panoids(lat, lon)

    expected = [
        #  {
            #  'lat': -33.88433247600134,
            #  'panoid': 'KTnyIFMvOh9uUqDVEQdP2w',
            #  'year': 2007,
            #  'lon': 151.1666428923351,
            #  'month': 12
        #  },
        {
            'lat': -33.88433963284601,
            'panoid': 'z8KUYeQ2l-O5zdzmSwqPRQ',
            'year': 2013,
            'lon': 151.1666253718159,
            'month': 7
        },
        {
            'lat': -33.88432975440379,
            'panoid': 'UQrvQ_b_TwO1ylks9VI9rA',
            'year': 2014,
            'lon': 151.1666391815143,
            'month': 5
        },
    ]

    # print get(info, expected)
    # pylint:disable=invalid-name
    with open(os.path.join(TESTDIR, 'test_panoids_sydney.actual'), 'w') as f:
        json.dump(info, f, indent=4, sort_keys=True)

    ids = {pano['panoid']: pano for pano in info}
    for example in expected:
        assert example['panoid'] in ids, "Could not fine expected panoid {} in response".format(example['panoid'])
        actual = ids[example['panoid']]
        aeq(actual['lat'], example['lat'])
        aeq(actual['lon'], example['lon'])
        aeq(actual['year'], example['year'])
        aeq(actual['month'], example['month'])


def test_panoids_belgrade():
    """test_panoids_belgrade"""

    lat = 44.7807774
    lon = 20.4631614
    info = streetview.panoids(lat, lon)

    expected = [
        {
            'lat': 44.78080446275501,
            'panoid': 'H4gnGehUMXHbEszHFtTvDA',
            'year': 2013,
            'lon': 20.46312104308652,
            'month': 11
        },
        {
            'lat': 44.7807773932411,
            'panoid': 'NFSzU4sTH3HR4J6QFgKFmw',
            'year': 2015,
            'lon': 20.4631613851401,
            'month': 6
        },
    ]

    with open(os.path.join(TESTDIR, 'test_panoids_belgrade.actual'), 'w') as output:
        json.dump(info, output, indent=4, sort_keys=True)

    ids = {pano['panoid']: pano for pano in info}
    for example in expected:
        assert example['panoid'] in ids, "Could not fine expected panoid {} in response".format(example['panoid'])
        actual = ids[example['panoid']]
        aeq(actual['lat'], example['lat'])
        aeq(actual['lon'], example['lon'])
        aeq(actual['year'], example['year'])
        aeq(actual['month'], example['month'])


def test_panoids_sanfransico():
    """test_panoids_sanfransico"""

    lat = 37.7743002
    lon = -122.4283573
    info = streetview.panoids(lat, lon)

    expected = [
        {
            'lat': 37.77432243711459,
            'panoid': 'mOIblLGQqLpZUDne_VLAdQ',
            'year': 2007,
            'lon': -122.4283616654013,
            'month': 11,
        },
        {
            'lat': 37.77429785272119,
            'panoid': 'm5xxmNmdd-g0y8Y-kpmb8Q',
            'year': 2008,
            'lon': -122.4283486679392,
            'month': 5,
        },
        {
            'lat': 37.77432814229113,
            'panoid': 'DgYMRMl9pMkPojc_aFaWOw',
            'year': 2011,
            'lon': -122.4283649736079,
            'month': 2,
        },
        #  {
            #  'lat': 37.77426806398835,
            #  'panoid': 'QO-svL6NrTqiocGSKWFK4w',
            #  'year': 2011,
            #  'lon': -122.4283685897149,
            #  'month': 4,
        #  },
        #  {
            #  'lat': 37.77426374081248,
            #  'panoid': '11HdGr2_t8BIZJ-56mJm9A',
            #  'year': 2013,
            #  'lon': -122.428371097386,
            #  'month': 11,
        #  },
        {
            'lat': 37.7743035331551,
            'panoid': '1G148Vno08mtwAaQ_roRqg',
            'year': 2014,
            'lon': -122.4283477300864,
            'month': 3,
        },
        {
            'lat': 37.7742959110328,
            'panoid': 'fp0uFJfqO2e0uEWhbDkIMQ',
            'year': 2014,
            'lon': -122.4283817194891,
            'month': 5,
        },
        #  {
            #  'lat': 37.77426752482152,
            #  'panoid': 'ag5GcSl7BmhYVmXNYYvcmw',
            #  'year': 2014,
            #  'lon': -122.4283597323728,
            #  'month': 7,
        #  },
        #  {
            #  'lat': 37.77426966585636,
            #  'panoid': 'wHBAtZTAqJHtrXqqIRNfgw',
            #  'year': 2014,
            #  'lon': -122.4283659734244,
            #  'month': 10,
        #  },
        {
            'lat': 37.77429993268145,
            'panoid': '3Eng_G9SqCYWnQydcZTP3A',
            'year': 2015,
            'lon': -122.428373031613,
            'month': 1,
        },
        {
            'lat': 37.77432015149672,
            'panoid': 'Hqhy1zUzdzwyhoLD1naHUQ',
            'year': 2015,
            'lon': -122.4283974703461,
            'month': 6,
        },
        #  {
            #  'lat': 37.7742707230769,
            #  'panoid': 'VlSQppuJiOrEXPl0uEFUpg',
            #  'year': 2015,
            #  'lon': -122.428350877336,
            #  'month': 7,
        #  },
        {
            'lat': 37.77429208676779,
            'panoid': 'q4XZZgs2zwWtc6eNblwbng',
            'year': 2015,
            'lon': -122.4283729863899,
            'month': 10,
        },
        {
            'lat': 37.77432525957246,
            'panoid': '84EbbbrnJI-Dnj7ZFgXj3A',
            'year': 2016,
            'lon': -122.4283551268714,
            'month': 6,
        },
        {
            'lat': 37.77432618270405,
            'panoid': 'e8LRJ1mcvgXXywxz2af_og',
            'year': 2017,
            'lon': -122.4283773760892,
            'month': 2,
        },
        #  {
            #  'lat': 37.77430015050959,
            #  'panoid': 'atLD3spRNleJ-50dqXZDmw',
            #  'year': 2017,
            #  'lon': -122.4283573289222,
            #  'month': 4,
        #  },
    ]

    # pylint:disable=invalid-name
    with open(os.path.join(TESTDIR, 'test_panoids_sanfransico.actual'), 'w') as f:
        json.dump(info, f, indent=4, sort_keys=True)

    ids = {pano['panoid']: pano for pano in info}
    for example in expected:
        assert example['panoid'] in ids, "Could not fine expected panoid {} in response".format(example['panoid'])
        actual = ids[example['panoid']]
        aeq(actual['lat'], example['lat'])
        aeq(actual['lon'], example['lon'])
        aeq(actual['year'], example['year'])
        aeq(actual['month'], example['month'])

#
