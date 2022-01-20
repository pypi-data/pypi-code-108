import csv
import os

list_path = os.path.join(os.path.dirname(__file__), "list.csv")


class TelemetryWhitelist(object):
    def __init__(self):
        self._data = set()
        with open(list_path, "r") as fd:
            whitelist_reader = csv.DictReader(fd)
            for row in whitelist_reader:
                self._data.add(row["appid"])

    def __contains__(self, value):
        return value in self._data


telemetry_whitelist = TelemetryWhitelist()
