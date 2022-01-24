import os
import sys

import ipywidgets as widgets


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


class BaseInterface:
    def __init__(self, scan_overview):
        self.scan_overview = scan_overview

        self.guide_names = self.scan_overview.get_guide_names()
        self.guide_enable = {}
        for guide in self.guide_names:
            self.guide_enable[guide] = True

        n_pars = self.scan_overview.get_n_scanned_parameters()
        #self.list_indicies = [0] * n_pars

        if len(self.scan_overview.succesful_indices) == 0:
            raise RuntimeError("No succesful runs found. Run load_all_guide_information in overview object.")
        else:
            self.guides_with_at_least_one_run = list(self.scan_overview.succesful_indices.keys())
            succesful_guide = self.guides_with_at_least_one_run[0]
            self.list_indicies = list(self.scan_overview.succesful_indices[succesful_guide][0])

        self.moderator = self.get_moderator_list()[0]
        self.run_name = self.get_run_name_list()[0]
        self.monitor = self.get_monitor_list()[0]

        self.last_legal_run_names = None

        self.moderator_scan_labels = None
        self.moderator_scan_sliders = None

        self.sample_scan_sliders = {}
        self.sample_scan_labels = {}

    def get_guide_names(self):
        return self.guide_names

    def enable_guide(self, guide):
        self.guide_enable[guide] = True

    def disable_guide(self, guide):
        self.guide_enable[guide] = False

    def enabled_guides(self):
        enabled_guides = []
        for guide in self.guide_enable:
            if self.guide_enable[guide]:
                enabled_guides.append(guide)
        return enabled_guides

    def get_monitor_list(self):
        shape = self.scan_overview.get_shape()
        indicies = tuple(self.list_indicies)
        guide = self.guides_with_at_least_one_run[0]
        moderator = self.get_moderator_list()[0]

        if self.scan_overview.data[guide][indicies][moderator] is not None:
            runs = self.scan_overview.data[guide][indicies][moderator].runs
            return runs[self.run_name].get_monitor_list()
        else:
            return []

    def set_monitor(self, monitor):
        if monitor not in self.get_monitor_list():
            raise KeyError("Monitor named " + monitor + " not available.")

        self.monitor = monitor

    def get_run_name_list(self):
        shape = self.scan_overview.get_shape()
        indicies = tuple(self.list_indicies)
        guide = self.guides_with_at_least_one_run[0]
        moderator = self.get_moderator_list()[0]

        if self.scan_overview.data[guide][indicies][moderator] is not None:
            runs = self.scan_overview.data[guide][indicies][moderator].runs
            return_value = list(runs.keys())
            self.last_legal_run_names = return_value

            return return_value
        else:
            if self.last_legal_run_names is not None:
                return self.last_legal_run_names
            else:
                return []

    def set_run_name(self, run_name):
        if run_name is None:
            return

        if run_name not in self.get_run_name_list():
            raise KeyError("Run named " + str(run_name) + " not available.")

        self.run_name = run_name

    def get_moderator_list(self):
        return self.scan_overview.get_moderators()

    def set_moderator(self, moderator):
        if moderator not in self.get_moderator_list():
            raise KeyError("Moderator named " + str(moderator) + " not available.")

        self.moderator = moderator

    def get_scanned_parameters(self):
        return self.scan_overview.get_scanned_parameters()

    def get_scanned_sample_parameters(self):
        return self.scan_overview.get_scanned_sample_parameters()

    def get_scanned_sample_parameter_values(self, parameter):
        return self.scan_overview.get_scanned_sample_parameter_values(parameter)

    def get_scanned_sample_parameter_unit(self, parameter):
        return self.scan_overview.get_scanned_sample_unit(parameter)

    def get_scanned_moderator_parameters(self):
        return self.scan_overview.get_scanned_moderator_parameters()

    def get_scanned_moderator_parameter_values(self, parameter):
        return self.scan_overview.get_scanned_moderator_parameter_values(parameter)

    def get_scanned_moderator_parameter_unit(self, parameter):
        return self.scan_overview.get_scanned_moderator_unit(parameter)

    def get_par_index(self, parameter, type):
        if parameter not in self.get_scanned_parameters():
            raise KeyError("Parameter named" + str(parameter) + "not available.")

        if type == "sample":
            par_index = self.scan_overview.get_par_index_sample(parameter)
        elif type == "moderator":
            par_index = self.scan_overview.get_par_index_moderator(parameter)
        else:
            raise KeyError("type should be sample or moderator")

        return par_index

    def get_scan_from_index(self, index):
        return self.scan_overview.get_scan_values(index)

    def get_par_max_index(self, parameter, type):
        par_index = self.get_par_index(parameter, type)

        scan_shape = self.scan_overview.get_shape()
        return scan_shape[par_index] - 1

    def set_index(self, parameter, type, index):
        par_index = self.get_par_index(parameter, type)
        if index < 0 or index > self.get_par_max_index(parameter, type):
            raise IndexError("Given index outside of range of parameter")

        self.list_indicies[par_index] = index

    def make_dropdown_monitor(self):
        dropdown_monitor = widgets.Dropdown(
            value=self.monitor,
            options=self.get_monitor_list(),
            description='monitor'
        )

        dropdown_monitor.observe(self.update_monitor, "value")

        return dropdown_monitor

    def update_monitor(self, change):
        self.set_monitor(change.new)
        self.update_plot()

    def make_dropdown_run_name(self):
        dropdown_run_name = widgets.Dropdown(
            value=self.run_name,
            options=self.get_run_name_list(),
            description='run_name'
        )

        dropdown_run_name.observe(self.update_run_name, "value")

        return dropdown_run_name

    def update_run_name(self, change):
        self.set_run_name(change.new)
        self.update_plot()

    def make_dropdown_moderator(self):
        dropdown_moderator = widgets.Dropdown(
            value=self.moderator,
            options=self.get_moderator_list(),
            description='moderator'
        )

        dropdown_moderator.observe(self.update_moderator, "value")

        return dropdown_moderator

    def update_moderator(self, change):
        self.set_moderator(change.new)
        self.update_plot()

    def make_guide_checkboxes(self):
        guide_checkboxes = []
        for guide in self.get_guide_names():
            widget = widgets.Checkbox(value=True, description=guide, disabled=False, indent=True)
            guide_checkboxes.append(widget)

        for checkbox in guide_checkboxes:
            checkbox.observe(self.update_guide_selection, "value")

        return guide_checkboxes

    def update_guide_selection(self, change):
        if change.new:
            self.enable_guide(change["owner"].description)
        else:
            self.disable_guide(change["owner"].description)
        self.update_plot()

    def make_sample_scan_sliders(self):
        sample_sliders = []
        sample_labels = []
        full_sample_sliders = []
        self.sample_scan_sliders = {}
        self.sample_scan_labels = {}
        for sample_par in self.get_scanned_sample_parameters():
            max_index = self.get_par_max_index(sample_par, "sample")
            global_index = self.scan_overview.get_global_index_from_sample_parameter(sample_par)
            current_index = self.list_indicies[global_index]

            widget = widgets.IntSlider(value=current_index, min=0, max=max_index, step=1,
                                       description=sample_par, readout=False,
                                       layout=widgets.Layout(width="80%"))
            self.sample_scan_sliders[sample_par] = widget
            sample_sliders.append(widget)


            initial_value = self.get_scanned_sample_parameter_values(sample_par)[current_index]
            unit = self.get_scanned_sample_parameter_unit(sample_par)
            if unit is not None:
                value_string = str(initial_value) + " [" + str(unit) + "]"
            else:
                value_string = str(initial_value)

            widget_label = widgets.Label(value=value_string)
            sample_labels.append(widget_label)
            self.sample_scan_labels[sample_par] = widget_label

            full_sample_sliders.append(widgets.HBox([widget, widget_label]))

        for slider, label in zip(sample_sliders, sample_labels):
            slider.observe(self.update_scan_sample, "value")

        return full_sample_sliders

    def update_scan_sample(self, change):

        par_name = change.owner.description
        # Set the new index
        self.set_index(par_name, "sample", change.new)
        # Find new value of scan to show on label
        new_value = self.get_scanned_sample_parameter_values(par_name)[change.new]
        unit = self.get_scanned_sample_parameter_unit(par_name)
        if unit is not None:
            value_string = str(new_value) + " [" + str(unit) + "]"
        else:
            value_string = str(new_value)

        # Assign new value to the label
        self.sample_scan_labels[par_name].value = value_string
        # Update run names as this scanned variable may impact what runs are available
        current_run_name = self.dropdown_run_name.value
        new_options = tuple(self.get_run_name_list())

        self.dropdown_run_name.options = new_options
        if current_run_name in new_options:
            self.set_run_name(current_run_name)
            self.dropdown_run_name.value = current_run_name
        elif len(new_options) > 0:
            self.set_run_name(new_options[0])
            self.dropdown_run_name.value = new_options[0]

        self.update_plot()

    def make_moderator_scan_sliders(self):
        moderator_sliders = []
        moderator_labels = []
        full_moderator_sliders = []
        self.moderator_scan_sliders = {}
        self.moderator_scan_labels = {}
        for moderator_par in self.get_scanned_moderator_parameters():
            max_index = self.get_par_max_index(moderator_par, "moderator")
            global_index = self.scan_overview.get_global_index_from_moderator_parameter(moderator_par)
            current_index = self.list_indicies[global_index]
            widget = widgets.IntSlider(value=current_index, min=0, max=max_index, step=1,
                                       description=moderator_par, readout=False,
                                       layout=widgets.Layout(width="80%"))
            moderator_sliders.append(widget)
            self.moderator_scan_sliders[moderator_par] = widget

            initial_value = self.get_scanned_moderator_parameter_values(moderator_par)[current_index]
            unit = self.get_scanned_moderator_parameter_unit(moderator_par)
            if unit is not None:
                value_string = str(initial_value) + " [" + str(unit) + "]"
            else:
                value_string = str(initial_value)
            widget_label = widgets.Label(value=value_string)
            moderator_labels.append(widget_label)
            self.moderator_scan_labels[moderator_par] = widget_label

            full_moderator_sliders.append(widgets.HBox([widget, widget_label]))

        for slider, label in zip(moderator_sliders, moderator_labels):
            slider.observe(self.update_scan_moderator, "value")

        return full_moderator_sliders

    def update_scan_moderator(self, change):

        par_name = change.owner.description
        # Set the new index
        self.set_index(par_name, "moderator", change.new)
        # Find new value of scan to show on label
        new_value = self.get_scanned_moderator_parameter_values(par_name)[change.new]
        unit = self.get_scanned_moderator_parameter_unit(par_name)
        if unit is not None:
            value_string = str(new_value) + " [" + str(unit) + "]"
        else:
            value_string = str(new_value)

        # Assign new value to the label
        self.moderator_scan_labels[par_name].value = value_string
        # Update run names as this scanned variable may impact what runs are available
        self.dropdown_run_name.options = tuple(self.get_run_name_list())
        self.update_plot()









