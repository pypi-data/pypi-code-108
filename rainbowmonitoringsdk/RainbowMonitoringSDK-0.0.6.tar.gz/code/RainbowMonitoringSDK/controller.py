import logging
import os
import RainbowMonitoringSDK.exporters as exporters
import RainbowMonitoringSDK.probes as probes
import time

from RainbowMonitoringSDK.utils.basics import time_to_seconds


class Controller(object):
    """
    The controller is responsible to orchestrate the execution of:
    - Sensing Units (Metric Collectors)
    - Dissemination Units
    """
    sensing_units: dict = {}
    dissemination_units: dict = {}
    configs: dict = {}

    def __init__(self, configs: dict = {}):
        self.configs = configs
        node_id = os.getenv('NODE_ID', self.configs.get('node_id', None))
        if not node_id: raise Exception("The node id is not defined")
        os.environ['NODE_ID'] = node_id

    def instantiate_sensing_units(self):
        """
        This function instantiates the sensing units and initialize their parameters
        :return:
        """
        res = self.configs['sensing-units'] if 'sensing-units' in self.configs else {}
        for i in res:
            metric_collector_class = getattr(probes, i, None)
            if metric_collector_class:
                print("Sensing Unit %s is instantiating" % i)
                current_conf = self.configs['sensing-units'][i]
                current_conf['periodicity'] = time_to_seconds(current_conf['periodicity'])
                self.sensing_units[i] = metric_collector_class(**current_conf)

    def instantiate_dissemination_units(self):
        """
        It instantiates the dissemination channels and injects their configuration parameters
        :return:
        """
        res = self.configs['dissemination-units'] if 'dissemination-units' in self.configs else {}
        for i in res:
            extractor_class = getattr(exporters, i, None)
            if extractor_class:
                print("Dissemination Unit %s is instantiating" % i)
                self.dissemination_units[i] = extractor_class(**self.configs['dissemination-units'][i])

    def start_sensing_units(self):
        """
        Starts, if it is necessary, the threads of the sensing units
        :return:
        """
        for i in self.sensing_units:
            print("Sensing Unit %s is starting" % i)
            self.sensing_units[i].activate()

    def start_dissemination_units(self):
        """
        Starts, if it is necessary, the dissemination channels connections e.g. starting Restful server, connection with kafka, etc
        :return:
        """
        for i in self.dissemination_units:
            print("Dissemination Unit %s is starting" % i)
            self.dissemination_units[i].activate()

    def start_control(self):  # TODO update it to encaptulate Queue
        """
        The main control loop of the monitoring system.
        In the loop, system captures one-by-one all metrics from metric collectors, combines them and
        disseminates them to all channels.
        :return:
        """
        running = True
        while running:
            try:
                res = {}
                for i in self.sensing_units:
                    sensing_unit = self.sensing_units[i]
                    metrics = sensing_unit.get_metrics()
                    res.update({i: metrics})
                    # sensing_unit.update()  # TODO Add adaptiveness functionality to update
                for i in self.dissemination_units:
                    self.dissemination_units[i].update(res)
                periodicity = self.configs['sensing-units']['general-periodicity']
                time.sleep(time_to_seconds(periodicity))
            except Exception as ex:
                logging.error("Error at start_control",
                              exc_info=True)
                print(ex)
        exit(0)
