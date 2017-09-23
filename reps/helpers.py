import simplejson
import urllib
from urllib.request import urlopen
from django.utils.encoding import smart_str


def get_lat_lng(location):
    """
    Reference: http://djangosnippets.org/snippets/293/
    """
    location = urllib.parse.quote_plus(smart_str(location))
    url = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false' % location
    response = urlopen(url).read()
    result = simplejson.loads(response)
    if result['status'] == 'OK':
        lat = str(result['results'][0]['geometry']['location']['lat'])
        lng = str(result['results'][0]['geometry']['location']['lng'])
        return '%s,%s' % (lat, lng)
    else:
        return ''
