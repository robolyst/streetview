streetview
----------

This is a light module for downloading photos from Google street view. The
functions allow you to retrieve current and **old** photos.

The photos on Google street view are panoramas and are refered to as such.
However, you have the option of downloading flat photos, or panoramas.

Retrieving photos is a two step process. First, you must translate GPS
coordinates into panorama ids. The following code retrieves a list of
the closest panoramas giving you their id and date:

	import streetview
	panoids = streetview.panoids(lat, lon)

You can then use the panorama ids to download photos with the following 
function:

	streetview.api_download(panoid, heading, flat_dir, key)

Full documentation is at docs/build/html/index.html


