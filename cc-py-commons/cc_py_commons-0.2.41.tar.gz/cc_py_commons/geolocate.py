import googlemaps

from cc_py_commons.config.env import app_config
from cc_py_commons.utils.redis import location_db_conn, distance_db_conn, timezone_db_conn
from ast import literal_eval

def get_location(city, state, zipcode, logger):
  from_cache = False
  pc_miler_can_be_called = False
  data = __get_location_from_cache(city, state, zipcode, logger)

  if data and data.get('postcode') and data.get('country'):
    from_cache = True
  else:
    data = None

  if not data:
    logger.debug(f"geolocate.get_location - Couldn't find location: {city},{state} {zipcode} in cache.")
    data = __get_google_location(city, state, zipcode, logger)

  if data:
    if not from_cache:
      __cache_location(city, state, zipcode, data, logger)
  else:
    logger.debug(f"geolocate.get_location - Google returned no result for ({city}, {state}, {zipcode})")

  return data

def get_distance(origin_latitude, origin_longitude, destination_latitude, destination_longitude, logger):
  if not origin_latitude or not origin_longitude or \
    not destination_latitude or not destination_longitude:
    raise Exception("Calculating distance requires both origin and destination lat/lng")

  from_cache = False
  pc_miler_can_be_called = False
  distance_cache_key = __get_distance_cache_key(origin_latitude, origin_longitude, destination_latitude, destination_longitude)
  distance = __get_distance_from_cache(distance_cache_key, logger)

  if distance:
    from_cache = True

  if not distance:      
    distance = __get_google_distance(origin_latitude, origin_longitude, destination_latitude, destination_longitude, logger)

  if distance:
    if not from_cache:
      __cache_distance(distance_cache_key, distance, logger)
  else:
    logger.debug(f"geolocate.get_distance - Google returned no result for {distance_cache_key}")

  return distance

def get_timezone(lat,lng, logger):
  from_cache = False
  timezone = None
  try:
    timezone_cache_key = __get_timezone_cache_key(lat, lng)
    timezone = __get_timezone_from_cache(timezone_cache_key, logger)
    if timezone:
      from_cache = True

    if not timezone:
      gmaps = googlemaps.Client(key=app_config.GOOGLE_API_KEY)
      timezone = gmaps.timezone((lat,lng))

    if timezone and not from_cache:
      __cache_timezone(timezone_cache_key, timezone, logger)
  except googlemaps.exceptions.Timeout as e:
    msg = "geolocate.get_timezone - Timezone lookup failed {0}, {1}: {2}".format(lat, lng, e)
    if logger:
      logger.error(msg)
    else:
      print(msg)

  return timezone

def __get_google_distance(origin_latitude, origin_longitude, destination_latitude, destination_longitude, logger):
  distance = None
  try:
    gmaps = googlemaps.Client(key=app_config.GOOGLE_API_KEY)
    origins = [f'{origin_latitude} {origin_longitude}']
    destinations = [f'{destination_latitude} {destination_longitude}']
    response = gmaps.distance_matrix(origins,destinations,mode="driving",units="imperial")
    if response and response['rows'][0]['elements'][0].get('distance', None):
      distance_in_meters = response['rows'][0]['elements'][0]['distance']['value']
      distance = distance_in_meters / 1609
  except Exception as e:
    logger.error("geolocate.__get_google_distance: Error while getting distance from google", e)
    distance = None
  return distance

def __get_google_location(city, state, zipcode, logger):
  try:
    loc_str = ''

    if city:
      loc_str = city

    if state:
      if len(loc_str) > 0:
        loc_str = loc_str + ', '

      loc_str = loc_str + state

    if zipcode:
      if len(loc_str) > 0:
        loc_str = loc_str + ' '

      loc_str = loc_str + zipcode

    def __parse_response(response):
      if not response or len(response) == 0:
        return None
      ''' 
        Sample response of Google Maps API for address: Cincinati, OH, 45204
        {
            "address_components": [
                {
                    "long_name": "45204",
                    "short_name": "45204",
                    "types": [
                        "postal_code"
                    ]
                },
                {
                    "long_name": "Cincinnati",
                    "short_name": "Cincinnati",
                    "types": [
                        "locality",
                        "political"
                    ]
                },
                {
                    "long_name": "Hamilton County",
                    "short_name": "Hamilton County",
                    "types": [
                        "administrative_area_level_2",
                        "political"
                    ]
                },
                {
                    "long_name": "Ohio",
                    "short_name": "OH",
                    "types": [
                        "administrative_area_level_1",
                        "political"
                    ]
                },
                {
                    "long_name": "United States",
                    "short_name": "US",
                    "types": [
                        "country",
                        "political"
                    ]
                }
            ],
            "formatted_address": "Cincinnati, OH 45204, USA",
            "geometry": {
                "bounds": {
                    "northeast": {
                        "lat": 39.1251898,
                        "lng": -84.539683
                    },
                    "southwest": {
                        "lat": 39.073286,
                        "lng": -84.62870989999999
                    }
                },
                "location": {
                    "lat": 39.0930395,
                    "lng": -84.56676650000001
                },
                "location_type": "APPROXIMATE",
                "viewport": {
                    "northeast": {
                        "lat": 39.1251898,
                        "lng": -84.539683
                    },
                    "southwest": {
                        "lat": 39.073286,
                        "lng": -84.62870989999999
                    }
                }
            },
            "place_id": "ChIJjYEP0hK2QYgRTJoYykoQeqw",
            "postcode_localities": [
                "Cincinnati",
                "Queen City Square"
            ],
            "types": [
                "postal_code"
            ]
        }
      '''
      components = response[0]['address_components']
      types = response[0]['types']
      location = response[0]['geometry']['location']
      postcode_localities = response[0].get('postcode_localities', None)

      data = { 'city': None, 'state': None, 'postcode': None }
      data['lat'] = location['lat']
      data['lng'] = location['lng']

      # when checking the response for a zipcode verify the city name is in the list of localities
      if 'postal_code' in types and postcode_localities and city:
        matches = [l for l in components if (
                    'postal_localities' in l.get('types') and
                    (l.short_name.lower() == city.lower() or l.long_name.lower() == city.lower())
        )]
        city_present_in_postcode_localities = (city in postcode_localities)

        if not matches and not city_present_in_postcode_localities:
          return None

      for component in components:
        if 'locality' in component['types']:
          data['city'] = component['short_name']
        elif 'administrative_area_level_1' in component['types']:
          data['state'] = component['short_name']
        elif 'postcode' in component['types'] or 'postal_code' in component['types']:
          data['postcode'] = component['short_name']
        elif 'country' in component['types']:
          data['country'] = component['short_name']

      return data

    gmaps = googlemaps.Client(key=app_config.GOOGLE_API_KEY)
    response = gmaps.geocode(loc_str)
    
    if response:
      if len(response) > 1:
        logger.warning(f"Google returned multiple matches for {loc_str}")
        return None

      data = __parse_response(response)
      
      # For some locals like neighborhood google does not return postal_code
      ## if zipcode is present run it only and verify against city
      if data and not data['postcode'] and zipcode:
        response = gmaps.geocode(zipcode)
        post_code_data = __parse_response(response)
        data['postcode'] = post_code_data['postcode'] if post_code_data else None
      
      return data
  except googlemaps.exceptions.Timeout as e:
    msg = "geolocate.__get_google_location - Location lookup timed out {0}, {1}, {2}: {3}".format(city, state, zipcode, e)

    if logger:
      logger.error(msg)
    else:
      print(msg)
  except googlemaps.exceptions.HTTPError as e:
    msg = "geolocate.__get_google_location - Location lookup failed {0}, {1}, {2}: {3}".format(city, state, zipcode, e)

    if logger:
      logger.error(msg)
    else:
      print(msg)

  return None

def __cache_location(city, state, zipcode, location_data, logger):
  location_string = __get_location_string(city, state, zipcode)
  location_db_conn.set(location_string, str(location_data))

def __get_location_from_cache(city, state, zipcode, logger):
  location = None
  try:
    location_string = __get_location_string(city, state, zipcode)
    location = location_db_conn.get(location_string)
    if location:
      location = literal_eval(location.decode('utf-8'))
  except Exception as e:
    logger.warn("geolocate.__get_location_from_cache: Error while getting location from cache", e)
    location = None
  return location

def __get_location_string(city, state, zipcode):
  location_string = ''
  if city:
    location_string += ('_'.join(city.split(' ')))
  if state:
    location_string += f'_{state}'
  if zipcode:
    location_string += f'_{zipcode}'

  return location_string.lower()

def __cache_distance(distance_cache_key, distance, logger):
  distance_db_conn.set(distance_cache_key, distance)

def __get_distance_from_cache(distance_cache_key, logger):
  distance = None
  try:
    distance = distance_db_conn.get(distance_cache_key)
    if distance:
      distance = float(distance)
  except Exception as e:
    logger.warn("geolocate.__get_distance_from_cache: Error while getting distance from cache", e)
    distance = None
  return distance

def __get_distance_cache_key(origin_latitude, origin_longitude, destination_latitude, destination_longitude):
  return f'{__truncate(origin_latitude)},{__truncate(origin_longitude)}->{__truncate(destination_latitude)},{__truncate(destination_longitude)}'

def __truncate(number):
  return int(number * 1000000) / 1000000

def __cache_timezone(timezone_cache_key, timezone, logger):
  timezone_db_conn.set(timezone_cache_key, timezone)

def __get_timezone_from_cache(timezone_cache_key, logger):
  timezone = None
  try:
    timezone = timezone_db_conn.get(timezone_cache_key)
    if timezone:
      timezone = literal_eval(timezone.decode('utf-8'))
  except Exception as e:
    logger.warn("geolocate.__get_timezone_from_cache - Error while getting timezone from cache", e)
    timezone = None
  return timezone

def __get_timezone_cache_key(lat,lng):
  return f'{lat},{lng}'
