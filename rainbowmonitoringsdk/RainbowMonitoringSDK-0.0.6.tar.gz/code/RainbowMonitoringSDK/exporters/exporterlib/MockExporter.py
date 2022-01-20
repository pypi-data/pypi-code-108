from venv import logger

from RainbowMonitoringSDK.exporters.Exporter import Exporter


class MockExporter(Exporter):

    def __init__(self, **kwargs):
        print("**initilization of MockExporter with params: %s"%str(kwargs))
        Exporter.__init__(self, name="mockexporter")


    def start(self):
        """
        Starts the extractor thread (if this is required)
        :return:
        """
        print("** start method of MockExporter is executed **")

    def dissemination_rate_adjustment(self, data: dict):
        print("** dissemination_rate_adjustment method of MockExporter is executed with %s data length **"%len(data))
        return data

    def update(self, data: dict):
        """
        Updates (prunes) the data based on specific logic (adaptive dissemination)
        :param data:
        :return:
        """
        print("** update method of MockExporter is executed with %s data **"%data)
        return data

    def run(self):
        print("** run method of MockExporter is executed**")
        pass
