SUCCESS = "success"
MESSAGE = "msg"
CONTENT = "content"

API_ENDPOINT = "https://api.luchtmeetnet.nl/open_api"  # no trailing slash

STATIONS_URL_TEMPLATE = (
    "%s/stations?page={page}&order_by=number&organisation_id=" % API_ENDPOINT
)
STATION_DATA_URL_TEMPLATE = "%s/stations/{number}/" % API_ENDPOINT
STATION_MEASUREMENTS_URL_TEMPLATE = (
    "%s/stations/{station}/measurements?order=timestamp_measured&order_direction=desc"
    % API_ENDPOINT
)
STATION_LKI_URL_TEMPLATE = (
    "%s/lki?station_number={station}&order_by=timestamp_measured&order_direction=desc"
    % API_ENDPOINT
)
