from replifactory.GUI.experiment_program_tab import ExperimentProgramTab
from replifactory.GUI.status_bar import StatusBar
import ipywidgets as widgets
from ipywidgets import HBox
from replifactory.GUI.device_tab import DeviceTab
from replifactory.GUI.calibration_tab import CalibrationTab
from replifactory.GUI.camera_tab import CameraTab
from replifactory.GUI.graph_tab import ExperimentPlotTab
import os
from replifactory.GUI.experiment_status_tab import ExperimentStatusTab


class MainGui:
    def __init__(self):
        global _main_gui
        if "_main_gui" in globals().keys():

            q = input("initialize new GUI?[y/n]")
            if q == "y":
                _main_gui = self
            else:
                raise RuntimeError("Existing GUI was NOT overwritten by new GUI")
        self._device = None
        self._experiment = None

        self.status_bar = StatusBar(main_gui=self)

        self.device_tab = DeviceTab(main_gui=self)
        self.experiment_tab = ExperimentProgramTab(main_gui=self)
        self.photo_tab = CameraTab()
        self.device_config_tab = CalibrationTab(main_gui=self)
        self.experiment_status_tab = ExperimentStatusTab(main_gui=self)
        self.experiment_plot_tab = ExperimentPlotTab(main_gui=self)
        self.tab_list = [self.experiment_tab, self.device_tab, self.device_config_tab,
                         self.experiment_status_tab, self.experiment_plot_tab, self.photo_tab]
        self.tabs = widgets.Tab()

        self.widget = HBox([self.status_bar.widget, self.tabs])
        self.update()
        _main_gui = self

    def update(self):
        self.status_bar.update()
        self.tabs.children = [tab.widget for tab in self.tab_list]
        for i in range(len(self.tab_list)):
            self.tabs.set_title(i, self.tab_list[i].title)
        for c in self.tabs.children:
            c.layout = widgets.Layout(width="800px")
        self.reload_status_bar_widget()

    def reload_status_bar_widget(self):
        self.widget = HBox([self.status_bar.widget, self.tabs])

    @property
    def device(self):
        if self.experiment is None:
            return self._device
        else:
            return self.experiment.device

    @device.setter
    def device(self, device):
        if self.experiment is not None:
            if device is not None:

                # if device.directory is None:
                #     device.directory = self.experiment.directory


                self.experiment.device = device
        self._device = device
        if device is not None:
            self.device_config_tab.update()

    @property
    def experiment(self):
        return self._experiment

    @experiment.setter
    def experiment(self, experiment):
        self._experiment = experiment
        if self.experiment.device is not None:
            # self.device = self.experiment.device
            if self.device.__class__ in self.device_tab.device_class.options:
                self.device_tab.device_class.index = self.device_tab.device_class.options.index(self.device.__class__)
            else:
                print("Experiment config device class unknown.")
            if self.device.ftdi_address in self.device_tab.ftdi_address.options:
                self.device_tab.ftdi_address.index = self.device_tab.ftdi_address.options.index(self.device.ftdi_address)
            else:
                print("Experiment config FTDI address does not match connected devices.")
            # config_paths = [p for p in self.status_bar.config_path.options if
            #                 os.path.realpath(p).startswith(os.path.realpath(self.device.directory))]
            # if len(self.status_bar.config_paths) > 0:
            #     self.device_tab.config_path.index = self.device_tab.config_path.options.index(config_paths[0])
            # else:
            #     print("Experiment config device directory unknown.")
        else:
            if self._device is not None:
                self.experiment.device = self._device
                print("New device associated with experiment.")

# class Tabs:
#     def __init__(self, main_gui):
#         self.main_gui = main_gui
#         self.widget = widgets.Tab()
#         self.device_tab = DeviceTab(self.main_gui)
#         self.experiment_tab = ProgramViewerTab(experiment=self.main_gui.experiment)
#
#         self.tab_list = [self.device_tab, self.experiment_tab]
#         self.update()
#
#     def update(self):
#         self.widget.children = [tab.widget for tab in self.tab_list]
#         for i in range(len(self.tab_list)):
#             self.widget.set_title(i, self.tab_list[i].title)

    # self.widget.children = [DeviceControl(None).widget,
        #                         ProgramViewerTab(None).widget]
        # self.widget.children = [DeviceControl(device=self.main_gui.device).widget,
        #                         ProgramViewerTab(experiment=self.main_gui.experiment).widget]
        # self.widget.set_title(0, "Control")
        # self.widget.set_title(1, "Program viewer")


# class NewExperimentWidget:
#     def __init__(self):
#         textbox = widgets.Text(description="New experiment:", value="experiment name", continuous_update=False,
#                                style={'description_width': 'initial'})
#         self.widget = interactive(self.make_new_experiment, experiment_name=textbox)
#
#
#     def make_new_experiment(self, experiment_name):
#         if experiment_name != "experiment name":
#             if experiment_name not in os.listdir("."):
#                 os.mkdir(experiment_name)
#                 experiment_path = os.path.join(os.getcwd(), experiment_name)
#                 experiment_name = os.path.realpath(experiment_path)
#                 print("Initialized experiment in directory\n", experiment_name)
#             else:
#                 raise FileExistsError


