#!/usr/bin/env python3

import json
import urllib.parse
import requests
import logging
from bs4 import BeautifulSoup

BASE_URL = "https://www.reseau-astuce.fr/fr/horaires-a-larret/28/StopTimeTable/NextDeparture"

class Request(object):
    def __init__(self, endpoint=BASE_URL, debug=False):
        self.logger = logging.getLogger('pymyastuce')
        self.logger.setLevel(logging.INFO)
        if debug:
            self.enableDebug()

    def enableDebug(self):
        self.logger.setLevel(logging.DEBUG)
        import http.client as http_client
        http_client.HTTPConnection.debuglevel = 1

        # You must initialize logging, otherwise you'll not see debug output.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    def buildTerminusJSON(self, line, station, direction):
        terminus = line.getTerminus(direction)
        self.logger.debug("Terminus: %s", str(terminus))
        obj = {}
        for i, val in enumerate(terminus):
            # We need to urlencode now to prevent json.dumps to convert special char to escaped UTF-8
            obj[str(i + 1)] = urllib.parse.quote(val)
        # We then decode once to restore the special chars
        j = json.dumps(obj).replace(" ", "")
        return urllib.parse.unquote(j)

    def getNextFormatter(self, text):
        soup = BeautifulSoup(text, 'html.parser')
        spans = soup.find_all('span', {"class": "item-text bold"})
        result = []
        for span in spans:
            if "dans" in span.text:
                span.span.abbr.decompose()
                result.append(span.span.text)
        return result

    def getNext(self, line, station, direction, raw=False):
        line_terminus = self.buildTerminusJSON(line, station, direction)
        params = {
            "destinations": line_terminus,
            "stopId": station.getPhysicalId(direction, line),
            "lineId": line.id,
            "sens": direction,
        }
        r = requests.post(BASE_URL, params=params)
        if raw:
            return r.text
        return self.getNextFormatter(r.text)
