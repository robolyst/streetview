streetview
==========

This is a light module for downloading photos from Google street view. The
functions allow you to retrieve current and **old** photos. Google does have an
API for accessing Street View. However, it does not allow you to access old
photos. Their javascript API allows you to download segments of current photos.
This API also allows you to download each full panorama as you see it on Google
Street View.

*Please note, Google does not maintain the access points used by this API for
public use. Therefore, this hack may break if Google makes changes to how
Street View works.*

Dependencies
------------
Requests:

	sudo pip install requests

Python Imaging Library:

	sudo apt-get install python-PIL

or

	sudo pip install pillow



Quick start
------------

The photos on Google street view are panoramas. Each parnorama has it's own
unique ID. Retrieving photos is a two step process. First, you must translate GPS
coordinates into panorama IDs. The following code retrieves a list of
the closest panoramas.

	import streetview
	panoids = streetview.panoids(lat=-33.85693857571269, lon=151.2144895142714)

The list contains their ID, exact coordinates, and the year and month the photo
was taken if known:

	[{
      'lat': -33.8568510378028,
      'panoid': u'aX3nhhCruYOr-i1vSef13Q',
      'lon': 151.2145143359253},
    {
      'lat': -33.85702709988117,
      'panoid': u'OH7ReEUauWGKYqUwff4csA',
      'lon': 151.2144704271479},
    {
      'lat': -33.85696902229012,
      'panoid': u'73qGSwuFKWAAAAQXLB3qpA',
      'year': 2014,
      'lon': 151.2143939813708,
      'month': 6},
    {
      'lat': -33.85698122751459,
      'panoid': u'FE62TMqVMXwAAAQo8C4L6A',
      'year': 2015,
      'lon': 151.214408211074,
      'month': 5},
    {
      'lat': -33.85694092862602,
      'panoid': u'pTWGmeN8LTgAAAQqT_-Ekg',
      'year': 2015,
      'lon': 151.2144308896659,
      'month': 6},
    {
      'lat': -33.85693857571269,
      'panoid': u'pV6jtRc157XZtWpVIR-rtg',
      'year': 2015,
      'lon': 151.2144895142714,
      'month': 12}
      ]


You can then use the panorama ids to download photos with the following
function:

	streetview.api_download(panoid, heading, flat_dir, key)


Documentation
-------------
Full documentation is at docs/build/html/index.html
