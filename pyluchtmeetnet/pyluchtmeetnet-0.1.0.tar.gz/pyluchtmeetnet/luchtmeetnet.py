import logging
import json
import sys
from math import cos, asin, sqrt

import requests

from .const import (
    CONTENT,
    MESSAGE,
    SUCCESS,
    STATIONS_URL_TEMPLATE,
    STATION_DATA_URL_TEMPLATE,
    STATION_MEASUREMENTS_URL_TEMPLATE,
    STATION_LKI_URL_TEMPLATE,
)

_LOGGER = logging.getLogger(__name__)


class Luchtmeetnet:
    def __init__(self):
        return None

    def get_nearest_station_data(self, latitude, longitude):
        _LOGGER.info("Get nearest station.")
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            _LOGGER.error("ValueError: Latitude and longitude are invalid floats.")
            return None

        location = {"latitude": latitude, "longitude": longitude}
        stations = self.__get_stations()
        return self.__closest(stations, location)

    def get_station_data(self, number):
        return self.__get_station_data(number)

    def get_latest_station_lki(self, station):
        _LOGGER.info("Get latest LKI for station %s" % station)
        data = {}
        result = self.__get_station_lki_json(station)
        if result[SUCCESS]:
            try:
                content = result[CONTENT]
                json_content = json.loads(content)
                measurements = json_content["data"]
                if len(measurements) > 0:
                    data = {
                        "LKI": measurements[0]["value"],
                        "timestamp": measurements[0]["timestamp_measured"],
                    }
                else:
                    _LOGGER.warn("No LKI found.")
            except json.JSONDecodeError as err:
                _LOGGER.error("Unable to parse content as json. %s", err)
        return data

    def get_latest_station_measurements(self, station):
        _LOGGER.info("Get latest measurements for station %s" % station)

        components = []
        result = self.__get_station_data_json(station)
        if result[SUCCESS]:
            try:
                content = result[CONTENT]
                json_content = json.loads(content)
                components = json_content["data"]["components"]
            except json.JSONDecodeError as err:
                _LOGGER.error("Unable to parse content as json. %s", err)

        result = self.__get_station_measurements_json(station)
        if result[SUCCESS]:
            try:
                content = result[CONTENT]
                json_content = json.loads(content)
                measurements = json_content["data"]
            except json.JSONDecodeError as err:
                _LOGGER.error("Unable to parse content as json. %s", err)

        data = []
        for component in components:
            json_component = [
                meas for meas in measurements if meas["formula"] == component
            ]
            element = {
                component: json_component[0]["value"],
                "timestamp": json_component[0]["timestamp_measured"],
            }
            data.append(element)

        _LOGGER.debug("Latest measurements:\n%s", data)
        return data

    def __get_stations(self):
        _LOGGER.info("Get all stations.")
        stations = []
        result = self.__get_stations_page_json(1)
        _LOGGER.debug("Result: %s", result)
        if result[SUCCESS]:
            try:
                _LOGGER.debug("Parse stations pages.")
                content = result[CONTENT]
                json_content = json.loads(content)
                for page in json_content["pagination"]["page_list"]:
                    page_result = self.__get_stations_page_json(page)
                    if page_result[SUCCESS]:
                        page_content = page_result[CONTENT]
                        page_json = json.loads(page_content)
                        for station in page_json["data"]:
                            element = self.__get_station_data(station["number"])
                            stations.append(element)
            except json.JSONDecodeError as err:
                result[MESSAGE] = "Unable to parse content as json. %s" % err
                _LOGGER.error(result[MESSAGE])

        return stations

    def __get_station_data(self, number):
        _LOGGER.info("Get station data.")
        result = self.__get_station_data_json(number)
        if result[SUCCESS]:
            content = result[CONTENT]
            json_content = json.loads(result[CONTENT])
            data = {
                "number": number,
                "longitude": json_content["data"]["geometry"]["coordinates"][0],
                "latitude": json_content["data"]["geometry"]["coordinates"][1],
                "location": json_content["data"]["location"],
                "municipality": json_content["data"]["municipality"],
                "organisation": json_content["data"]["organisation"],
                "description_nl": json_content["data"]["description"]["NL"],
                "description_en": json_content["data"]["description"]["EN"],
                "components": json_content["data"]["components"],
            }
            _LOGGER.debug(data)
        return data

    def __get_stations_page_json(self, page):
        _LOGGER.info("Get stations page %d.", page)
        result = {SUCCESS: False, MESSAGE: None}
        try:
            url = self.__json_stations_page_url(page)
            r = requests.get(url)
            if r.status_code == 200:
                result[SUCCESS] = True
                result[MESSAGE] = "%d: %s" % (r.status_code, r.reason)
                result[CONTENT] = r.text
            else:
                result[MESSAGE] = "Error retrieving stations page: %d - %s" % (
                    r.status_code,
                    r.reason,
                )
                _LOGGER.warn(result[MESSAGE])
        except requests.RequestException as rre:
            result[MESSAGE] = "Error retrieving stations page. %s" % rre
            _LOGGER.error(result[MESSAGE])

        _LOGGER.debug("Stations page result:\n%s", result)
        return result

    def __get_station_data_json(self, number):
        _LOGGER.info("Get station data.")
        result = {SUCCESS: False, MESSAGE: None}
        try:
            url = self.__json_station_data_url(number)
            r = requests.get(url)
            if r.status_code == 200:
                result[SUCCESS] = True
                result[CONTENT] = r.text
            else:
                result[MESSAGE] = "Error retrieving stations: %d - %s." % (
                    r.status_code,
                    r.reason,
                )
        except requests.RequestException as rre:
            result[MESSAGE] = "Error retrieving stations data. %s" % rre
            _LOGGER.error(result[MESSAGE])

        _LOGGER.debug("Station data result:\n%s", result)
        return result

    def __get_station_lki_json(self, number):
        result = {SUCCESS: False, MESSAGE: None, CONTENT: None}
        try:
            url = self.__json_station_lki_url(number)
            r = requests.get(url)
            if r.status_code == 200:
                result[SUCCESS] = True
                result[CONTENT] = r.text
            else:
                result[MESSAGE] = "Error retrieving LKI: %d - %s." % (
                    r.status_code,
                    r.reason,
                )
                _LOGGER.warn(result[MESSAGE])
        except requests.RequestException as rre:
            result[MESSAGE] = "Error retrieving LKI. %s" % rre
            log.error(result[MESSAGE])

        _LOGGER.debug("LKI result:\n%s", result)
        return result

    def __get_station_measurements_json(self, station):
        result = {SUCCESS: False, MESSAGE: None}
        try:
            url = self.__json_station_measurements_url(station)
            r = requests.get(url)
            if r.status_code == 200:
                result[SUCCESS] = True
                result[CONTENT] = r.text
            else:
                result[
                    MESSAGE
                ] = "Error retrieving latest station measurements: %d - %s" % (
                    r.status_code,
                    r.reason,
                )
                _LOGGER.warn(result[MESSAGE])
        except requests.RequestException as rre:
            result[MESSAGE] = "Error retrieving latest station measurements. %s" % rre
            _LOGGER.error(result[MESSAGE])

        _LOGGER.debug("Station measurements result:\n%s", result)
        return result

    def __json_stations_page_url(self, pagenumber) -> str:
        return STATIONS_URL_TEMPLATE.format(page=pagenumber)

    def __json_station_data_url(self, stationnumber) -> str:
        return STATION_DATA_URL_TEMPLATE.format(number=stationnumber)

    def __json_station_lki_url(self, stationnumber) -> str:
        return STATION_LKI_URL_TEMPLATE.format(station=stationnumber)

    def __json_station_measurements_url(self, stationnumber) -> str:
        return STATION_MEASUREMENTS_URL_TEMPLATE.format(station=stationnumber)

    def __distance(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = (
            0.5
            - cos((lat2 - lat1) * p) / 2
            + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
        )
        distance = 12742 * asin(sqrt(a))
        return distance

    def __closest(self, data, v):
        return min(
            data,
            key=lambda p: self.__distance(
                v["latitude"], v["longitude"], p["latitude"], p["longitude"]
            ),
        )
