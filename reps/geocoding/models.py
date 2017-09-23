from django.db import models
from helpers import get_lat_lng
import usaddress


class CachedAddress(models.Model):
    # Address that seeded this record:
    address_string = models.CharField(max_length=200)
    # Geocoded coordinates:
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    # Parsed address components:
    postal_code = models.IntegerField(null=True)
    address_number = models.CharField(max_length=200, null=True)
    street_name = models.CharField(max_length=200, null=True)
    street_name_post_type = models.CharField(max_length=32, null=True)
    place_name = models.CharField(max_length=200, null=True)
    state_name = models.CharField(max_length=32, null=True)
    zip_code = models.CharField(max_length=32, null=True)

    def save(self, *args, **kwargs):
        # Parse address into components if necessary:
        if not all([self.address_number, self.street_name, self.street_name_post_type, self.place_name, self.state_name, self.zip_code]):
            # Remove some characters we don't want included:
            address_string = self.address_string
            for char in '.,':
                address_string = address_string.replace(char, '')

            # Parse address:
            parsed_address = usaddress.parse(address_string)
            # Turn this into a dictionary for convenience:
            parsed_address = {value: key for key, value in parsed_address}

            # TODO: there's a more pythonic way to do the following...
            if 'AddressNumber' in parsed_address:
                self.address_number = parsed_address['AddressNumber']
            if 'StreetName' in parsed_address:
                self.street_name = parsed_address['StreetName']
            if 'StreetNamePostType' in parsed_address:
                self.street_name_post_type = parsed_address['StreetNamePostType']
            if 'PlaceName' in parsed_address:
                self.place_name = parsed_address['PlaceName']
            if 'StateName' in parsed_address:
                self.state_name = parsed_address['StateName']
            if 'ZipCode' in parsed_address:
                self.zip_code = parsed_address['ZipCode']

        # Geocode if necessary:
        if not self.latitude or not self.longitude:
            lat_long = get_lat_lng(self.address_string)
            self.latitude = lat_long.split(',')[0]
            self.longitude = lat_long.split(',')[1]

        # Get legislators if necessary:
        # I have the "pyopenstates" package installed, but it doesn't appear to work correctly:
        #   pyopenstates.locate_legislators('36.191402','86.73449959999999')
        #   []
        # Instead, make a request like so:
        #   https://openstates.org/api/v1/legislators/geo/?lat=36.191402&long=-86.73449959999999
        #   Header: X-API-KEY=settings.OPENSTATES_API_KEY
        #
        # Next up: figure out how to store legislator info
        super(CachedAddress, self).save(*args, **kwargs)



# class CachedAddress(models.Model):
#     """
#     Geocoded address.
#     """
#     full_address = AddressField()
#     latlng = models.CharField(blank=True, max_length=100)

#     # def _get_full_address(self):
#     #     """
#     #     Geocode using full address
#     #     """
#     #     return u'%s %s %s %s %s %s' % (self.address_1, self.address_2, self.city, self.state, self.country, self.zipcode)
#     # full_address = property(_get_full_address)

#     def save(self, *args, **kwargs):
#         if not self.latlng:
#             if self.zipcode and self.country:
#                 location = self.geo_address
#                 self.latlng = get_lat_lng(location)
#             else:
#                 location = '+'.join(filter(None, (self.address_1, self.address_2, self.city, self.state, self.country)))
#                 self.latlng = get_lat_lng(location)
#         super(CachedAddress, self).save(*args, **kwargs)


class InputAddress(models.Model):
    """
    Address requested by a user. We save the "input string" as an additional
    caching layer, so we don't have to parse the same address multiple times.
    """
    input_string = models.CharField(max_length=200)
    cached_address = models.ForeignKey(CachedAddress)

    #def save(self, *args, **kwargs):
        # Find the CachedAddress we'll use for this record.
        # Round the street address to 100's, to "bucket" addresses
        # and reduce the number of geocoding queries:
        #...
        # Now find or create a related CachedAddress:
        #...
