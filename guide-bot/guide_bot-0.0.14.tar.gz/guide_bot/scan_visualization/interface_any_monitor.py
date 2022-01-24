import matplotlib.pyplot as plt

import ipywidgets as widgets
from IPython.display import display

from mcstasscript.interface import instr, functions, plotter

from guide_bot.scan_visualization.jb_interface import HiddenPrints
from guide_bot.scan_visualization.jb_interface import BaseInterface

class PlotAnyMonitor(BaseInterface):
    def __init__(self, scan_overview):
        super().__init__(scan_overview)

        self.fig = None
        self.ax = None
        self.colorbar_ax = None

        self.dropdown_monitor = None
        self.dropdown_run_name = None
        self.dropdown_moderator = None

        self.sample_scan_labels = None
        self.moderator_scan_labels = None

        self.selected_guide = self.guides_with_at_least_one_run[0]


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

    def get_plot_data(self):

        guide = self.selected_guide
        indices = tuple(self.list_indicies)
        moderator = self.moderator
        run_name = self.run_name
        monitor = self.monitor

        output = None
        if self.scan_overview.data[guide][indices][moderator] is not None:
            if run_name in self.scan_overview.data[guide][indices][moderator].runs:
                output = self.scan_overview.data[guide][indices][moderator].runs[run_name].get_data(monitor)

        return output

    def new_plot(self):

        self.fig, (self.ax, self.colorbar_ax) = plt.subplots(ncols=2, gridspec_kw={'width_ratios': [4, 1]})

        self.update_plot()

    def update_plot(self):

        plot_data = self.get_plot_data()

        self.ax.cla()
        # self.ax.xaxis.set_ticks([])
        # self.ax.yaxis.set_ticks([])
        self.colorbar_ax.cla()
        self.colorbar_ax.xaxis.set_ticks([])
        self.colorbar_ax.yaxis.set_ticks([])
        self.colorbar_ax.axis("off")

        if plot_data is None:
            self.ax.text(0.4,0.5, "No data available")
            return

        #print(self.ax.get_position())
        #print(self.original_ax_position)
        #self.ax.set_position(list(self.original_ax_position))

        plot_data.set_plot_options(show_colorbar=True)
        with HiddenPrints():
            plotter._plot_fig_ax(plot_data, self.fig, self.ax, colorbar_axes=self.colorbar_ax)

        if self.colorbar_ax.has_data():
            self.colorbar_ax.axis("on")
            self.ax.grid(False)
        else:
            self.ax.grid(True)

        self.colorbar_ax.set_aspect(20)

        plt.tight_layout()

    def show_interface(self):
        output = widgets.Output()

        # default line color
        initial_color = '#FF00DD'

        with output:
            # fig, ax = plt.subplots(constrained_layout=True, figsize=(6, 4))
            self.new_plot()

        # move the toolbar to the bottom
        self.fig.canvas.toolbar_position = 'bottom'
        #self.ax.grid(True)

        control_widgets = []
        # Place control widgets
        control_widgets += [widgets.Label(value="Data source")]

        self.dropdown_monitor = self.make_dropdown_monitor()
        control_widgets.append(self.dropdown_monitor)

        self.dropdown_run_name = self.make_dropdown_run_name()
        control_widgets.append(self.dropdown_run_name)

        self.dropdown_moderator = self.make_dropdown_moderator()
        control_widgets.append(self.dropdown_moderator)

        if len(self.get_scanned_sample_parameters()) > 0:
            control_widgets += [widgets.Label(value="Scanned sample parameters")]
            control_widgets += self.make_sample_scan_sliders()

        if len(self.get_scanned_moderator_parameters()) > 0:
            control_widgets += [widgets.Label(value="Scanned moderator parameters")]
            control_widgets += self.make_moderator_scan_sliders()

        control_widgets += [widgets.Label(value="Guide selection")]

        control_widgets.append(self.make_guide_selector())

        controls = widgets.VBox(control_widgets)
        return widgets.HBox([controls, output])