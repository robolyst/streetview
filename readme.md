# streetview

This is a light module for downloading photos from Google street view. The
functions allow you to retrieve current and **old** photos. Google does have an
API for accessing Street View. However, it does not allow you to access old
photos. Their javascript API allows you to download segments of current photos.
This API also allows you to download each full panorama as you see it on Google
Street View.

*Please note, Google does not maintain the access points used by this API for
public use. Therefore, this hack may break if Google makes changes to how
Street View works.*

# Install

Install from pip with:

	pip install streetview

# Quick start

## Search for Panoramas

The photos on Google street view are panoramas. Each parnorama has its own
unique ID. Retrieving photos is a two step process. First, you must translate GPS
coordinates into panorama IDs. The following code retrieves a list of
the closest panoramas:

```python
from streetview import search_panoramas

panos = search_panoramas(lat=41.8982208, lon=12.4764804)
first = panos[0]

print(first)
# pano_id='_R1mwpMkiqa2p0zp48EBJg' lat=41.89820676786453 lon=12.47644220919742 heading=0.8815613985061646 pitch=89.001953125 roll=0.1744659692049026 date='2019-08'
```

## Get Metadata

Not all panoramas will have a `date` field in the search results. You can fetch a date for any valid panorama from the metadata api:

```python
from streetview import get_panorama_meta

meta = get_panorama_meta(pano_id='_R1mwpMkiqa2p0zp48EBJg', api_key=GOOGLE_MAPS_API_KEY)

print(meta)
# date='2019-08' location=Location(lat=41.89820659475458, lng=12.47644649615282) pano_id='_R1mwpMkiqa2p0zp48EBJg'
```
## Download streetview image

You can then use the panorama ids to download streetview images:
```python
from streetview import get_streetview

image = get_streetview(
    pano_id="z80QZ1_QgCbYwj7RrmlS0Q",
    api_key=GOOGLE_MAPS_API_KEY,
)

image.save("image.jpg", "jpeg")
```

## Download panorama

You can download a full panorama like this:

```python
from streetview import get_panorama

image = get_panorama(pano_id="z80QZ1_QgCbYwj7RrmlS0Q")

image.save("image.jpg", "jpeg")
```

# Development

Run tests with:
```bash
make test
```
this will install mamba and the required Python packages into a local env.

If you want to rebuild VCR cassettes, you will need to copy `.env-example` to `.env` and add your Google Maps API Key.
