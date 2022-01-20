from flask import Flask

from RainbowMonitoringSDK.exporters.Exporter import Exporter


class RestAPIExporter(Exporter):
    """
    API extractor class. This extractor provides an API where other services can request it
    """

    def __init__(self, port: int, path: str):
        self.port = port
        self.path = path
        self.data = {}
        self.app = Flask(__name__)
        self.__initialize_routes()
        Exporter.__init__(self, "RestAPIExporter")

    def __initialize_routes(self):
        @self.app.route(self.path)
        def main_route():
            print(self.data)
            return self.data

    def run(self):  # run a server that can accept requests
        self.app.run(host="0.0.0.0", port=self.port)

    def update(self, data: dict):
        data = Exporter.update(self, data)
        self.data.update(data)
        return data
