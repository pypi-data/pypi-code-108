import threading
from copy import deepcopy

from RainbowMonitoringSDK.probes.Metric import SimpleMetric
from RainbowMonitoringSDK.probes.Probe import Probe
from flask import request, Flask


class ServerAppMetricsProbe(Probe):

    latest_metrics = []
    app = Flask(__name__)
    def __init__(self,
                 periodicity, debug=False, _logging=False,
                 **kwargs):
        Probe.__init__(self, "ServerAppMetricsProbe", periodicity,  debug, _logging )
        self.config = kwargs
        threading.Thread(target=ServerAppMetricsProbe.start_stand_by_server, args=[self]).start()

    def get_desc(self):
        return "The monitoring probe of user defined metrics"

    def collect(self):
        json_metrics = self.retrieve_metrics()
        for _metric in json_metrics:
            metric = self.__metric_from_dictionary(_metric)
            self.add_metric(metric)

    @staticmethod
    def __metric_from_dictionary(collected):
        metric = SimpleMetric(collected.get('name'), collected.get('units'), collected.get('desc'))
        metric.set_val(collected.get('val'))
        metric.set_group(collected.get('group'))
        return metric

    def retrieve_metrics(self):
        res = deepcopy(self.latest_metrics)
        self.latest_metrics = []
        return res

    def get_metrics(self):
        self.collect()
        return Probe.get_metrics(self)

    def start_stand_by_server(self):
        path = self.config.get("path", "/")
        port = self.config.get("port", "1090")
        @self.app.route(path, methods=["POST"])
        def main_route():
            data = request.json
            if type(data) != dict: return {"success": False}
            for param in ['name', 'units', 'desc', 'val', 'group']:
                if data.get(param) == None: return {"success": False}

            self.latest_metrics.append(data)
            return {"success": True}
        self.app.run(host="0.0.0.0", port=port)