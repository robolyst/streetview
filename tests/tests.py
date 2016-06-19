import sys
import nose
import streetview2 as streetview


def test__panoids_data():

	lat = -33.8796052
	lon = 151.1655341

	resp = streetview._panoids_data(lat, lon)

	assert resp.status_code == 200
	assert len(resp.text) > 10000


def test_extract_correct_panoid_and_dates():
    
    # Converts the panoids dictionary to a string
    def format(info):
        return  " : ".join(["%s %d %d" % (i['panoid'], i['year'], i['month']) for i in info[::-1] if 'year' in i])

    # Check to make sure that the panoids are matched with the right dates
    lat = -33.8772851
    lon = 151.1680999
    info = streetview.panoids(lat, lon)
    correct = "-qYBkMMcizSkvAlOQycuUQ 2014 4 : MqmnY5liP8KZ7ARbQReK2w 2013 7 : KbLn6JUJgGEH5PlS2PqEdQ 2009 12 : QXWvZA0iAkym7rIeepaXIQ 2007 11"
    assert correct in format(info)
    
    lat = 52.4031729
    lon = -1.5491263
    info = streetview.panoids(lat, lon)
    correct = "kA7IlR8AraikrwDNockDgQ 2015 9 : 0Ij4F_ykgshzUeJggW2NlA 2014 7"
    
    print format(info)
    assert correct in format(info)