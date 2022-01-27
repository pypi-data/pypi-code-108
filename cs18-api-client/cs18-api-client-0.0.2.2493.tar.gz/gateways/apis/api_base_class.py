class ApiBase:
    def __init__(self, api_address: str, version: str = None):
        _version = "/v{}".format(version) if version else ""
        self._root = "{api_address}/api{_version}".format(**locals())

    def build_route(self, route: str):
        return "{root}/{route}".format(root=self._root, route=route)
