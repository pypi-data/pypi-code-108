import copy

import matplotlib.pyplot as plt

from collections import OrderedDict

import ipywidgets as widgets
from IPython.display import display

from guide_bot.scan_visualization.jb_interface import HiddenPrints
from guide_bot.scan_visualization.jb_interface import BaseInterface

class CompareMonitorsScan(BaseInterface):
    def __init__(self, scan_overview):
        super().__init__(scan_overview)

        self.fig = None
        self.ax = None

        #self.show_interface()

        self.dropdown_monitor = None
        self.dropdown_run_name = None
        self.dropdown_moderator = None

        self.sample_scan_labels = None
        self.moderator_scan_labels = None

        self.selected_guide = self.guides_with_at_least_one_run[0]

        self.scan_par = None
        self.target = None

        sample_scan = self.get_scanned_sample_parameters()
        if len(sample_scan) > 0:
            self.target = "sample"
            self.scan_par = sample_scan[0]
            self.unit = self.get_scanned_sample_parameter_unit(self.scan_par)

        mod_scan = self.get_scanned_moderator_parameters()
        if len(mod_scan) > 0:
            self.target = "moderator"
            self.scan_par = mod_scan[0]
            self.unit = self.get_scanned_moderator_parameter_unit(self.scan_par)

    def set_guide(self, guide):
        if guide not in self.get_guide_names():
            raise KeyError("Need to select a guide available in the dataset!")

        self.selected_guide = guide

    def make_guide_selector(self):

        widget = widgets.RadioButtons(options=self.get_guide_names(),
                                      value=self.selected_guide,
                                      disabled=False, indent=True)

        widget.observe(self.update_guide_selector, "value")

        return widget

    def update_guide_selector(self, change):
        self.set_guide(change.new)
        self.update_plot()

    def set_scanned_par(self, par_name, target):

        if target not in ["sample", "moderator"]:
            raise KeyError("Target has to be either sample or moderator")

        self.target = target

        if target == "sample":
            if par_name not in self.get_scanned_sample_parameters():
                raise KeyError("Parameter not recognized in sample scan")
            self.scan_par = par_name
            self.unit = self.get_scanned_sample_parameter_unit(self.scan_par)

            if len(self.sample_scan_sliders) > 0:
                self.unlock_all_sliders()
                locked_slider = self.sample_scan_sliders[par_name]
                locked_slider.disabled = True

        elif target == "moderator":
            if par_name not in self.get_scanned_moderator_parameters():
                raise KeyError("Parameter not recognized in moderator scan")
            self.scan_par = par_name
            self.unit = self.get_scanned_moderator_parameter_unit(self.scan_par)

            if len(self.moderator_scan_sliders) > 0:
                self.unlock_all_sliders()
                locked_slider = self.moderator_scan_sliders[par_name]
                locked_slider.disabled = True

    def unlock_all_sliders(self):
        for key in self.sample_scan_sliders:
            self.sample_scan_sliders[key].disabled = False
        for key in self.moderator_scan_sliders:
            self.moderator_scan_sliders[key].disabled = False

    def make_dropdown_scan_par(self):

        sample_scan = self.get_scanned_sample_parameters()
        mod_scan = self.get_scanned_moderator_parameters()

        option_list = []
        self.option_to_par_and_target = {}
        for par_name in sample_scan:
            original_par_name = par_name
            par_name = "sample: " + par_name
            self.option_to_par_and_target[par_name] = (original_par_name, "sample")
            option_list.append(par_name)
            if self.target == "sample":
                if self.scan_par == original_par_name:
                    initial_value = par_name

        for par_name in mod_scan:
            original_par_name = par_name
            par_name = "moderator: " + par_name
            self.option_to_par_and_target[par_name] = (original_par_name, "moderator")
            option_list.append(par_name)
            if self.target == "moderator":
                if self.scan_par == original_par_name:
                    initial_value = par_name

        dropdown_scan_par = widgets.Dropdown(
            value=initial_value,
            options=option_list,
            description=''
        )

        dropdown_scan_par.observe(self.update_scan_par, "value")

        return dropdown_scan_par

    def update_scan_par(self, change):
        par_name, target = self.option_to_par_and_target[change.new]
        self.set_scanned_par(par_name, target)

        self.update_plot()

    def get_monitor_list(self):
        # Overwrite get_monitor_list to only allow 1D monitors
        shape = self.scan_overview.get_shape()
        indicies = tuple(self.list_indicies)
        guide = self.guides_with_at_least_one_run[0]
        moderator = self.get_moderator_list()[0]

        if self.scan_overview.data[guide][indicies][moderator] is not None:
            runs = self.scan_overview.data[guide][indicies][moderator].runs
        else:
            return []

        return runs[self.run_name].get_1D_monitor_list()

    def get_plot_data(self):

        par_index = self.get_par_index(self.scan_par, self.target)
        par_values = self.get_scan_from_index(par_index)

        base_indices = self.list_indicies
        moderator = self.moderator
        run_name = self.run_name
        monitor = self.monitor
        guide = self.selected_guide

        plot_data = OrderedDict()
        for scan_index, par_value in zip(range(len(par_values)), par_values):
            indices = copy.copy(base_indices)
            indices[par_index] = scan_index
            indices = tuple(indices)

            label = self.target + " " +  self.scan_par  + " = " + str(par_value) + " " + self.unit

            if self.scan_overview.data[guide][indices][moderator] is not None:
                if run_name in self.scan_overview.data[guide][indices][moderator].runs:
                    try:
                        plot_data[label] = self.scan_overview.data[guide][indices][moderator].runs[run_name].get_data(monitor)
                    except NameError:
                        pass

        return plot_data

    def new_plot(self):

        self.fig, self.ax = plt.subplots()

        self.update_plot()

    def update_plot(self):

        plot_data = self.get_plot_data()

        self.ax.cla()
        for label in reversed(plot_data):
            data = plot_data[label]

            xaxis = data.xaxis
            intensity = data.Intensity

            self.ax.plot(xaxis, intensity, label=label)
            self.ax.set_xlabel(data.metadata.xlabel)
            self.ax.set_ylabel(data.metadata.ylabel)

            self.ax.legend()

        self.ax.grid(True)

    def show_interface(self):
        output = widgets.Output()

        # default line color
        initial_color = '#FF00DD'

        with output:
            # fig, ax = plt.subplots(constrained_layout=True, figsize=(6, 4))
            self.new_plot()

        # move the toolbar to the bottom
        self.fig.canvas.toolbar_position = 'bottom'
        self.ax.grid(True)

        control_widgets = []
        # Place control widgets
        control_widgets += [widgets.Label(value="Data source")]

        self.dropdown_monitor = self.make_dropdown_monitor()
        control_widgets.append(self.dropdown_monitor)

        self.dropdown_run_name = self.make_dropdown_run_name()
        control_widgets.append(self.dropdown_run_name)

        self.dropdown_moderator = self.make_dropdown_moderator()
        control_widgets.append(self.dropdown_moderator)

        control_widgets += [widgets.Label(value="Scan parameter to plot")]

        self.dropdown_scan_par = self.make_dropdown_scan_par()
        control_widgets.append(self.dropdown_scan_par)

        if len(self.get_scanned_sample_parameters()) > 0:
            control_widgets += [widgets.Label(value="Scanned sample parameters")]
            self.sample_sliders = self.make_sample_scan_sliders()
            control_widgets += self.sample_sliders

        if len(self.get_scanned_moderator_parameters()) > 0:
            control_widgets += [widgets.Label(value="Scanned moderator parameters")]
            self.moderator_sliders = self.make_moderator_scan_sliders()
            control_widgets += self.moderator_sliders

        self.set_scanned_par(self.scan_par, self.target)  # locks slider corresponding to plotted parameter

        control_widgets += [widgets.Label(value="Guide selection")]

        control_widgets.append(self.make_guide_selector())

        controls = widgets.VBox(control_widgets)
        return widgets.HBox([controls, output])

