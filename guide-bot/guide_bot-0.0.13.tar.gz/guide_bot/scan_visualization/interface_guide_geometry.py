import matplotlib.pyplot as plt

import ipywidgets as widgets
from IPython.display import display

from mcstasscript.interface import instr, functions, plotter

from guide_bot.logging.log_plotter import LogPlotter
from guide_bot.scan_visualization.jb_interface import HiddenPrints
from guide_bot.scan_visualization.jb_interface import BaseInterface

class PlotGuideGeometry(BaseInterface):
    def __init__(self, scan_overview):
        super().__init__(scan_overview)

        self.fig = None
        self.ax_h = None
        self.ax_v = None

        self.fom_fig = None
        self.fom_ax = None

        self.dropdown_monitor = None
        self.dropdown_run_name = None
        self.dropdown_moderator = None
        self.fom_slider = None

        self.fom_index = 1
        self.fom_max_index = 1

        self.last_log_plotter = None
        self.last_guide = None
        self.last_indices = None

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

    def make_fom_slider(self, nmax):

        self.fom_slider = widgets.IntSlider(value=nmax, min=0, max=nmax, step=1,
                                            description="Worst", readout=True,
                                            continouos_update=True,
                                            layout=widgets.Layout(width="80%"))

        self.fom_slider.observe(self.update_fom_slider, "value")
        widget_label = widgets.Label("Best")

        return widgets.HBox([self.fom_slider, widget_label])

    def update_fom_slider(self, change):
        self.fom_index = change.new
        self.update_plot()

    def get_plot_data(self):

        guide = self.selected_guide
        indices = tuple(self.list_indicies)
        #moderator = self.moderator
        #run_name = self.run_name
        #monitor = self.monitor

        if self.last_guide == guide and self.last_indices == indices:
            return self.last_log_plotter

        log_plotter = None
        if self.scan_overview.log[guide][indices]["log"] is not None:
            log_plotter = LogPlotter(self.scan_overview.log[guide][indices]["log"])
            self.last_guide = guide
            self.last_indices = indices
            self.last_log_plotter = log_plotter

        n_foms = len(log_plotter.data_fom_sorted[:, 0])
        self.fom_index = n_foms - 1
        if self.fom_slider is not None:
            self.fom_slider.min = 0
            self.fom_slider.max = n_foms - 1
            self.fom_slider.value = n_foms - 1

        return log_plotter

    def new_plot(self):

        self.fig, (self.ax_h, self.ax_v) = plt.subplots(nrows=2, figsize=(6,6))
        self.update_plot()

    def update_plot(self):

        log_plotter = self.get_plot_data()

        self.ax_h.cla()
        self.ax_v.cla()

        if log_plotter is None:
            self.ax_h.text(0.4, 0.5, "No data available")
            self.ax_v.text(0.4, 0.5, "No data available")
            return

        data_line = log_plotter.data_fom_sorted[self.fom_index, :]
        log_plotter.plot_guide_center_line_ax(self.ax_h, horizontal=True, data_line=data_line)
        log_plotter.plot_guide_center_line_ax(self.ax_v, horizontal=False, data_line=data_line)

        plt.tight_layout()

        self.update_fom_plot()

    def new_fom_plot(self):

        self.fom_fig, self.fom_ax = plt.subplots(figsize=(3, 2))
        self.update_fom_plot()

    def update_fom_plot(self):

        log_plotter = self.get_plot_data()

        self.fom_ax.cla()

        if log_plotter is None:
            self.fom_ax.text(0.4, 0.5, "No data available")
            return

        log_plotter.plot_1D_fom_ax(self.fom_ax, highlight_sorted_index=self.fom_index)
        self.fom_ax.set_ylabel("")
        self.fom_ax.set_yticklabels([])
        self.fom_ax.set_title("Fom history")


    def show_interface(self):
        # default line color
        initial_color = '#FF00DD'

        control_widgets = []
        # Place control widgets
        control_widgets += [widgets.Label(value="Data source")]

        self.dropdown_monitor = self.make_dropdown_monitor()

        self.dropdown_run_name = self.make_dropdown_run_name()

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

        log_plotter = self.get_plot_data()
        n_foms = len(log_plotter.data_fom_sorted[:, 0])

        control_widgets += [widgets.Label(value="Fom slider")]
        control_widgets.append(self.make_fom_slider(n_foms - 1))

        output_fom = widgets.Output()
        with output_fom:
            self.new_fom_plot()

        output = widgets.Output()
        with output:
            # fig, ax = plt.subplots(constrained_layout=True, figsize=(6, 4))
            self.new_plot()

        # Handle toolbar
        self.fig.canvas.toolbar_position = 'bottom'
        self.fom_fig.canvas.toolbar_position = 'bottom'
        self.fom_fig.canvas.toolbar_visible = False

        control_widgets.append(output_fom)

        controls = widgets.VBox(control_widgets)
        return widgets.HBox([controls, output])