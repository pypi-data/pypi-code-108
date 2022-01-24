import copy

import matplotlib.pyplot as plt

import ipywidgets as widgets
from IPython.display import display

from guide_bot.scan_visualization.jb_interface import HiddenPrints
from guide_bot.scan_visualization.jb_interface import BaseInterface

class PlotSum(BaseInterface):
    def __init__(self, scan_overview):
        super().__init__(scan_overview)

        self.fig = None
        self.ax = None

        self.dropdown_monitor = None
        self.dropdown_run_name = None
        self.dropdown_moderator = None

        self.sample_scan_labels = None
        self.moderator_scan_labels = None

        self.option_to_par_and_target = None
        self.dropdown_scan_par = None

        self.sample_sliders = None
        self.moderator_sliders = None

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

    def get_plot_data(self):

        par_index = self.get_par_index(self.scan_par, self.target)
        par_values = self.get_scan_from_index(par_index)

        base_indices = self.list_indicies
        moderator = self.moderator
        run_name = self.run_name
        monitor = self.monitor

        plot_data = {}
        for guide in self.enabled_guides():

            data = []
            scan_values = []
            for scan_index, par_value in zip(range(len(par_values)), par_values):
                indices = copy.copy(base_indices)
                indices[par_index] = scan_index
                indices = tuple(indices)

                if self.scan_overview.data[guide][indices][moderator] is not None:
                    #intensity = self.scan_overview.data[guide][indices][moderator].runs[run_name].get_sum_data(monitor)
                    if run_name in self.scan_overview.data[guide][indices][moderator].runs:
                        intensity = self.scan_overview.data[guide][indices][moderator].runs[run_name].get_average_data(monitor)
                else:
                    intensity = None

                if intensity is not None:
                    scan_values.append(par_value)
                    data.append(intensity)


            plot_data[guide] = (scan_values, data)

        return plot_data

    def new_plot(self):

        self.fig, self.ax = plt.subplots()

        self.update_plot()

    def update_plot(self):
        plot_data = self.get_plot_data()

        self.ax.cla()
        for label in plot_data:
            scan_values, data = plot_data[label]

            self.ax.plot(scan_values, data, "-o", label=label)
            xlabel = self.scan_par
            if self.unit is not None:
                xlabel += " [" + str(self.unit) + "]"
            self.ax.set_xlabel(xlabel)
            self.ax.set_ylabel("average intensity")

            self.ax.legend()

        self.ax.grid(True)
        plt.tight_layout()

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

        self.set_scanned_par(self.scan_par, self.target) # locks slider corresponding to plotted parameter

        control_widgets += [widgets.Label(value="Guide selection")]

        guide_checkboxes = self.make_guide_checkboxes()
        control_widgets += guide_checkboxes

        controls = widgets.VBox(control_widgets)
        return widgets.HBox([controls, output])