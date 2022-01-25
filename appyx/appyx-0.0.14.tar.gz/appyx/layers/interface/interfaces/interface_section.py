class HTTPInterfaceSection:
    def __init__(self, endpoints, name) -> None:
        self._endpoints = endpoints
        self._name = name

    def endpoints(self):
        return self._endpoints

    def name(self):
        return self._name
