import os

from guide_bot.scan_visualization.interface_plot_sum import PlotSum
from guide_bot.scan_visualization.interface_compare_monitors_scan import CompareMonitorsScan
from guide_bot.scan_visualization.interface_compare_monitors import CompareMonitors
from guide_bot.scan_visualization.interface_any_monitor import PlotAnyMonitor
from guide_bot.scan_visualization.interface_guide_geometry import PlotGuideGeometry

from guide_bot.logging.overview import ScanOverview


class Results:
    def __init__(self, project_path):
        if not os.path.isdir(project_path):
            raise ValueError("Given path does not correspond to a directory!")

        self.project_path = os.path.abspath(project_path)
        self.overview = ScanOverview(self.project_path)
        self.overview.load_run_information()

        self.plot_sum_interface = None
        self.compare_monitors_scan_interface = None
        self.compare_monitors_interface = None
        self.plot_any_monitors_interface = None
        self.plot_guide_interface = None

    def get_guide_names(self):
        return self.overview.get_guide_names()

    def get_moderators(self):
        return self.overview.get_moderators()

    def get_shape(self):
        return self.overview.get_shape()

    def get_scanned_parameters(self):
        return self.overview.get_scanned_parameters()

    def show_scan(self):
        return self.overview.show_scan()

    def show_status_guide(self, guide):
        self.overview.guide_run_status(guide)

    def show_status(self):
        self.overview.run_status()

    def get_overview(self):
        return self.overview

    def get_plot_any_monitor(self):
        if self.plot_any_monitors_interface is None:
            self.plot_any_monitors_interface = PlotAnyMonitor(self.overview)

        return self.plot_any_monitors_interface

    def plot_any_monitor(self):
        interface = self.get_plot_any_monitor()
        return interface.show_interface()

    def get_compare_monitors(self):
        if self.compare_monitors_interface is None:
            self.compare_monitors_interface = CompareMonitors(self.overview)

        return self.compare_monitors_interface

    def compare_monitors(self):
        interface = self.get_compare_monitors()
        return interface.show_interface()

    def get_compare_monitors_scan(self):
        if self.compare_monitors_scan_interface is None:
            self.compare_monitors_scan_interface = CompareMonitorsScan(self.overview)

        return self.compare_monitors_scan_interface

    def compare_monitors_scan(self):
        interface = self.get_compare_monitors_scan()
        return interface.show_interface()

    def get_plot_sum(self):
        if self.plot_sum_interface is None:
            self.plot_sum_interface = PlotSum(self.overview)

        return self.plot_sum_interface

    def plot_sum(self):
        interface = self.get_plot_sum()
        return interface.show_interface()

    def get_plot_guide(self):
        if self.plot_guide_interface is None:
            self.plot_guide_interface = PlotGuideGeometry(self.overview)

        return self.plot_guide_interface

    def plot_guide(self):
        interface = self.get_plot_guide()
        return interface.show_interface()

