from msgraphy.data.monitor import Monitor, AsyncJobStatus


class MonitorGraphApi:

    def __init__(self, api):
        self._api = api

    def get_status(self, monitor: Monitor):
        return self._api.client.make_request(url=monitor.location, use_auth=False, response_type=AsyncJobStatus)
