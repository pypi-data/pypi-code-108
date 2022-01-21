"""This is a reader for openweathermap (https://openweathermap.org) historical weather files.

Author: stephane.ploix@grenoble-inp.fr
"""
from buildingenergy import timemg
import json

class OpenWeatherMapJsonReader:
    """Extract the content of a json openweather data file.

    :param json_filename: openweather data file in json format
    :param from_stringdate: initial date in format DD/MM/YYYY hh:mm:ss
    :param to_stringdate: final date in format DD/MM/YYYY hh:mm:ss
    :return: a tuple containing
        - city file_name
        - latitude in decimal north degree
        - longitude in decimal east degree
        - hourly time data variables as a dictionnary with variable file_name as a key
        - units as a dictionnary with variable file_name as a key
        - initial date as a string
        - final date as a string
    """

    def __init__(self, json_filename, from_stringdate=None, to_stringdate=None, sea_level_in_meter=290, albedo=.1, pollution=0.1):
        """Read data from an openweather map json file.

        :param json_filename: name of the openweathermap historical weather file
        :type json_filename: str
        :param from_stringdate: starting date for the data collection, defaults to None
        :type from_stringdate: str, optional
        :param to_stringdate: ending date for the data collection, defaults to None
        :type to_stringdate: str, optional
        :param sea_level_in_meter: sea level in meter of the site location, defaults to 290
        :type sea_level_in_meter: float, optional
        :param albedo: albedo at current site location (see https://en.wikipedia.org/wiki/Albedo), defaults to .1
        :type albedo: float, optional
        :param pollution: turbidity coefficient to model the air pollution at the current site location, defaults to 0.1
        :type pollution: float, optional
        """
        if from_stringdate is not None:
            from_epochtimems = timemg.stringdate_to_epochtimems(from_stringdate)
        if to_stringdate is not None:
            to_epochtimems = timemg.stringdate_to_epochtimems(to_stringdate)

        with open(json_filename) as json_file:
            weather_records = json.load(json_file)
            location = weather_records[0]['city_name']
            latitude_in_deg = float(weather_records[0]['lat'])
            longitude_in_deg = float(weather_records[0]['lon'])
            variable_names = ('epochtimems', 'temperature', 'wind_speed', 'wind_direction_in_deg', 'feels_like', 'humidity', 'pressure', 'cloudiness', 'temp_min', 'temp_max', 'description')
            variable_units = {'epochtimems': 'ms', 'temperature': 'celcius', 'wind_speed': 'm/s', 'wind_direction_in_deg': 'degree', 'feels_like': 'celcius', 'humidity': 'percent', 'pressure': 'hPa', 'cloudiness': 'percent', 'temp_min': 'celcius', 'temp_max': 'celcius', 'description': 'text'}
            self._site_weather_data = SiteWeatherData(location, latitude_in_deg, longitude_in_deg, variable_names, variable_units, sea_level_in_meter=sea_level_in_meter, albedo=albedo, pollution=pollution, _direct_call=False)

            for _record in weather_records:
                _epochtimems = int(_record['dt']) * 1000
                if from_stringdate is not None and _epochtimems >= from_epochtimems and from_stringdate is not None and _epochtimems <= to_epochtimems:
                    _temperature = float(_record['main']['temp'])
                    _wind_speed = float(_record['wind']['speed'])
                    _wind_direction_in_deg = float(_record['wind']['deg'])
                    _feels_like = float(_record['main']['feels_like'])
                    _humidity = float(_record['main']['humidity'])
                    _pressure = float(_record['main']['pressure'])
                    _cloudiness = float(_record['clouds']['all'])
                    _temp_min = float(_record['main']['temp_min'])
                    _temp_max = float(_record['main']['temp_max'])
                    _description = ''
                    for weather_description in _record['weather']:
                        _description += weather_description['description'] + ', '
                    self._site_weather_data._add_row(_epochtimems, _temperature, _wind_speed, _wind_direction_in_deg, _feels_like, _humidity, _pressure, _cloudiness, _temp_min, _temp_max, _description[:-2])

    @property
    def site_weather_data(self):
        """Return the site weather data.

        :return: a SideData object containing all the information of a site (see SiteWeatherData)
        :rtype: a buildingenergy.SiteWeatherData object.
        """
        return self._site_weather_data


class SiteWeatherData:
    """Gathers all the data related to a site dealing with location, albedo, pollution, timezone but also weather timedata coming from an openweather json file."""

    def __init__(self, location, latitude_in_deg, longitude_in_deg,
variable_names, variable_units, sea_level_in_meter=290, albedo=.1, timezone='Europe/Paris', pollution=0.1, _direct_call=True):
        """Create object containing data dealing with a specific site, including the weather data.

        :param location: name of the site
        :type location: str
        :param latitude_in_deg: latitude in East degree
        :type latitude_in_deg: float
        :param longitude_in_deg: longitude in North degree
        :type longitude_in_deg: float
        :param variable_names: name of the weather variables
        :type variable_names: tuple[str]
        :param variable_units: units of the weather variables
        :type variable_units: tuple[str]
        :param sea_level_in_meter: altitude of the site in meter from sea level, defaults to 290
        :type sea_level_in_meter: float, optional
        :param albedo: albedo of the site, defaults to .1
        :type albedo: float, optional
        :param timezone: timezone of the site, defaults to 'Europe/Paris'
        :type timezone: str, optional
        :param pollution: pollution coefficient between 0 and 1, defaults to 0.1
        :type pollution: float, optional
        :param _direct_call: internal use to prohibit direct calls of the initializer, defaults to True
        :type _direct_call: bool, optional
        :raises PermissionError: raised in case of direct use, the object must be created by OpenWeatherMapJsonReader
        """
        if _direct_call:
            raise PermissionError('SiteWeatherData cannot be called directly')
        self._location = location
        self._latitude_in_deg = latitude_in_deg
        self._longitude_in_deg = longitude_in_deg
        self._sea_level_in_meter = sea_level_in_meter
        self._albedo = albedo
        self._pollution = pollution
        self._timezone = timezone
        self._variable_names : tuple[str] = variable_names
        self._variable_units: tuple[str] = variable_units
        self._from_epochtimems = None
        self._to_epochtimems = None
        self._variable_data = dict()
        for variable_name in variable_names:
            self._variable_data[variable_name] = []
        self._cache = dict()
        self._cache_from_epochtimems = None
        self._cache_to_epochtimems = None

    @property
    def location(self):
        """Return the site name.

        :return: name of the site
        :rtype: str
        """
        return self._location

    @property
    def latitude_in_deg(self):
        """Return the latitude of the site in East degrees.

        :return: latitude of the site in East degrees
        :rtype: float
        """
        return self._latitude_in_deg

    @property
    def longitude_in_deg(self):
        """Return the longitude of the site in North degrees.

        :return: longitude of the site in North degrees
        :rtype: float
        """
        return self._longitude_in_deg

    @property
    def sea_level_in_meter(self):
        """Return the altitude of the site in meters from sea level.

        :return: altitude of the site
        :rtype: float
        """
        return self._sea_level_in_meter

    @property
    def albedo(self):
        """Return the albedo of the site.

        :return: albedo coefficient of the ground between 0 and 1
        :rtype: float
        """
        return self._albedo

    @property
    def pollution(self):
        """Return the air turbidity of the site as a coefficient.

        :return: pollution coefficient between 0 and 1
        :rtype: float
        """
        return self._pollution

    @property
    def timezone(self):
        """Return the site administrative time zone.

        :return: the timezone of the site
        :rtype: str
        """
        return self._timezone

    @property
    def variable_names(self):
        """Return the available weather variables.

        :return: list of the available weather variables
        :rtype: list[str]
        """
        return self._variable_names

    def unit(self, variable_name):
        """Return the unit of a variable.

        :param variable_name: file_name of the variable
        :type variable_name: str
        :return: unit of this variable
        :rtype: str
        """
        return self._variable_units[variable_name]

    @property
    def from_stringdate(self):
        """Return the starting data of the data collection.

        :return: first date where data are available in epoch time (ms)
        :rtype: int
        """
        return timemg.epochtimems_to_stringdate(self._from_epochtimems)

    @property
    def to_stringdate(self):
        """Return the ending date of the data collection.

        :return: last date where data are available
        :rtype: str
        """
        return timemg.epochtimems_to_stringdate(self._to_epochtimems)

    def _add_row(self, *variable_values):
        """Add a row to the weather data collection.

        Internal usage: must not be used directly

        :param variable_values: a list of values correspong to a row in the json openweather file
        :type variable_values: list[float]
        """
        epochtimems = variable_values[0]
        if self._from_epochtimems is None:
            self._from_epochtimems = epochtimems
            self._to_epochtimems = epochtimems
        elif epochtimems > self._to_epochtimems:
            self._to_epochtimems = epochtimems
        for i in range(len(variable_values)):
            self._variable_data[self._variable_names[i]].append(variable_values[i])

    def get(self, variable_name):
        """Return the data collection related to one variable.

        :param variable_name: variable file_name
        :type variable_name: str
        :return: list of float or str values corresponding to common dates for the specified variable
        :rtype: list[float or str]
        """
        if self._cache_from_epochtimems is not None and self._cache_from_epochtimems == self._from_epochtimems and self._cache_to_epochtimems == self._to_epochtimems and variable_name in self._cache:
            return self._cache[variable_name]
        _data = list()
        for i in range(len(self._variable_data['epochtimems'])):
            if self._from_epochtimems <= self._variable_data['epochtimems'][i] <= self._to_epochtimems:
                if variable_name == 'stringdate':
                    _data.append(timemg.epochtimems_to_stringdate(self._variable_data['epochtimems'][i]))
                elif variable_name == 'datetime':
                    _data.append(timemg.epochtimems_to_datetime(self._variable_data['epochtimems'][i]))
                else:
                    _data.append(self._variable_data[variable_name][i])
        if self._cache_from_epochtimems != self._from_epochtimems or self._cache_to_epochtimems != self._to_epochtimems:
            self._cache.clear()
        self._cache_from_epochtimems = self._from_epochtimems
        self._cache_to_epochtimems = self._to_epochtimems
        self._cache[variable_name] = _data
        return _data

    def day_degrees(self, temperature_reference=18, heat=True):
        """Compute heating or cooling day degrees and print in terminal the sum of day degrees per month.

        :param temperature_reference: reference temperature (default is 18°C)
        :param heat: True if heating, False if cooling
        :return: list of day dates as string, list of day average, min and max outdoor temperature and day degrees per day
        :rtype: [list[str], list[float], list[float], list[float], list[float]]
        """
        datetimes = self.get('datetime')
        stringdates = self.get('stringdate')
        temperatures = self.get('temperature')
        dd_months = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        day_stringdate_days = list()
        average_temperature_days = list()
        min_temperature_days = list()
        max_temperature_days = list()
        heat_degree_days = list()
        day_temperature = list()
        current_day = datetimes[0].day
        for k in range(len(datetimes)):
            if current_day == datetimes[k].day:
                day_temperature.append(temperatures[k])
            else:
                day_stringdate_days.append(stringdates[k-1].split(' ')[0])
                average_day_temperature = sum(day_temperature)/len(day_temperature)
                average_temperature_days.append(average_day_temperature)
                min_temperature_days.append(min(day_temperature))
                max_temperature_days.append(max(day_temperature))
                hdd = 0
                if heat:
                    if average_day_temperature < temperature_reference:
                        hdd = temperature_reference - average_day_temperature
                elif not heat:
                    if average_day_temperature > temperature_reference:
                        hdd = average_day_temperature - temperature_reference
                heat_degree_days.append(hdd)
                dd_months[datetimes[k].month-1] += hdd
                day_temperature = list()
            current_day = datetimes[k].day
        for i in range(len(dd_months)):
            print('day degrees', month_names[i], ': ', dd_months[i])
        return day_stringdate_days, average_temperature_days, min_temperature_days, max_temperature_days, heat_degree_days
