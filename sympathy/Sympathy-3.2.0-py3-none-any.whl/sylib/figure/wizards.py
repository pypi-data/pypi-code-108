# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import json
import itertools

from sympathy.api import qt2 as qt
from sympathy.api import node as synode
from sylib.icons import utils as icon_utils

QtGui = qt.QtGui
QtCore = qt.QtCore
QtWidgets = qt.QtWidgets


class Names:
    """
    Helper class to manage and provide names to the wizard methods.
    """

    def __init__(self, data):
        self._data = data

        fields = ['expr', 'path', 'name']
        names = list(data.names(kind='cols', fields=fields))
        self._expr = [f"arg{n.get('expr', '')}" for n in names]
        self._path = [n.get('path', []) for n in names]
        self._name = [n.get('name', '') for n in names]

        self._opts = self._uniquify([self._path_join(p) for p in self._path])
        self._opts_lookup = {v: i for i, v in enumerate(self._opts)}

    def _uniquify(self, opts):
        res = []
        out = set(opts)
        cnt = {}
        for k in opts:
            cnt[k] = opts.count(k)

        for k in opts:
            if cnt[k] == 1:
                res.append(k)
            else:
                for i in itertools.count():
                    candidate = f'{k}:{i}'
                    if candidate not in out:
                        res.append(candidate)
                        break
        return res

    def _path_join(self, path):
        return '/'.join(
            [str(seg[-1]) for seg in path if seg and seg[-1] != []])

    @property
    def options(self):
        return self._opts

    def to_name(self, option):
        try:
            return self._name[self._opts_lookup[option]]
        except KeyError:
            return ''

    def to_expr(self, option):
        try:
            return self._expr[self._opts_lookup[option]]
        except KeyError:
            return ''


class Wizard(QtCore.QObject):
    """
    Inherit this class to create another Figure wizard.

    Always override:
        * name
        * description
        * _init_parameters
        * _get_model
    Optionally override:
        * _adjust_parameters
    """
    wizard_changed = QtCore.Signal()

    name = None
    description = None
    help_text = None

    def __init__(self, model):
        super().__init__()
        self._model = model
        self._parameters = synode.parameters()
        self._init_parameters(self._parameters)

        self._data_names = Names(self._model.get_data_table())
        self._adjust_parameters(self._parameters, self._data_names)

        self._parameters.value_changed.add_handler(self._params_changed)

    def gui(self):
        """
        Return a gui for the wizard, with a title, help text and all
        parameters.
        """
        if not self._parameters.keys():
            return None

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel(f"<h1>{self.name}</h1>"))
        if self.help_text:
            icon = icon_utils.create_icon(icon_utils.SvgIcon.info)
            icon_label = QtWidgets.QLabel()
            icon_label.setPixmap(icon.pixmap(24))
            icon_label.setFixedSize(QtCore.QSize(32, 32))
            help_label = QtWidgets.QLabel(self.help_text)
            help_label.setWordWrap(True)
            help_widget = QtWidgets.QLabel()
            help_widget.setFrameStyle(QtWidgets.QFrame.Box)
            help_widget.setStyleSheet(
                "QLabel { background-color : #9ad2ea; }")
            help_layout = QtWidgets.QHBoxLayout()
            help_layout.addWidget(icon_label)
            help_layout.addWidget(help_label)
            help_widget.setLayout(help_layout)
            layout.addWidget(help_widget)
        layout.addWidget(self._parameters.gui())
        widget.setLayout(layout)
        return widget

    @classmethod
    def get_button(cls):
        button = QtWidgets.QPushButton()
        icon = icon_utils.create_icon(getattr(
            icon_utils.SvgIcon, cls.icon_name))
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(200, 100))
        button.setToolTip(cls.description)
        return button

    def get_model(self):
        return self._get_model(self._parameters, self._data_names)

    def _params_changed(self):
        self.wizard_changed.emit()

    def _init_parameters(self, parameters):
        """
        Override to create parameter structure in parameters argument using
        parameter helper.
        """
        raise NotImplementedError()

    def _adjust_parameters(self, parameters, names):
        """Override to adjust the parameters to the input data table."""
        pass

    def _get_model(self, parameters, names):
        """
        Override to specify how the figure model should be created from the
        parameters.
        """
        raise NotImplementedError()


class EmptyWizard(Wizard):
    name = 'empty'
    icon_name = 'custom_plot'
    description = "Create custom plot in advanced configuration view."

    def _init_parameters(self, parameters):
        pass

    def _get_model(self, parameters, names):
        return {
            "axes": [{
                "xaxis": {
                    "position": ("bottom", "value"),
                },
                "yaxis": {
                    "position": ("left", "value"),
                },
            }]}


class ScatterWizard(Wizard):
    name = 'Scatter'
    icon_name = 'scatter_wizard'
    description = (
        "Create scatter plot, optionally using extra "
        "signals for color and size.\n\n"
        "Suitable for showing how a small amount of data points are "
        "distributed along two contiguous axes"
    )

    def _init_parameters(self, parameters):
        parameters.set_string(
            'x_signal', label='X signal',
            description='A signal with the x coordinates of all points.',
            editor=synode.editors.combo_editor(filter=True))
        parameters.set_string(
            'y_signal', label='Y signal',
            description='A signal with the y coordinates of all points.',
            editor=synode.editors.combo_editor(filter=True))
        parameters.set_string(
            'colors', label='Color signal (optional)',
            description='A signal which should be used to determine '
                        'the color of each point.',
            editor=synode.editors.combo_editor(filter=True, include_empty=True))
        parameters.set_string(
            'sizes', label='Size signal (optional)',
            description='A signal which should be used to determine '
                        'the size of each point.',
            editor=synode.editors.combo_editor(filter=True, include_empty=True))
        parameters.set_integer(
            'size_scale', value=100, label='Size scale factor',
            description='A factor which is multiplied with all sizes in '
                        'the size signal.')

    def _adjust_parameters(self, parameters, names):
        parameters['x_signal'].adjust(names.options)
        parameters['y_signal'].adjust(names.options)
        parameters['colors'].adjust(names.options)
        parameters['sizes'].adjust(names.options)

    def _get_model(self, parameters, names):
        x_sig = parameters['x_signal'].value
        y_sig = parameters['y_signal'].value
        col_sig = parameters['colors'].value
        size_sig = parameters['sizes'].value
        scale = parameters['size_scale'].value
        plot = {
            "xdata": (names.to_expr(x_sig), "py"),
            "ydata": (names.to_expr(y_sig), "py"),
            "edgecolors": ("#000000", "value"),
            "linewidths": ("0.2", "value"),
            "type": "scatter"
        }
        if col_sig:
            plot["color"] = (names.to_expr(col_sig), "py")
            plot["colorbar"] = {
                "show": ("True", "value"),
                "label": (names.to_name(col_sig), "value"),
            }
        title_postfix = ""
        if size_sig:
            plot["s"] = (f"{scale}*{names.to_expr(size_sig)}", "py")
            title_postfix = f" (size = {names.to_name(size_sig)})"
        else:
            plot["s"] = (f"{scale}".format(scale), "value")

        x_sig_name = names.to_name(x_sig)
        y_sig_name = names.to_name(y_sig)
        return {
            "axes": [{
                "title": (
                    f"{x_sig_name} vs. {y_sig_name}{title_postfix}", "value"),
                "xaxis": {
                    "position": ("bottom", "value"),
                    "label": (x_sig_name, "value")
                },
                "yaxis": {
                    "position": ("left", "value"),
                    "label": (y_sig_name, "value")
                },
                "plots": [plot]
            }]}


class LineWizard(Wizard):
    name = 'Line plot'
    icon_name = 'line_wizard'
    description = (
        "Create line plot of one or more signals.\n\n"
        "Suitable for showing how signals vary as functions of another "
        "signal (often time)."
    )

    def _init_parameters(self, parameters):
        parameters.set_string(
            'title', label='Title',
            description='The title for the plot.')
        parameters.set_string(
            'y_label', label='Y Label',
            description='A label for the Y axis.')
        parameters.set_string(
            'x_signal', label='X Signal',
            description='Select the signal that defines the x axis '
                        '(e.g. time).',
            editor=synode.editors.combo_editor(filter=True))
        parameters.set_list(
            'y_signals', label='Y Signals',
            description='Check any signals which should be plotted. '
                        'Each checked signal gets its own color.',
            editor=synode.editors.multilist_editor(mode=False))
        parameters.set_boolean(
            'markers', value=False, label='Mark data points',
            description='Mark each data point with a circle.')

    def _adjust_parameters(self, parameters, names):
        parameters['x_signal'].adjust(names.options)
        parameters['y_signals'].adjust(names.options)

    def _get_model(self, parameters, names):
        title = parameters['title'].value
        x_sig = parameters['x_signal'].value
        y_sigs = parameters['y_signals'].value_names
        y_label = parameters['y_label'].value
        markers = parameters['markers'].value
        plots = [
            {
                "xdata": (names.to_expr(x_sig), "py"),
                "ydata": (names.to_expr(y_sig), "py"),
                "label": (names.to_name(y_sig), "value"),
                "type": "line"
            }
            for y_sig in y_sigs
        ]
        if markers:
            for plot in plots:
                plot['marker'] = ("circle", "value")
        return {
            "axes": [{
                "title": (title, "value"),
                "xaxis": {
                    "position": ("bottom", "value"),
                    "label": (names.to_name(x_sig), "value")
                },
                "yaxis": {
                    "position": ("left", "value"),
                    "label": (y_label, "value")
                },
                "plots": plots,
                "legend": {
                    "show": ("True", "value"),
                }
            }]}


class BarWizard(Wizard):
    name = 'Bar plot'
    icon_name = 'bar_wizard'
    description = (
        "Create grouped bar plot of one or more signals.\n\n"
        "Suitable for comparing categorical data from one or more signals."
    )

    def _init_parameters(self, parameters):
        parameters.set_string(
            'title', label='Title',
            description='The title for the plot.')
        parameters.set_string(
            'y_label', label='Y Label',
            description='A label for the Y axis.')
        parameters.set_string(
            'bin_labels', label='Bin labels',
            description='A signal with the labels of each bin. '
                        'These are printed along the x axis.',
            editor=synode.editors.combo_editor(filter=True))
        parameters.set_list(
            'y_signals', label='Y Signals',
            description='Check any signals which should be plotted. '
                        'Each checked signal gets its own color.',
            editor=synode.editors.multilist_editor(mode=False))
        parameters.set_boolean(
            'rotate', label='Rotate bin labels', value=False,
            description='Rotate bin labels to make room for longer labels.')

    def _adjust_parameters(self, parameters, names):
        parameters['bin_labels'].adjust(names.options)
        parameters['y_signals'].adjust(names.options)

    def _get_model(self, parameters, names):
        title = parameters['title'].value
        bin_labels = parameters['bin_labels'].value
        y_sigs = parameters['y_signals'].value_names
        y_label = parameters['y_label'].value
        rotate = parameters['rotate'].value
        plots = [
            {
                "bin_labels": (names.to_expr(bin_labels), "py"),
                "ydata": (names.to_expr(y_sig), "py"),
                "label": (names.to_name(y_sig), "value"),
                "type": "bar"
            }
            for y_sig in y_sigs
        ]
        xaxis = {"position": ("bottom", "value")}
        if rotate:
            xaxis["rot_tick_labels"] = ("Counter clockwise", "value")
        return {
            "axes": [{
                "title": (title, "value"),
                "xaxis": xaxis,
                "yaxis": {
                    "position": ("left", "value"),
                    "label": (y_label, "value")
                },
                "plots": [{
                    "grouping": ("grouped", "value"),
                    "plots": plots,
                    "type": "barcontainer"
                }],
                "legend": {
                    "show": ("True", "value")
                }
            }]}


class PieWizard(Wizard):
    name = 'Pie chart'
    icon_name = 'pie_wizard'
    description = "Create pie chart."

    def _init_parameters(self, parameters):
        parameters.set_string(
            'title', label='Title',
            description='The title for the plot.')
        parameters.set_string(
            'labels', label='Bin labels',
            description='A signal with the labels of the wedges.',
            editor=synode.editors.combo_editor(filter=True))
        parameters.set_string(
            'values', label='Values',
            description='A signal with the values of the wedges.',
            editor=synode.editors.combo_editor(filter=True))
        parameters.set_boolean(
            'percentages', label='Show percentages', value=False,
            description='If checked write the percentage in each wedge.')
        parameters.set_boolean(
            'legend', label='Put labels in legend', value=False,
            description='If checked puts all labels in a legend, '
                        'if unchecked write the labels next to their '
                        'respective pie piece.')

    def _adjust_parameters(self, parameters, names):
        parameters['labels'].adjust(names.options)
        parameters['values'].adjust(names.options)

    def _get_model(self, parameters, names):
        title = parameters['title'].value
        labels = parameters['labels'].value
        values = parameters['values'].value
        legend = parameters['legend'].value
        percentages = parameters['percentages'].value
        axes = {
            "title": (title, "value"),
            "aspect": ("equal", "value"),
            "frameon": ("False", "value"),
            "xaxis": {
                "position": ("bottom", "value"),
                "visible": ("False", "value")
            },
            "yaxis": {
                "position": ("left", "value"),
                "visible": ("False", "value")
            },
            "plots": [{
                "weights": (names.to_expr(values), "py"),
                "labels": (names.to_expr(labels), "py"),
                "type": "pie"
            }]}
        if percentages:
            axes['plots'][0]['autopct'] = ("Auto", "value")
        if legend:
            axes['plots'][0]['labelhide'] = ("True", "value")
            axes['legend'] = {
                "show": ("True", "value"),
                "loc": ("outside right", "value"),
                "distance": ("2.0", "value"),
            }
        return {"axes": [axes]}


class BoxWizard(Wizard):
    name = 'Box plot'
    icon_name = 'box_wizard'
    description = (
        "Create box plot of one or more signals.\n\n"
        "Suitable for comparing the distributions of different signals."
    )

    def _init_parameters(self, parameters):
        parameters.set_string(
            'title', label='Title',
            description='The title for the plot.')
        parameters.set_string(
            'y_label', label='Y Label',
            description='A label for the Y axis.')
        parameters.set_list(
            'signals', label='Signals',
            description='Check all signals that should be in the plot. Each '
                        'signal gets a box plot showing its distribution.',
            editor=synode.editors.multilist_editor(mode=False))
        parameters.set_boolean(
            'rotate', label='Rotate labels', value=False,
            description='Rotate signal labels to make room for longer labels.')

    def _adjust_parameters(self, parameters, names):
        parameters['signals'].adjust(names.options)

    def _get_model(self, parameters, names):
        title = parameters['title'].value
        signals = parameters['signals'].value_names
        y_label = parameters['y_label'].value
        rotate = parameters['rotate'].value
        ydata = ", ".join(names.to_expr(sig) for sig in signals)
        bin_labels = ", ".join(f"'{names.to_name(sig)}'" for sig in signals)
        xaxis = {"position": ("bottom", "value")}
        if rotate:
            xaxis["rot_tick_labels"] = ("Counter clockwise", "value")
        return {
            "axes": [{
                "title": (title, "value"),
                "xaxis": xaxis,
                "yaxis": {
                    "position": ("left", "value"),
                    "label": (y_label, "value")
                },
                "plots": [{
                    "ydata": (f"[{ydata}]", "py"),
                    "bin_labels": (f"[{bin_labels}]", "py"),
                    "type": "box"
                }]
            }]}


class HistogramWizard(Wizard):
    name = 'Histogram plot'
    icon_name = 'hist_wizard'
    description = (
        "Creates a histogram plot from prebinned data.\n\n"
        "Suitable for showing how data is distributed along "
        "one contiguous axis."
    )
    help_text = (
        "In order to create a histogram, you should first bin your "
        "signal using the node 'Histogram Calculation'."
    )

    def _init_parameters(self, parameters):
        parameters.set_string(
            'title', label='Title',
            description='The title for the plot.')
        parameters.set_string(
            'x_label', label='X Label',
            description='A label for the X axis.')
        parameters.set_string(
            'y_label', label='Y Label',
            description='A label for the Y axis.')
        parameters.set_string(
            'bin_min_edges', label='Bin min edges',
            description='A signal with the min edges for all bins.',
            editor=synode.editors.combo_editor(filter=True))
        parameters.set_string(
            'bin_max_edges', label='Bin max edges',
            description='A signal with the max edges for all bins.',
            editor=synode.editors.combo_editor(filter=True))
        parameters.set_string(
            'bin_values', label='Bin values',
            description='A signal with the values for all bins.',
            editor=synode.editors.combo_editor(filter=True))

    def _adjust_parameters(self, parameters, names):
        # Automatically set all parameters to the default column names from
        # Histogram Calculation.
        parameters['bin_min_edges'].adjust(names.options)
        if 'Bin min edges' in names.options:
            parameters['bin_min_edges'].value = 'Bin min edges'
        parameters['bin_max_edges'].adjust(names.options)
        if 'Bin max edges' in names.options:
            parameters['bin_max_edges'].value = 'Bin max edges'
        parameters['bin_values'].adjust(names.options)
        if 'Bin values' in names.options:
            parameters['bin_values'].value = 'Bin values'

    def _get_model(self, parameters, names):
        title = parameters['title'].value
        x_label = parameters['x_label'].value
        y_label = parameters['y_label'].value
        bin_min_edges = names.to_expr(parameters['bin_min_edges'].value)
        bin_max_edges = names.to_expr(parameters['bin_max_edges'].value)
        bin_values = names.to_expr(parameters['bin_values'].value)
        return {
            "axes": [{
                "title": (title, "value"),
                "xaxis": {
                    "position": ("bottom", "value"),
                    "label": (x_label, "value")
                },
                "yaxis": {
                    "position": ("left", "value"),
                    "label": (y_label, "value")
                },
                "plots": [{
                    "bin_min_edges": (bin_min_edges, "py"),
                    "bin_max_edges": (bin_max_edges, "py"),
                    "ydata": (bin_values, "py"),
                    "type": "hist"
                }]
            }]}


class HeatmapWizard(Wizard):
    name = 'Heatmap plot'
    icon_name = 'heatmap_wizard'
    description = (
        "Creates heatmap plot from prebinned data.\n\n"
        "Suitable for showing how data is "
        "distributed along two contiguous axes."
    )
    help_text = (
        "In order to create a heatmap, you should first bin your signal "
        "using the node 'Heatmap Calculation'."
    )

    def _init_parameters(self, parameters):
        parameters.set_string(
            'title', label='Title',
            description='The title for the plot.')
        parameters.set_string(
            'x_label', label='X Label',
            description='A label for the X axis.')
        parameters.set_string(
            'y_label', label='Y Label',
            description='A label for the Y axis.')
        parameters.set_string(
            'z_label', label='Z Label',
            description='A label for the color scale.')
        parameters.set_string(
            'x_bin_edges', label='X bin edges',
            description='A signal with the X edges for all bins.',
            editor=synode.editors.combo_editor(filter=True))
        parameters.set_string(
            'y_bin_edges', label='Bin max edges',
            description='A signal with the Y edges for all bins.',
            editor=synode.editors.combo_editor(filter=True))
        parameters.set_string(
            'bin_values', label='Bin values',
            description='A signal with the values for all bins.',
            editor=synode.editors.combo_editor(filter=True))

    def _adjust_parameters(self, parameters, names):
        # Automatically set all parameters to the default column names from
        # Heatmap Calculation.
        parameters['x_bin_edges'].adjust(names.options)
        if 'X bin edges' in names.options:
            parameters['x_bin_edges'].value = 'X bin edges'
        parameters['y_bin_edges'].adjust(names.options)
        if 'Y bin edges' in names.options:
            parameters['y_bin_edges'].value = 'Y bin edges'
        parameters['bin_values'].adjust(names.options)
        if 'Bin values' in names.options:
            parameters['bin_values'].value = 'Bin values'

    def _get_model(self, parameters, names):
        title = parameters['title'].value
        x_label = parameters['x_label'].value
        y_label = parameters['y_label'].value
        z_label = parameters['z_label'].value
        x_bin_edges = names.to_expr(parameters['x_bin_edges'].value)
        y_bin_edges = names.to_expr(parameters['y_bin_edges'].value)
        bin_values = names.to_expr(parameters['bin_values'].value)
        return {
            "axes": [{
                "title": (title, "value"),
                "xaxis": {
                    "position": ("bottom", "value"),
                    "label": (x_label, "value"),
                },
                "yaxis": {
                    "position": ("left", "value"),
                    "label": (y_label, "value"),
                },
                "plots": [{
                    "xdata": (x_bin_edges, "py"),
                    "ydata": (y_bin_edges, "py"),
                    "zdata": (bin_values, "py"),
                    "colorbar": {
                        "show": ("True", "value"),
                        "label": (z_label, "value"),
                    },
                    "type": "heatmap",
                }]
            }]}


class TimelineWizard(Wizard):
    name = 'Timeline plot'
    icon_name = 'timeline_wizard'
    description = (
        "Create timeline plot.\n\n"
        "Suitable for showing how one or more "
        "signals switch between discrete values."
    )

    def _init_parameters(self, parameters):
        parameters.set_string(
            'title', label='Title',
            description='The title for the plot.')
        parameters.set_string(
            'x_signal', label='X Signal',
            description='A signal with the X values for all state changes.',
            editor=synode.editors.combo_editor(filter=True))
        parameters.set_list(
            'y_signals', label='Values signals',
            description='Signals with discrete values.',
            editor=synode.editors.multilist_editor(mode=False))

    def _adjust_parameters(self, parameters, names):
        parameters['x_signal'].adjust(names.options)
        parameters['y_signals'].adjust(names.options)

    def _get_model(self, parameters, names):
        title = parameters['title'].value
        x_sig = parameters['x_signal'].value
        y_sigs = parameters['y_signals'].value_names
        plots = [
            {
                "xdata": (names.to_expr(x_sig), "py"),
                "values": (names.to_expr(y_sig), "py"),
                "label": (names.to_name(y_sig), "value"),
                "y_start": (str(i), "value"),
                "type": "timeline"
            }
            for i, y_sig in enumerate(y_sigs)
        ]
        return {
            "axes": [{
                "title": (title, "value"),
                "xaxis": {
                    "position": ("bottom", "value"),
                    "label": (names.to_name(x_sig), "value"),
                },
                "yaxis": {
                    "position": ("left", "value"),
                    "visible": ("False", "value"),
                },
                "plots": plots
            }]}


class ImageWizard(Wizard):
    name = 'Image plot'
    icon_name = 'image_wizard'
    description = "Create image plot from an image port."
    help_text = (
        "Image plots are for plotting an image from the image processing "
        "nodes, so for this plot the input port should be of type image."
    )

    def _init_parameters(self, parameters):
        parameters.set_string(
            'title', label='Title',
            description='The title for the plot.')
        parameters.set_boolean(
            'show_ticks', label='Show ticks', value=True,
            description='Show ticks on X and Y axes.')

    def _get_model(self, parameters, names):
        title = parameters['title'].value
        show_ticks = parameters['show_ticks'].value
        xaxis = {"position": ("bottom", "value")}
        yaxis = {
            "position": ("left", "value"),
            "inverted": ("True", "value")
        }
        if not show_ticks:
            xaxis['visible'] = ("False", "value")
            yaxis['visible'] = ("False", "value")
        return {
            "axes": [{
                "title": (title, "value"),
                "aspect": ("equal", "value"),
                "xaxis": xaxis,
                "yaxis": yaxis,
                "plots": [{
                    "image": ("arg.im", "py"),
                    "type": "image",
                }]
            }]}


sections = {
    'Basic plots': [
        EmptyWizard,
        LineWizard,
        ScatterWizard,
    ],
    'Distribution plots': [
        HistogramWizard,
        HeatmapWizard,
        BoxWizard,
    ],
    'Discrete data': [
        BarWizard,
        PieWizard,
        TimelineWizard,
    ],
    'Other plots': [
        ImageWizard,
    ],
}


# Flatten sections dictionary, discarding section names
wizard_classes = {
    wizard.name: wizard
    for wizard_classes in sections.values()
    for wizard in wizard_classes
}
