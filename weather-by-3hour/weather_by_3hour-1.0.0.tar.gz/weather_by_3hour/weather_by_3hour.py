import requests, pprint

# API_KEY = "6acfabc53c031834d981317a924a821d"



class Weather:
    """
    Create a Weather object getting an apikey as input and
    either a city name or lat and lon coordinates.

    Package use example:
    # Create a weather object using a city name:
    # The api key below is not guaranteed to work.
    # Get your own apikey from https://openweathermap.org
    # And wait a couple of hours for the apikey to be activated

    weather1 = Weather(apikey = "YOUR API KEY", city = "CITY")

    # Using latitude and longitude coordinates
    weather2 = Weather(apikey="YOUR API KEY", lat="LATITUDE", lon="LONGITUDE")

    # Get complete weather data for the next 12 hours:
    weather1.next_12h()

    #Simplied data for the next 12 hours:
    weather1.next_12h_simplified()

    """

    def __init__(self, apikey, city=None, lat=None, lon=None):
        """
        The constructor that construct the Weather Object.
        :param apikey:
        :param city:
        :param lat:
        :param lon:
        """

        if city: # city is provided
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={apikey}&units=metric"
            r = requests.get(url)
            self.data = r.json()
        elif lat and lon: # lat and lon are provided
            url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={apikey}&units=metric"
            r = requests.get(url)
            self.data = r.json()
        else: # no argument is provided
            raise TypeError("Provide either city or lat and lon arguments")

        if self.data['cod'] != '200':
            raise ValueError(self.data['message'])

    def next_12h(self):
        """
        returns data for the next 12hours at
        an interval of 3hours as a dict...
        """
        return self.data['list'][:4]

    def next_12h_simplified(self):
        """
        returns date, temperature and sky condition
        for the next 12hours at an interval of 3hours
        as a tuple of tuples...
        """
        simple_data = []
        for dict in self.data['list'][:4]:
            simple_data.append((dict['dt_txt'],
                                dict['main']['temp'],
                                dict['weather'][0]['description']))
        return simple_data


