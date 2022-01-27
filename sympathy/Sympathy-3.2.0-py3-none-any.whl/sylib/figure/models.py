# This file is part of Sympathy for Data.
# Copyright (c) 2016-2017, Combine Control Systems AB
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
import copy
import types
from collections import OrderedDict, defaultdict

from sylib.icons.utils import SvgIcon, color_icon, create_icon
from sylib.tree_model.models import NodeTags, BaseNode, Property
from sylib.tree_model import widgets as tree_widgets
from sylib.figure import colors, mpl_utils, common
from sylib.figure import widgets as fig_widgets


SY_XDATA_PARAMS = {'label': 'X Data',
                   'type': str,
                   'icon': SvgIcon.x_data,
                   'default': '',
                   'options': None,
                   'description': (
                       'Specify the column used as x-data as a python '
                       'expression which evaluates to a numpy ndarray'),
                   'editor': None}

SY_XERR_PARAMS = {'label': 'X Error',
                  'type': str,
                  'icon': SvgIcon.y_data,
                  'default': '',
                  'options': None,
                  'description': (
                       'Specify the column used as x errors as a python '
                       'expression which evaluates to a numpy ndarray'),
                  'editor': None}

SY_YDATA_PARAMS = {'label': 'Y Data',
                   'type': str,
                   'icon': SvgIcon.y_data,
                   'default': '',
                   'options': None,
                   'description': (
                       'Specify the column used as y data a python '
                       'expression which evaluates to a numpy ndarray'),
                   'editor': None}

SY_YERR_PARAMS = {'label': 'Y Error',
                  'type': str,
                  'icon': SvgIcon.y_data,
                  'default': '',
                  'options': None,
                  'description': (
                       'Specify the column used as y errors as a python '
                       'expression which evaluates to a numpy ndarray'),
                  'editor': None}

SY_ZDATA_PARAMS = {'label': 'Z Data',
                   'type': str,
                   'icon': SvgIcon.z_data,
                   'default': '',
                   'options': None,
                   'description': (
                       'Specify the column used as y data a python '
                       'expression which evaluates to a numpy ndarray'),
                   'editor': None}

SY_MINOR_TICK_PARAMS = {'label': 'Minor ticks',
                        'type': str,
                        'icon': SvgIcon.grid,
                        'default': '',
                        'options': None,
                        'description': (
                            'Specify the column used as minor ticks, '
                            'as a python expression which evaluates to a '
                            'numpy ndarray'),
                        'editor': None}

SY_MAJOR_TICK_PARAMS = {'label': 'Major ticks',
                        'type': str,
                        'icon': SvgIcon.grid,
                        'default': '',
                        'options': None,
                        'description': (
                            'Specify the column used as major ticks, '
                            'as a python expression which evaluates to a '
                            'numpy ndarray'),
                        'editor': None}

SY_LABEL_PARAMS = {'label': 'Label',
                   'type': str,
                   'icon': SvgIcon.label,
                   'default': '',
                   'options': None,
                   'description': 'Specify the text used as label.',
                   'editor': tree_widgets.SyLabelEdit}

COLOR_DESCRIPTION = ('Specify a color either as RGB or RGBA'
                     '(e.g. "[1., 0., 0.]" or [255, 0, 0]), '
                     'hex color (e.g. #112233 or #112233AA), or as a '
                     'matplotlib color name (e.g. "red" or "r").')

SY_COLOR_PARAMS = {'label': 'Color',
                   'type': 'colortype',
                   'icon': lambda value: color_icon(value),
                   'default': None,
                   'options': colors.COLORS,
                   'description': COLOR_DESCRIPTION,
                   'editor': fig_widgets.SyColorEdit}

SY_COLORMAP_PARAMS = {'label': 'Colormap',
                      'type': 'options',
                      'icon': SvgIcon.color,
                      'default': 'auto',
                      'options': list(colors.COLORMAPS.keys()),
                      'description': (
                          'Specify the name of a colormap. '
                          'Default behavior (auto) tries to '
                          'determine a fitting colormap depending '
                          'on the data.'),
                      'editor': tree_widgets.SyComboBox}

SY_COLORMAP_MIN_PARAMS = {'label': 'Colormap Min',
                          'type': float,
                          'icon': SvgIcon.colorbar_min,
                          'default': 0.0,
                          'options': None,
                          'description': (
                              'Specify the lowest value that should be '
                              'represented by the colormap.'),
                          'editor': tree_widgets.SyFloatLineEdit}

SY_COLORMAP_MAX_PARAMS = {'label': 'Colormap Max',
                          'type': float,
                          'icon': SvgIcon.colorbar_min,
                          'default': 0.0,
                          'options': None,
                          'description': (
                              'Specify the highest value that should be '
                              'represented by the colormap.'),
                          'editor': tree_widgets.SyFloatLineEdit}

SY_NORMALIZATION_PARAMS = {'label': 'Colormap scale',
                           'type': 'options',
                           'icon': SvgIcon.scales,
                           'default': 'linear',
                           'options': ['linear', 'log'],
                           'description': (
                               'Choose between linear and '
                               'logarithmic color scale. '),
                           'editor': tree_widgets.SyComboBox}

SY_EDGECOLOR_PARAMS = {'label': 'Edge Color',
                       'type': 'colortype',
                       'icon': lambda value: color_icon(value),
                       'default': None,
                       'options': colors.COLORS,
                       'description': COLOR_DESCRIPTION,
                       'editor': fig_widgets.SyColorEdit}

SY_LINEWIDTH_PARAMS = {'label': 'Line Width',
                       'type': float,
                       'icon': SvgIcon.linewidth,
                       'default': '1.',
                       'options': (0., None, 1.),
                       'description': (
                           'Specify the line width as floating '
                           'point number.'),
                       'editor': tree_widgets.SyDoubleSpinBox}

SY_LINESTYLE_PARAMS = {'label': 'Line Style',
                       'type': str,
                       'icon': SvgIcon.linestyle,
                       'default': 'solid',
                       'options': mpl_utils.LINESTYLES,
                       'description': (
                           'Specify the line style (e.g. "solid" or'
                           '"dashed").'),
                       'editor': tree_widgets.SyComboBox}

SY_MARKER_PARAMS = {'label': 'Marker',
                    'type': str,
                    'icon': SvgIcon.marker,
                    'default': 'circle',
                    'options': list(mpl_utils.MARKERS.values()),
                    'description': (
                        'Specify the marker used, cannot be an array'),
                    'editor': tree_widgets.SyComboBox}

SY_DRAWSTYLE_PARAMS = {'label': 'Draw Style',
                       'type': 'options',
                       'icon': SvgIcon.drawstyle,
                       'default': 'default',
                       'options': mpl_utils.DRAWSTYLES,
                       'description': 'Specify the draw style.',
                       'editor': tree_widgets.SyComboBox}

SY_SIZEBASE_PARAMS = {'label': 'Size',
                      'type': float,
                      'icon': SvgIcon.ruler,
                      'default': 1.,
                      'options': (0., None, 1.),
                      'description': 'Specify the size.',
                      'editor': tree_widgets.SyDoubleSpinBox}

SY_ALPHA_PARAMS = {'label': 'Alpha',
                   'type': float,
                   'icon': SvgIcon.alpha,
                   'default': 1.,
                   'options': (0., 1., 0.05),
                   'description': 'Specify the transparency (alpha) value.',
                   'editor': tree_widgets.SyDoubleSpinBox}

SY_ZORDER_PARAMS = {'label': 'Z-Order',
                    'type': int,
                    'icon': SvgIcon.layer,
                    'default': 1,
                    'options': (1, None, 1),
                    'description': 'Specify the stack order. Higher numbers '
                                   'get plotted on top of lower numbers.',
                    'editor': tree_widgets.SyIntSpinBox}

SY_BAR_LABEL_VALIGN_PARAMS = {'label': 'Bar Labels VAlign',
                              'type': 'options',
                              'icon': SvgIcon.barlabelvalgin,
                              'default': 'center',
                              'options': [
                                  'under', 'bottom', 'center', 'top', 'over'],
                              'description': 'Specify the location for the '
                                             'Bar Label.',
                              'editor': tree_widgets.SyComboBox}

SY_VISIBLE_PARAMS = {'label': 'Visible',
                     'type': bool,
                     'icon': lambda v: create_icon(
                         SvgIcon.visible if v else SvgIcon.invisible),
                     'default': True,
                     'options': None,
                     'description': 'Enable/disable if this item should be '
                                    'shown in the figure.',
                     'editor': tree_widgets.SyBoolComboBox}

SY_FONTSIZE_PARAMS = {'label': 'Font Size',
                      'type': float,
                      'icon': SvgIcon.text,
                      'default': 12.,
                      'options': (0., None, 1.),
                      'description': (
                          'Specify the font size in points (1/72 inch). '
                          'Actual size in pixels on screen or rendered images '
                          'depend on output DPI'),
                      'editor': tree_widgets.SyDoubleSpinBox}

SY_FONTCOLOR_PARAMS = {'label': 'Font color',
                       'type': 'colortype',
                       'icon': lambda value: color_icon(value),
                       'default': None,
                       'options': colors.COLORS,
                       'description': COLOR_DESCRIPTION,
                       'editor': fig_widgets.SyColorEdit}

SY_FILLED_PARAMS = {'label': 'Filled',
                    'type': bool,
                    'icon': SvgIcon.filled,
                    'default': True,
                    'options': None,
                    'description': 'If true then draw filled rectangles',
                    'editor': tree_widgets.SyBoolComboBox}

SY_MARKER_SIZE_PARAMS = {
    'label': 'Markersize',
    'type': float,
    'icon': SvgIcon.markersize,
    'default': 20,
    'options': None,
    'description': 'Specify the area of the markers.',
    'editor': tree_widgets.SyFloatLineEdit
}

SY_ROTATION_PARAMS = {
    'label': 'Rotation',
    'type': float,
    'icon': SvgIcon.angle,
    'default': 0,
    'options': (0., 360., 0.1),
    'description': 'Rotation measured in degrees',
    'editor': tree_widgets.SyDoubleSpinBox,
}

SY_WIDTH_PARAMS = {
    'label': 'Width',
    'type': str,
    'icon': SvgIcon.x_data,
    'default': '',
    'options': None,
    'description': (
        'Specify the column used as width as a python expression '
        'which evaluates to a numpy ndarray'),
    'editor': None
}

SY_HEIGHT_PARAMS = {
    'label': 'Height',
    'type': str,
    'icon': SvgIcon.y_data,
    'default': '',
    'options': None,
    'description': (
        'Specify the column used as height as a python expression '
        'which evaluates to a numpy ndarray'),
    'editor': None
}

SY_BAR_ORIENTATION_PARAMS = {
    'label': 'Bar orientation',
    'type': str,
    'icon': SvgIcon.height,
    'default': 'Vertical',
    'options': ['Vertical', 'Horizontal'],
    'description': (
        'Orientation of the bars. If Vertical (default) draws bars '
        'standing next to each other, if Horizontal draws bars lying '
        'on top of each other.'),
    'editor': tree_widgets.SyComboBox}


class FigureBaseNode(BaseNode):
    def create_leaf(self, leaf, data=None, eval=None, params=None):
        if params is None:
            params = self.NODE_LEAFS.get(leaf)
        if data is None:
            data = str(params['default'])
        # add the data to the model if required but not existing
        is_required = leaf in self.REQUIRED_LEAFS
        default_eval = 'py' if params['editor'] is None else 'value'
        leaf_cls = FigureRequiredProperty if is_required else FigureProperty
        leaf_inst = leaf_cls({'label': params['label'],
                              'name': leaf,
                              'type': params['type'],
                              'default': str(params['default']),
                              'icon': params['icon'],
                              'options': params['options'],
                              'editor': params['editor'],
                              'description': params.get('description', ''),
                              'data': data,
                              'eval': eval or default_eval},
                             parent=None)
        return leaf_inst

    def export_config(self, eval=False, extra_vars=None):
        """Export configuration."""
        config = {}
        for child in self.children:
            child_config = child.export_config(eval, extra_vars)
            if isinstance(child, FigureProperty):
                config.update(child_config)
            else:
                name = child.node_type
                if NodeTags.unique in child.cls_tags:
                    config[name] = child_config
                else:
                    config.setdefault(name, [])
                    config[name].append(child_config)
        return config


class FigureProperty(Property):
    def set_data(self, value, eval):
        if eval == 'py':
            self.data = value
        elif eval == 'value':
            value = common.parse_type(value, self.type, self.options)
            self.data = str(value)
        else:
            raise ValueError("Unknown eval method: {}".format(eval))
        self.eval = eval

    def parsed_value(self, extra_vars=None):
        if self.eval == 'py':
            data_table = self.root_node().get_data_table()
            value = common.parse_value(
                self.data, data_table=data_table, extra_vars=extra_vars)
        elif self.eval == 'value':
            value = common.parse_type(self.data, self.type, self.options)
        return value

    def get_icon(self):
        if isinstance(self.icon, types.FunctionType):
            try:
                value = self.parsed_value()
                icon = self.icon(value)
            except Exception:
                icon = self.icon(self.default)
        else:
            icon = create_icon(self.icon)
        return icon

    def export_config(self, eval=False, extra_vars=None):
        """Evaluate property if eval is True."""
        if eval:
            value = self.parsed_value(extra_vars=extra_vars)
        else:
            value = (self.data, self.eval)
        return {self.name: value}


class FigureRequiredProperty(FigureProperty):
    """A property which is not deletable."""
    cls_tags = frozenset({NodeTags.editable})


class Root(FigureBaseNode):
    """Root node."""

    node_type = 'root'
    cls_tags = frozenset({NodeTags.root})

    def __init__(self, data, parent=None):
        super(Root, self).__init__(data, parent)
        self._data_table = None
        self._given_ids = defaultdict(int)

    def init(self, data):
        # Figure is the root object of the stored data model:
        figure = Figure(data, parent=self)
        self.children = [figure]

    @classmethod
    def valid_children(cls):
        return frozenset({Figure})

    def set_data_table(self, data_table):
        self._data_table = data_table

    def get_data_table(self):
        return self._data_table

    def export_config(self, eval=False, extra_vars=None):
        return self.children[0].export_config(eval, extra_vars)


class Figure(FigureBaseNode):
    """Figure node."""

    node_type = 'figure'
    description = 'The base figure.'
    cls_tags = frozenset({NodeTags.unique})

    NODE_LEAFS = OrderedDict([
        ('title', {'label': 'Title',
                   'type': str,
                   'icon': SvgIcon.label,
                   'default': '',
                   'options': None,
                   'editor': tree_widgets.SyLabelEdit})
    ])

    @classmethod
    def valid_children(cls):
        return frozenset({Axes, Legend, FigureProperty})

    def init(self, data):
        for axes_data in data.pop('axes', []):
            axes = Axes(axes_data, parent=self)
            self.children.append(axes)
        self.add_children_to_node(data, [Legend])

    def has_axes(self):
        return any([isinstance(child, Axes) for child in self.children])


class Axes(FigureBaseNode):
    """Axes node."""

    icon = SvgIcon.plot
    default_data = {
        'xaxis': {'position': ('bottom', 'value')},
        'yaxis': {'position': ('left', 'value')},
        'plots': []}

    node_type = 'axes'
    needs_id = True
    description = ('The axes defines the axes labels, axes limits, etc. and '
                   'contains the different plot types (e.g. LinePlot, etc.).')

    cls_tags = frozenset({
        NodeTags.deletable,
        NodeTags.rearrangable,
        NodeTags.is_container,
        NodeTags.editable,
        NodeTags.copyable})

    NODE_LEAFS = OrderedDict([
        ('title', {'label': 'Title',
                   'type': str,
                   'icon': SvgIcon.label,
                   'default': '',
                   'options': None,
                   'description': 'Specify the title of the Axes.',
                   'editor': tree_widgets.SyLabelEdit}),
        ('aspect', {'label': 'Aspect Ratio',
                    'type': str,
                    'icon': SvgIcon.aspect,
                    'default': 'auto',
                    'options': ['auto', 'equal', '1.'],
                    'description': 'Specify the aspect ratio of the axes.',
                    'editor': tree_widgets.SyComboBoxEditable}),
        ('color_cycle', {'label': 'Color cycle',
                         'type': 'options',
                         'icon': SvgIcon.color,
                         'default': 'default',
                         'options': list(colors.COLOR_CYCLES.keys()),
                         'description': 'Color cycle used to select next '
                                        'default colors for plots.',
                         'editor': tree_widgets.SyComboBox}),
        ('frameon', {'label': 'Show frame',
                     'type': bool,
                     'icon': SvgIcon.show_frame,
                     'default': True,
                     'options': None,
                     'description': 'Shows a frame around the plot',
                     'editor': tree_widgets.SyBoolComboBox}),
        ('color', SY_COLOR_PARAMS),
    ])

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty, XAxis, YAxis, Plots, Legend, Grid})

    def init(self, data):
        for axis_type, axis_cls in zip(['xaxis', 'yaxis'], [XAxis, YAxis]):
            c_data = data.pop(axis_type, copy.deepcopy(axis_cls.default_data))
            if c_data is not None:
                self.children.append(axis_cls(c_data, parent=self))

        plots = Plots(data.pop('plots', []), parent=self)
        self.children.append(plots)
        for child_cls in [Legend, Grid]:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)

    def plots(self):
        """Return a list of all plot objects."""
        plot_parent = self.plot_container
        return [c for c in plot_parent.children if isinstance(c, BasePlot)]

    @property
    def plot_container(self):
        for child in self.children:
            if isinstance(child, Plots):
                return child
        return None

    @property
    def label(self):
        title_child = self.get_leaf_with_name('title')
        if title_child is not None:
            title = title_child.parsed_value()
            return '{} ({})'.format(self.prettify_class_name(), title)
        return super(Axes, self).label


class Colorbar(FigureBaseNode):
    icon = SvgIcon.color
    node_type = 'colorbar'
    default_data = {
        'show': ('True', 'value')}

    description = 'Defines Colorbar properties.'
    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.copyable,
        NodeTags.unique,
        NodeTags.deletable})

    NODE_LEAFS = OrderedDict([
        ('show', SY_VISIBLE_PARAMS),
        ('orientation', {'label': 'Orientation',
                         'type': 'options',
                         'icon': SvgIcon.colorbar_orientation,
                         'default': 'vertical',
                         'options': ['vertical', 'horizontal'],
                         'description': ('Specify the orientation of the '
                                         'colorbar.'),
                         'editor': tree_widgets.SyComboBox}),
        ('label', SY_LABEL_PARAMS),
    ])
    REQUIRED_LEAFS = set()

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})


class ErrorBar(FigureBaseNode):
    icon = SvgIcon.errorbar
    node_type = 'errorbar'
    default_data = {}

    description = 'Defines errorbar properties.'
    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.copyable,
        NodeTags.unique,
        NodeTags.deletable})

    NODE_LEAFS = OrderedDict([
        ('xerr', SY_XERR_PARAMS),
        ('yerr', SY_YERR_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('ecolor', SY_COLOR_PARAMS),
        ('capsize',
         {'label': 'Cap Size',
          'type': float,
          'icon': SvgIcon.errorbar,
          'default': '6.',
          'options': (0., None, 1.),
          'description': (
              'Specify the size of the caps on the end of the error bars, '
              'measured in points.'),
          'editor': tree_widgets.SyDoubleSpinBox}),
        ('capthick',
         {'label': 'Cap Thickness',
          'type': float,
          'icon': SvgIcon.linewidth,
          'default': '1.',
          'options': (0., None, 1.),
          'description': 'Specify the width of error bar caps in points.',
          'editor': tree_widgets.SyDoubleSpinBox}),
        ('elinewidth',
         {'label': 'Thickness',
          'type': float,
          'icon': SvgIcon.linewidth,
          'default': '1.',
          'options': (0., None, 1.),
          'description': 'Specify the width of error bars in points.',
          'editor': tree_widgets.SyDoubleSpinBox}),
    ])
    REQUIRED_LEAFS = set()

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})


class BoxBackground(FigureBaseNode):
    icon = SvgIcon.label
    node_type = 'boxbackground'
    default_data = {}

    description = 'Defines boundingbox background properties.'
    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.copyable,
        NodeTags.unique,
        NodeTags.deletable})

    NODE_LEAFS = OrderedDict([
        ('color', {'label': 'Color',
                   'type': 'colortype',
                   'icon': lambda value: color_icon(value),
                   'default': None,
                   'options': colors.COLORS,
                   'description': COLOR_DESCRIPTION,
                   'editor': fig_widgets.SyColorEdit}),
        ('border', {'label': 'Border',
                    'type': 'colortype',
                    'icon': lambda value: color_icon(value),
                    'default': None,
                    'options': colors.COLORS,
                    'description': COLOR_DESCRIPTION,
                    'editor': fig_widgets.SyColorEdit}),
        ('style', {'label': 'Style',
                   'type': 'options',
                   'icon': SvgIcon.rounded_rectangle,
                   'default': 'rounded',
                   'options': ['circle', 'darrow', 'larrow', 'rarrow',
                               'rounded', 'roundtooth', 'sawtooth'],
                   'description': 'Style of box around the text',
                   'editor': tree_widgets.SyComboBox}),
    ])
    REQUIRED_LEAFS = set(['color'])

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})


class AnnotationArrow(FigureBaseNode):
    icon = SvgIcon.arrow
    node_type = 'arrow'
    default_data = {}

    description = 'Defines the properties for annotation arrows.'
    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.copyable,
        NodeTags.unique,
        NodeTags.deletable})

    NODE_LEAFS = OrderedDict([
        ('annotate_x', {
            'label': 'Annotated X',
            'type': float,
            'icon': SvgIcon.plot,
            'default': 0.0,
            'options': None,
            'description': 'Position given as scalar or a column/array. '
                           'Default 0.0',
            'editor': tree_widgets.SyFloatLineEdit}),
        ('annotate_y', {
            'label': 'Annotated Y',
            'type': float,
            'icon': SvgIcon.plot,
            'default': 0.0,
            'options': None,
            'description': 'Position given as scalar or a column/array. '
                           'Default 0.0',
            'editor': tree_widgets.SyFloatLineEdit}),
        ('shrink', {
            'label': 'Shrink',
            'type': float,
            'icon': SvgIcon.ruler,
            'default': 0.0,
            'options': (0., 1.0, 0.05),
            'description': 'Shrinks the arrow from text to annotatated point.',
            'editor': tree_widgets.SyDoubleSpinBox}),
        ('facecolor', SY_COLOR_PARAMS),
        ('edgecolor', {'label': 'Edge Color',
                       'type': 'colortype',
                       'icon': lambda value: color_icon(value),
                       'default': None,
                       'options': colors.COLORS,
                       'description': COLOR_DESCRIPTION,
                       'editor': fig_widgets.SyColorEdit}),
        ('arrow_width', {
            'label': 'Arrow Width',
            'type': float,
            'icon': SvgIcon.ruler,
            'default': 4.0,
            'options': None,
            'description': 'Width of the arrow in points.',
            'editor': tree_widgets.SyFloatLineEdit}),
        ('arrow_length', {
            'label': 'Arrow Head Length',
            'type': float,
            'icon': SvgIcon.ruler,
            'default': 10.0,
            'options': None,
            'description': 'Length of arrow head in points.',
            'editor': tree_widgets.SyFloatLineEdit}),
        ('arrow_headwidth', {
            'label': 'Arrow Head Width',
            'type': float,
            'icon': SvgIcon.ruler,
            'default': 10.0,
            'options': None,
            'description': 'Width of the arrow head in points.',
            'editor': tree_widgets.SyFloatLineEdit}),
    ])
    REQUIRED_LEAFS = set(['annotate_x', 'annotate_y'])

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})


class BaseFont(FigureBaseNode):
    icon = SvgIcon.text
    node_type = 'font'
    default_data = {
        'color': ('#000000', 'value'),
        'size': (12, 'value')}

    description = 'Defines Font properties.'
    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.copyable,
        NodeTags.unique,
        NodeTags.deletable})

    NODE_LEAFS = OrderedDict([
        ('color', SY_COLOR_PARAMS),
        ('size', SY_SIZEBASE_PARAMS)
    ])

    REQUIRED_LEAFS = set()

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})


class BarLabelsFont(BaseFont):
    node_type = 'bar_labels_font'
    description = 'Defines the Font properties of the Bar Labels.'


class BasePlot(FigureBaseNode):
    needs_id = True
    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.deletable,
        NodeTags.copyable})

    REQUIRED_LEAFS = {'xdata', 'ydata'}

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if not c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)

    @property
    def label(self):
        label_child = self.get_leaf_with_name('label')
        if label_child is not None:
            label = label_child.parsed_value()
            return '{} ({})'.format(self.prettify_class_name(), label)
        return super(BasePlot, self).label

    def export_config(self, eval=False, extra_vars=None):
        config = super().export_config(eval, extra_vars)
        config['type'] = self.node_type
        return config


class LinePlot(BasePlot):
    icon = SvgIcon.line
    node_type = 'line'
    description = ('A Line Plot defined by x and y-data with different '
                   'linestyles, linewidth, additional makers, etc.')

    default_data = {
        'xdata': ('', 'py'),
        'ydata': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('xdata', SY_XDATA_PARAMS),
        ('ydata', SY_YDATA_PARAMS),
        ('label', SY_LABEL_PARAMS),
        ('marker', SY_MARKER_PARAMS),
        ('markersize', SY_MARKER_SIZE_PARAMS),
        ('markeredgecolor', {'label': 'Marker Edge Color',
                             'type': 'colortype',
                             'icon': lambda value: color_icon(value),
                             'default': None,
                             'options': colors.COLORS,
                             'description': COLOR_DESCRIPTION,
                             'editor': fig_widgets.SyColorEdit}),
        ('markeredgewidth', {'label': 'Markeredgewidth',
                             'type': float,
                             'icon': SvgIcon.linewidth,
                             'default': 0.1,
                             'options': (0., None, 0.01),
                             'editor': tree_widgets.SyDoubleSpinBox}),
        ('markerfacecolor', {'label': 'Marker Face Color',
                             'type': 'colortype',
                             'icon': lambda value: color_icon(value),
                             'default': None,
                             'options': colors.COLORS,
                             'description': COLOR_DESCRIPTION,
                             'editor': fig_widgets.SyColorEdit}),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('color', SY_COLOR_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('drawstyle', SY_DRAWSTYLE_PARAMS),
        ('show', SY_VISIBLE_PARAMS),
    ])


class Lines(BasePlot):
    icon = SvgIcon.lines
    node_type = 'lines'
    description = (
        'A set of separate lines defined by starting and '
        'ending x and y coordinates')

    default_data = {
        'startx': ('', 'py'),
        'starty': ('', 'py'),
        'endx': ('', 'py'),
        'endy': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('startx', {'label': 'Start X',
                    'type': str,
                    'icon': SvgIcon.x_data,
                    'default': '',
                    'options': None,
                    'description': (
                        'Specify the column used as start x as a python '
                        'expression which evaluates to a numpy ndarray'),
                    'editor': None}),
        ('starty', {'label': 'Start Y',
                    'type': str,
                    'icon': SvgIcon.y_data,
                    'default': '',
                    'options': None,
                    'description': (
                        'Specify the column used as start y as a python '
                        'expression which evaluates to a numpy ndarray'),
                    'editor': None}),
        ('endx', {'label': 'End X',
                  'type': str,
                  'icon': SvgIcon.x_data,
                  'default': '',
                  'options': None,
                  'description': (
                        'Specify the column used as end x as a python '
                        'expression which evaluates to a numpy ndarray'),
                  'editor': None}),
        ('endy', {'label': 'End Y',
                  'type': str,
                  'icon': SvgIcon.y_data,
                  'default': '',
                  'options': None,
                  'description': (
                        'Specify the column used as end y as a python '
                        'expression which evaluates to a numpy ndarray'),
                  'editor': None}),
        ('marker', SY_MARKER_PARAMS),
        ('markersize', SY_MARKER_SIZE_PARAMS),
        ('markeredgecolor', {'label': 'Marker Edge Color',
                             'type': 'colortype',
                             'icon': lambda value: color_icon(value),
                             'default': None,
                             'options': colors.COLORS,
                             'description': COLOR_DESCRIPTION,
                             'editor': fig_widgets.SyColorEdit}),
        ('markeredgewidth', {'label': 'Marker Edge Width',
                             'type': float,
                             'icon': SvgIcon.linewidth,
                             'default': 0.1,
                             'options': (0., None, 0.01),
                             'editor': tree_widgets.SyDoubleSpinBox}),
        ('markerfacecolor', {'label': 'Marker Face Color',
                             'type': 'colortype',
                             'icon': lambda value: color_icon(value),
                             'default': None,
                             'options': colors.COLORS,
                             'description': COLOR_DESCRIPTION,
                             'editor': fig_widgets.SyColorEdit}),
        ('label', SY_LABEL_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('color', SY_COLOR_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('show', SY_VISIBLE_PARAMS),
    ])


class Rectangles(BasePlot):
    icon = SvgIcon.rectangles
    node_type = 'rectangles'
    description = (
        'Draws rectangles at the given positions')

    default_data = {
        'xdata': ('', 'py'),
        'ydata': ('', 'py'),
        'width': ('', 'py'),
        'height': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('xdata', SY_XDATA_PARAMS),
        ('ydata', SY_YDATA_PARAMS),
        ('width', SY_WIDTH_PARAMS),
        ('height', SY_HEIGHT_PARAMS),
        ('angle', SY_ROTATION_PARAMS),
        ('label', SY_LABEL_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('facecolor', SY_COLOR_PARAMS),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('fill', SY_FILLED_PARAMS),
        ('show', SY_VISIBLE_PARAMS),
    ])


class Ellipses(BasePlot):
    icon = SvgIcon.ellipses
    node_type = 'ellipses'
    description = (
        'Draws ellipses or circles at the given positions')

    default_data = {
        'xdata': ('', 'py'),
        'ydata': ('', 'py'),
        'width': ('', 'py'),
        'height': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('xdata', SY_XDATA_PARAMS),
        ('ydata', SY_YDATA_PARAMS),
        ('width', SY_WIDTH_PARAMS),
        ('height', SY_HEIGHT_PARAMS),
        ('angle', SY_ROTATION_PARAMS),
        ('label', SY_LABEL_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('facecolor', SY_COLOR_PARAMS),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('fill', SY_FILLED_PARAMS),
        ('show', SY_VISIBLE_PARAMS),
    ])


class PieChart(BasePlot):
    icon = SvgIcon.piechart
    node_type = 'pie'
    description = 'A Pie Chart showing the proportions of different parts.'

    default_data = {
        'weights': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('weights', {
            'label': 'Weights',
            'type': str,
            'icon': SvgIcon.x_data,
            'default': '',
            'options': None,
            'description': (
                'Specify the column used as pie sizes as python '
                'expression which evaluates to a numpy ndarray'),
            'editor': None
            }),
        ('labels', {
            'label': 'Labels',
            'type': str,
            'icon': SvgIcon.labels,
            'default': '',
            'options': None,
            'description': (
                'Specify the column used as pie sizes as python '
                'expression which evaluates to a numpy ndarray'),
            'editor': None
            }),
        ('colors', {
            'label': 'Colors',
            'type': str,
            'icon': SvgIcon.color,
            'default': '',
            'options': None,
            'description': (
                'Specify the column used to colour each slices.'),
            'editor': None
            }),
        ('explode', {
            'label': 'Explode',
            'type': float,
            'icon': SvgIcon.piechart_explode,
            'default': '',
            'options': (0., None, 0.1),
            'description': (
                'Specify a scalar or the column used to give distances '
                'with which pie-pieces are moved away from the center'),
            'editor': tree_widgets.SyDoubleSpinBox
            }),
        ('center', {
            'label': 'Center',
            'type': str,
            'icon': SvgIcon.plot,
            'default': '(0.0, 0.0)',
            'options': None,
            'description': (
                'Center point of piechart on plot given as a tuple of two '
                'values. Default (0.0, 0.0)'),
            'editor': None
            }),
        ('labeldistance', {
            'label': 'Label position',
            'type': float,
            'icon': SvgIcon.ruler,
            'default': 1.1,
            'options': (0., 2.0, 0.05),
            'description': (
                'Position of labels from center relative to piechart radius.'),
            'editor': tree_widgets.SyDoubleSpinBox}),
        ('labelhide', {
            'label': 'Hide labels',
            'type': bool,
            'icon': SvgIcon.labels,
            'default': False,
            'options': None,
            'description': (
                'If true then do not draw the labels directly, but preserve '
                'them for use by the legend (if used)'),
            'editor': tree_widgets.SyBoolComboBox}),
        ('autopct', {
            'label': 'Percentage',
            'type': str,
            'icon': SvgIcon.percentage,
            'default': 'None',
            'options': ['None', 'Auto'],
            'description': (
                'Adds percentage labels to each slice using the '
                'Python "%" operator. Eg: "Foo %.2" gives the '
                'labels "Foo 0.00". '
                'You can also give a lambda expression'),
            'editor': tree_widgets.SyComboBoxEditable}),
        ('pctdistance', {
            'label': 'Percentage position',
            'type': float,
            'icon': SvgIcon.ruler,
            'default': 0.6,
            'options': (0., 1.0, 0.05),
            'description': 'Position of percentage labels.',
            'editor': tree_widgets.SyDoubleSpinBox}),
        ('startangle', {
            'label': 'Starting angle',
            'type': float,
            'icon': SvgIcon.ruler,
            'default': 0,
            'options': (0., 360.0, 0.10),
            'description': 'Degrees to rotate start of pie chart.',
            'editor': tree_widgets.SyDoubleSpinBox}),
        ('radius', {
            'label': 'Radius',
            'type': float,
            'icon': SvgIcon.diameter,
            'default': 1.0,
            'options': None,
            'description': 'Radius of the pie chart.',
            'editor': tree_widgets.SyFloatLineEdit}),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('fontsize', SY_FONTSIZE_PARAMS),
        ('fontcolor', SY_FONTCOLOR_PARAMS),
        ('show', SY_VISIBLE_PARAMS),
    ])


class Annotation(BasePlot):
    icon = SvgIcon.text
    node_type = 'annotation'
    description = (
        'Draws text from a string or a column of strings, can optionally also '
        'draw an arrow that points to a specific XY point.')

    default_data = {
        'text': ('', 'value'),
        'textx': ('0.0', 'value'),
        'texty': ('0.0', 'value')}

    NODE_LEAFS = OrderedDict([
        ('text', {
            'label': 'Text',
            'type': str,
            'icon': SvgIcon.text,
            'default': '',
            'options': None,
            'description': (
                'A text string or a python expression evaluating to a '
                'text string'),
            'editor': tree_widgets.SyBaseTextEdit}),
        ('textx', {
            'label': 'Text X',
            'type': float,
            'icon': SvgIcon.plot,
            'default': '0.0',
            'options': None,
            'description': 'Position given as scalar or a column/array. '
                           'Default 0.0',
            'editor': tree_widgets.SyFloatLineEdit}),
        ('texty', {
            'label': 'Text Y',
            'type': float,
            'icon': SvgIcon.plot,
            'default': '0.0',
            'options': None,
            'description': 'Position given as scalar or a column/array. '
                           'Default 0.0',
            'editor': tree_widgets.SyFloatLineEdit}),
        ('fontsize', SY_FONTSIZE_PARAMS),
        ('fontcolor', SY_FONTCOLOR_PARAMS),
        ('textalpha', {
            'label': 'Text alpha',
            'type': float,
            'icon': SvgIcon.alpha,
            'default': 1.,
            'options': (0., 1., 0.05),
            'description': (
                'Specify the transparency (alpha) value for the text.'),
            'editor': tree_widgets.SyDoubleSpinBox}),
        ('rotation', SY_ROTATION_PARAMS),
        ('vert_align', {
            'label': 'Vertical Alignment',
            'type': 'options',
            'icon': SvgIcon.vert_align,
            'default': 'center',
            'options': ['top', 'center', 'bottom', 'baseline'],
            'description': 'Vertical alignment of text relative to point',
            'editor': tree_widgets.SyComboBox}),
        ('horz_align', {
            'label': 'Horizontal Alignment',
            'type': 'options',
            'icon': SvgIcon.horz_align,
            'default': 'left',
            'options': ['left', 'center', 'right'],
            'description': 'Horizontal alignment of text relative to point',
            'editor': tree_widgets.SyComboBox}),
        ('show', SY_VISIBLE_PARAMS),
    ])

    @classmethod
    def valid_children(cls):
        return frozenset({BoxBackground, AnnotationArrow, FigureProperty})


class ScatterPlot(BasePlot):
    icon = SvgIcon.scatter
    node_type = 'scatter'
    description = ('A Scatter Plot defined by x and y-data with different '
                   'marker styles, sizes, etc.')

    default_data = {
        'xdata': ('', 'py'),
        'ydata': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('xdata', SY_XDATA_PARAMS),
        ('ydata', SY_YDATA_PARAMS),
        ('label', SY_LABEL_PARAMS),
        ('s', SY_MARKER_SIZE_PARAMS),
        ('edgecolors', {'label': 'Marker Edge Color',
                        'type': 'colortype',
                        'icon': lambda value: color_icon(value),
                        'default': None,
                        'options': colors.COLORS,
                        'description': COLOR_DESCRIPTION,
                        'editor': fig_widgets.SyColorEdit}),
        ('linewidths', {'label': 'Marker Edge Width',
                        'type': float,
                        'icon': SvgIcon.linewidth,
                        'default': 0.1,
                        'options': (0., None, 0.01),
                        'editor': tree_widgets.SyDoubleSpinBox}),
        ('color', SY_COLOR_PARAMS),
        ('cmap', SY_COLORMAP_PARAMS),
        ('vmin', SY_COLORMAP_MIN_PARAMS),
        ('vmax', SY_COLORMAP_MAX_PARAMS),
        ('marker', SY_MARKER_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('show', SY_VISIBLE_PARAMS),
    ])

    @classmethod
    def valid_children(cls):
        return frozenset({Colorbar, FigureProperty, ErrorBar})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if not c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)


class HeatmapPlot(BasePlot):
    icon = SvgIcon.heatmap
    node_type = 'heatmap'
    description = ('A heatmap plot defined by x, y, and z-data. The color of '
                   'each cell corresponds to the z-value at those x and '
                   'y-coordinates.')

    default_data = {
        'xdata': ('', 'py'),
        'ydata': ('', 'py'),
        'zdata': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('xdata', SY_XDATA_PARAMS),
        ('ydata', SY_YDATA_PARAMS),
        ('zdata', SY_ZDATA_PARAMS),
        ('vmin', SY_COLORMAP_MIN_PARAMS),
        ('vmax', SY_COLORMAP_MAX_PARAMS),
        ('colormap', SY_COLORMAP_PARAMS),
        ('normalization', SY_NORMALIZATION_PARAMS),
        ('zlabels', {'label': 'Z Labels',
                     'type': str,
                     'icon': SvgIcon.label,
                     'default': '',
                     'options': None,
                     'description': 'Specify data used as "Labels" printed '
                                    'in each bin. Should a python expression '
                                    'which evaluates to a numpy ndarray',
                     'editor': None}),
        ('zorder', SY_ZORDER_PARAMS),
        ('show', SY_VISIBLE_PARAMS),
    ])

    REQUIRED_LEAFS = {'xdata', 'ydata', 'zdata'}

    @classmethod
    def valid_children(cls):
        return frozenset({Colorbar, FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if not c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)


class BarPlot(BasePlot):
    icon = SvgIcon.bar
    node_type = 'bar'
    description = ('A Bar Plot for categorical y-data. Additional '
                   '"Bin Labels" can be given as x-axis labels.')

    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.deletable,
        NodeTags.copyable})

    default_data = {
        'ydata': ('', 'py'),
        'bin_labels': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('ydata', SY_YDATA_PARAMS),
        ('yerr', SY_YERR_PARAMS),
        ('bin_labels', {'label': 'Bin Labels',
                        'type': str,
                        'icon': SvgIcon.label,
                        'default': '',
                        'options': None,
                        'description': 'Specify data used as "Labels" plotted '
                                       'on the x-axis as a python expression '
                                       'which evaluates to a numpy ndarray',
                        'editor': None}),
        ('label', SY_LABEL_PARAMS),
        ('bar_labels', {'label': 'Bar Labels',
                        'type': str,
                        'icon': SvgIcon.label,
                        'default': '',
                        'options': None,
                        'description': 'Specify data used as "Labels" plotted '
                                       'on top of the Bars as a python '
                                       'expression which evaluates to a numpy '
                                       'ndarray',
                        'editor': None}),
        ('bar_labels_valign', SY_BAR_LABEL_VALIGN_PARAMS),
        ('rwidth', {'label': 'Width',
                    'type': float,
                    'icon': SvgIcon.barwidth,
                    'default': 0.8,
                    'options': (0., 1., 0.05),
                    'description': 'Specify the width of the bins, '
                                   'between 0 and 1.',
                    'editor': tree_widgets.SyDoubleSpinBox}),
        ('orientation', SY_BAR_ORIENTATION_PARAMS),
        ('color', SY_COLOR_PARAMS),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('show', SY_VISIBLE_PARAMS),
    ])

    REQUIRED_LEAFS = {'ydata'}

    @classmethod
    def valid_children(cls):
        return frozenset({BarLabelsFont, FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if not c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)


class BoxPlot(BasePlot):
    icon = SvgIcon.boxplot
    node_type = 'box'
    description = (
        'One or more box plots showing upper/lower quantile and outliers.')

    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.deletable,
        NodeTags.copyable})

    default_data = {
        'ydata': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('ydata', {
            'label': 'Y Data',
            'type': str,
            'icon': SvgIcon.y_data,
            'default': '',
            'options': None,
            'description': (
                'Specify a column or a LIST (inside brackets) of columns used '
                'as y-data.'),
            'editor': None}),
        ('positions', {
            'label': 'Positions',
            'type': str,
            'icon': SvgIcon.x_data,
            'default': '',
            'options': None,
            'description': (
                'List or array giving the position on the minor axis '
                '(usually X) of each boxplot'),
            'editor': None}),
        ('bin_labels', {
            'label': 'Bin Labels',
            'type': str,
            'icon': SvgIcon.label,
            'default': '',
            'options': None,
            'description': (
                'Specify data used as "Labels" plotted '
                'on the x-axis and in the legend, '
                'either as a list of strings or as '
                'a numpy array'),
            'editor': None}),
        ('marker', SY_MARKER_PARAMS),
        ('markersize', SY_MARKER_SIZE_PARAMS),
        ('filled', SY_FILLED_PARAMS),
        ('color', SY_COLOR_PARAMS),
        ('flier_color', {
            'label': 'Outlier Color',
            'type': 'colortype',
            'icon': lambda value: color_icon(value),
            'default': None,
            'options': colors.COLORS,
            'description': 'Specify a color either as RGB '
            '(e.g. "[1., 0., 0.]" or [255, 0, 0]), '
            'hex color (e.g. #ff00000), or as a '
            'matplotlib color name '
            '(e.g. "red" or "r").',
            'editor': fig_widgets.SyColorEdit}),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('notch', {
            'label': 'Notch',
            'type': bool,
            'icon': SvgIcon.show_frame,
            'default': False,
            'options': None,
            'description': (
                'Draws notches representing confidence interval '
                'around median'),
            'editor': tree_widgets.SyBoolComboBox}),
        ('orientation', {
            'label': 'Box orientation',
            'type': 'options',
            'icon': SvgIcon.height,
            'default': 'Vertical',
            'options': ['Vertical', 'Horizontal'],
            'description': (
                'Orientation of the boxplots. If Vertical (default) draws '
                'boxplots standing next to each other, if Horizontal draws '
                'boxplots lying on top of each other.'),
            'editor': tree_widgets.SyComboBox}),
        ('widths', {
            'label': 'Width',
            'type': float,
            'icon': SvgIcon.ruler,
            'default': 0.5,
            'options': (0., None, 1.),
            'description': 'Specify the width of the box plots, '
                           'between 0 and 1.',
            'editor': tree_widgets.SyDoubleSpinBox}),
        ('show', SY_VISIBLE_PARAMS),
    ])

    REQUIRED_LEAFS = {'ydata'}

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if not c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)


class HistogramPlot(BasePlot):
    icon = SvgIcon.histogram1d
    node_type = 'hist'
    description = ('A Histogram Plot for plotting sequential binned y-data in '
                   'Bar or Step style. The "Bin egdes" need to be given as '
                   '"Bin min edges" and "Bin max edges".')

    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.deletable,
        NodeTags.copyable})

    default_data = {
        'bin_min_edges': ('', 'py'),
        'bin_max_edges': ('', 'py'),
        'ydata': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('bin_min_edges', {'label': 'Bin min edges',
                           'type': str,
                           'icon': SvgIcon.bin_min_edge,
                           'default': '',
                           'options': None,
                           'description': 'Specify the column used as '
                                          '"Bin min edges" as a python '
                                          'expression which evaluates to '
                                          'a numpy ndarray.',
                           'editor': None}),
        ('bin_max_edges', {'label': 'Bin max edges',
                           'type': str,
                           'icon': SvgIcon.bin_max_edge,
                           'default': '',
                           'options': None,
                           'description': 'Specify the column used as '
                                          '"Bin max edges" as a python '
                                          'expression which evaluates to '
                                          'a numpy ndarray',
                           'editor': None}),
        ('ydata', SY_YDATA_PARAMS),
        ('bar_labels', {'label': 'Bar Labels',
                        'type': str,
                        'icon': SvgIcon.label,
                        'default': '',
                        'options': None,
                        'description': 'Specify data used as "Labels" plotted '
                                       'on the x-axis as a python expression '
                                       'which evaluates to a numpy ndarray',
                        'editor': None}),
        ('bar_labels_valign', SY_BAR_LABEL_VALIGN_PARAMS),
        ('label', SY_LABEL_PARAMS),
        ('color', SY_COLOR_PARAMS),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('edges', {'label': 'Edges between bars',
                   'type': bool,
                   'icon': SvgIcon.histtype,
                   'default': False,
                   'options': None,
                   'description': 'Specify if the Histogram gets plotted '
                                  'as individual bars with visible edges '
                                  'between or as a filled step line plot. '
                                  'This will only have a visible effect if '
                                  'an edge color has been set.',
                   'editor': tree_widgets.SyBoolComboBox}),
        ('show', SY_VISIBLE_PARAMS),
    ])

    REQUIRED_LEAFS = {'bin_min_edges', 'bin_max_edges', 'ydata'}

    @classmethod
    def valid_children(cls):
        return frozenset({BarLabelsFont, FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if not c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)


class TimelinePlot(BasePlot):
    icon = SvgIcon.timeline
    node_type = 'timeline'
    description = (
        'Plots a timeline of events or states. Requires a column with X '
        'values and a column with state-values. Draws one rectangle for each '
        'change in the state value.')

    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.deletable,
        NodeTags.copyable})

    default_data = {
        'xdata': ('', 'py'),
        'values': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('xdata', SY_XDATA_PARAMS),
        ('values', {'label': 'State values',
                    'type': str,
                    'icon': SvgIcon.x_data,
                    'default': '',
                    'options': None,
                    'description': (
                        'Specify the column used for values (numbers or text '
                        'that is is printed inside each interval) as a python '
                        'expression which evaluates to a numpy ndarray'),
                    'editor': None}),
        ('alpha', SY_ALPHA_PARAMS),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('fontsize', SY_FONTSIZE_PARAMS),
        ('fontcolor', SY_FONTCOLOR_PARAMS),
        ('y_start', {'label': 'Y start',
                     'type': float,
                     'icon': SvgIcon.ypos,
                     'default': 0,
                     'options': None,
                     'description': (
                         'The y coordinate of the bottom part of the '
                         'timeline plot'),
                     'editor': tree_widgets.SyFloatLineEdit}),
        ('y_height', {'label': 'Y height',
                      'type': float,
                      'icon': SvgIcon.ypos,
                      'default': 0.5,
                      'options': None,
                      'description': (
                          'A number or an expression giving a number that '
                          'gives the height of the timeline'),
                      'editor': tree_widgets.SyFloatLineEdit}),
        ('last_step', {'label': 'Last step',
                       'type': str,
                       'icon': SvgIcon.x_data,
                       'default': '',
                       'options': None,
                       'description': (
                           'The length that the last entry should extend to '
                           'the right. If not given this is calculated '
                           'automatically by assuming that the X values '
                           'increase constantly'),
                       'editor': None}),
        ('label', SY_LABEL_PARAMS),
        ('colormap_name', SY_COLORMAP_PARAMS),
        ('text_visible', {'label': 'Text visible',
                          'type': bool,
                          'icon': lambda v: create_icon(
                              SvgIcon.visible if v else SvgIcon.invisible),
                          'default': True,
                          'options': None,
                          'description': (
                              'Enable/disable if the text should be shown'),
                          'editor': tree_widgets.SyBoolComboBox}),
        ('add_to_legend', {'label': 'Add to legend',
                           'type': bool,
                           'icon': SvgIcon.legend,
                           'default': True,
                           'options': None,
                           'description': (
                               'Enable/disable if all values should be '
                               'added to the legend (if any).'),
                           'editor': tree_widgets.SyBoolComboBox}),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('filled', SY_FILLED_PARAMS),
        ('hatch', {'label': 'Hatch pattern',
                   'type': 'options',
                   'icon': SvgIcon.hatch_pattern,
                   'default': '/',
                   'options': ['/', '\\', '|', '-', '+',
                               'x', 'o', 'O', '.', '*'],
                   'description': (
                       'Draws a hatch pattern inside the rectangles'),
                   'editor': tree_widgets.SyComboBox}),
        ('show', SY_VISIBLE_PARAMS),
    ])

    REQUIRED_LEAFS = {'xdata', 'values'}

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)


class ImagePlot(BasePlot):
    icon = SvgIcon.imageplot
    node_type = 'image'
    description = (
        'Plots an image.')

    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.deletable,
        NodeTags.copyable})

    default_data = {
        'image': ('', 'py')}

    NODE_LEAFS = OrderedDict([
        ('image', {'label': 'Image',
                   'type': str,
                   'icon': SvgIcon.x_data,
                   'default': 'arg.im',
                   'options': None,
                   'description': (
                       'Image object (eg. "arg.im") or a 2D/3D numpy array'),
                   'editor': None}),
        ('vmin', SY_COLORMAP_MIN_PARAMS),
        ('vmax', SY_COLORMAP_MAX_PARAMS),
        ('colormap_name', SY_COLORMAP_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('origo', {'label': 'Origin',
                   'type': str,
                   'icon': SvgIcon.limit,
                   'default': '(0, 0)',
                   'options': None,
                   'description': (
                       'Specify the XY coordinate of the top-left corner '
                       '(origin) of the image'),
                   'editor': None}),
        ('width', {'label': 'Width',
                   'type': int,
                   'icon': SvgIcon.limit,
                   'default': 100,
                   'options': None,
                   'description': (
                       'Specify the drawn width of the image, '
                       'this should be a scalar value'),
                   'editor': tree_widgets.SyIntLineEdit}),
        ('height', {'label': 'Height',
                    'type': int,
                    'icon': SvgIcon.limit,
                    'default': 100,
                    'options': None,
                    'description': (
                        'Specify the drawn height of the image, '
                        'this should be a scalar value'),
                    'editor': tree_widgets.SyIntLineEdit}),
        ('show', SY_VISIBLE_PARAMS),
    ])

    REQUIRED_LEAFS = {'image'}

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)


class BasePlotContainer(FigureBaseNode):
    icon = SvgIcon.layers
    needs_id = True

    cls_tags = frozenset({NodeTags.is_container})

    PLOT_TYPES = {}

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def init(self, data):
        self.add_plots(data)

    def add_plots(self, data):
        for plot_data in data:
            plot_type = plot_data.get('type')
            if plot_type is None:
                continue
            plot_cls = self.PLOT_TYPES.get(plot_type)
            if plot_type is None:
                continue
            plot = plot_cls(plot_data, parent=self)
            self.children.append(plot)

    def export_config(self, eval=False, extra_vars=None):
        # Put all child plots under a 'plots' key.
        config = {}
        for child in self.children:
            child_config = child.export_config(eval, extra_vars)
            if isinstance(child, FigureProperty):
                config.update(child_config)
            elif isinstance(child_config, list):
                # Iterators return a list of plots if eval=True.
                config.setdefault('plots', []).extend(child_config)
            else:
                config.setdefault('plots', []).append(child_config)
        config['type'] = self.node_type
        return config


class Iterator(BasePlotContainer):
    icon = SvgIcon.iterator
    needs_id = True
    node_type = 'iterator'
    description = ('Repeat the contents while looping over an iterable. '
                   'Use this to create a dynamic number of plots.')

    cls_tags = frozenset({
        NodeTags.is_container,
        NodeTags.deletable,
        NodeTags.rearrangable,
        NodeTags.copyable})

    PLOT_TYPES = {
        'scatter': ScatterPlot,
        'line': LinePlot,
        'bar': BarPlot,
        'hist': HistogramPlot,
        'box': BoxPlot,
        'pie': PieChart,
        'annotation': Annotation,
        'timeline': TimelinePlot,
        'image': ImagePlot,
        'lines': Lines,
        'rectangles': Rectangles,
        'ellipses': Ellipses,
    }

    NODE_LEAFS = OrderedDict([
        ('iterable', {'label': 'Iterable',
                      'type': str,
                      'icon': None,
                      'default': 'e = ',
                      'options': None,
                      'description': '',
                      'editor': tree_widgets.SyIterableEdit}),
        ('counter', {'label': 'Counter name',
                     'type': str,
                     'icon': None,
                     'default': 'i',
                     'options': None,
                     'description': 'The variable name used for the '
                                    'incremental counter for this iterator.',
                     # 'editor': tree_widgets.SyIdentifierEdit})
                     'editor': tree_widgets.SyBaseTextEdit})
    ])

    REQUIRED_LEAFS = {'iterable'}

    default_data = {'plots': []}

    @classmethod
    def valid_children(cls):
        return frozenset(
            set(cls.PLOT_TYPES.values()) | {FigureProperty})

    def init(self, data):
        self.add_plots(data)

    def add_plots(self, data):
        for plot_data in data.pop('plots', []):
            plot_type = plot_data.get('type')
            if plot_type is not None:
                plot_cls = self.PLOT_TYPES.get(plot_type)
                plot = plot_cls(plot_data, parent=self)
                self.children.append(plot)

    def get_available_children(self):
        if len([c for c in self.children if c.node_type in self.PLOT_TYPES]):
            return []
        elif isinstance(self.parent, BasePlotContainer):
            return [
                c for c in self.valid_children() & self.parent.valid_children()
                if not c.is_leaf]
        else:
            return [c for c in self.valid_children() if not c.is_leaf]

    def export_config(self, eval=False, extra_vars=None):
        if eval:
            # Expand the iterator into multiple copies of the inner plot.
            plot_children = [c for c in self.children
                             if c.node_type in self.PLOT_TYPES]
            if not len(plot_children):
                return []
            child_plot = plot_children[0]

            iterable_text = self.get_leaf_with_name('iterable').data
            iter_name, iter_expression = iterable_text.split(' = ', 1)
            iter_name = iter_name.strip()
            iter_expression = iter_expression.strip()
            iterable = common.parse_value(
                iter_expression,
                data_table=self.root_node().get_data_table(),
                extra_vars=extra_vars)
            counter_leaf = self.get_leaf_with_name('counter')
            if counter_leaf is None:
                counter_name = None
            else:
                counter_name = counter_leaf.data

            extra_vars = extra_vars or {}
            config = []
            for i, e in enumerate(iterable):
                inner_vars = copy.deepcopy(extra_vars)
                inner_vars.update({iter_name: e})
                if counter_name:
                    inner_vars.update({counter_name: i})
                child_config = child_plot.export_config(eval, inner_vars)
                if isinstance(child_config, list):
                    # Iterators return a list of plots.
                    config.extend(child_config)
                else:
                    config.append(child_config)
            return config
        else:
            return super().export_config(eval, extra_vars)


class BarContainer(BasePlotContainer):
    icon = SvgIcon.barcontainer
    node_type = 'barcontainer'
    description = ('A Bar Container for horizontal grouping or vertical '
                   'stacking of multiple Bar Plots.')

    cls_tags = frozenset({NodeTags.is_container,
                          NodeTags.deletable,
                          NodeTags.rearrangable,
                          NodeTags.copyable})

    default_data = {'plots': []}

    PLOT_TYPES = {
        'bar': BarPlot,
        'iterator': Iterator,
    }

    NODE_LEAFS = OrderedDict([
        ('bin_labels', {'label': 'Bin Labels',
                        'type': str,
                        'icon': SvgIcon.label,
                        'default': '',
                        'options': None,
                        'description': 'Specify data used as "Labels" plotted '
                                       'on the x-axis name or as a python '
                                       'expression which evaluates to a numpy '
                                       'ndarray',
                        'editor': None}),
        ('grouping', {'label': 'Grouping',
                      'type': 'options',
                      'icon': SvgIcon.bar_grouping,
                      'default': 'grouped',
                      'options': ['grouped', 'stacked'],
                      'description': 'Specify if Bars should be borizontally '
                                     'grouped or vertically stacked.',
                      'editor': tree_widgets.SyComboBox}),
        ('rwidth', {'label': 'Width',
                    'type': float,
                    'icon': SvgIcon.barwidth,
                    'default': 0.8,
                    'options': (0., 1., 0.05),
                    'description': 'Specify the total width used for one '
                                   '"bin".',
                    'editor': tree_widgets.SyDoubleSpinBox}),
        ('color', SY_COLOR_PARAMS),
        ('orientation', SY_BAR_ORIENTATION_PARAMS),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('show', SY_VISIBLE_PARAMS),
    ])

    REQUIRED_LEAFS = {'grouping'}

    @classmethod
    def valid_children(cls):
        return frozenset(
            set(cls.PLOT_TYPES.values()) | {FigureProperty, BarLabelsFont})

    def init(self, data):
        self.add_plots(data)
        self.add_other_nodes(data)

    def add_plots(self, data):
        for plot_data in data.pop('plots', []):
            plot_type = plot_data.get('type')
            if plot_type is not None:
                plot_cls = self.PLOT_TYPES.get(plot_type)
                plot = plot_cls(plot_data, parent=self)
                self.children.append(plot)

    def add_other_nodes(self, data):
        valid_child_nodes = [c for c in self.valid_children()
                             if not c.is_leaf and
                             not issubclass(c, (BasePlot, BasePlotContainer))]
        self.add_children_to_node(data, valid_child_nodes)


class HistogramContainer(BarContainer):
    icon = SvgIcon.histcontainer
    node_type = 'histcontainer'
    description = ('A Histogram Container for vertical stacking '
                   'of multiple Histogram Plots.')

    PLOT_TYPES = {
        'hist': HistogramPlot,
        'iterator': Iterator,
    }

    NODE_LEAFS = OrderedDict([
        ('bin_min_edges', {'label': 'Bin min edges',
                           'type': str,
                           'icon': SvgIcon.bin_min_edge,
                           'default': '',
                           'options': None,
                           'description': 'Specify the column used as '
                                          '"Bin min edges" as a python '
                                          'expression which evaluates to '
                                          'a numpy ndarray',
                           'editor': None}),
        ('bin_max_edges', {'label': 'Bin max edges',
                           'type': str,
                           'icon': SvgIcon.bin_max_edge,
                           'default': '',
                           'options': None,
                           'description': 'Specify the column used as '
                                          '"Bin max edges" as python '
                                          'expression which evaluates to '
                                          'a numpy ndarray',
                           'editor': None}),
        ('color', SY_COLOR_PARAMS),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('edges', {'label': 'Edges between bars',
                   'type': bool,
                   'icon': SvgIcon.histtype,
                   'default': False,
                   'options': None,
                   'description': 'Specify if the Histogram gets plotted '
                                  'as individual bars with visible edges '
                                  'between or as a filled step line plot. '
                                  'This will only have a visible effect if '
                                  'an edge color has been set.',
                   'editor': tree_widgets.SyBoolComboBox}),
        ('show', SY_VISIBLE_PARAMS),
    ])

    REQUIRED_LEAFS = {}

    @classmethod
    def valid_children(cls):
        return frozenset(
            set(cls.PLOT_TYPES.values()) | {FigureProperty, BarLabelsFont})


class Plots(BasePlotContainer):
    node_type = 'plots'
    needs_id = False
    description = 'A container collecting all different Plots for one Axes.'

    cls_tags = frozenset({
        NodeTags.is_container,
        NodeTags.unique})

    PLOT_TYPES = {
        'scatter': ScatterPlot,
        'line': LinePlot,
        'bar': BarPlot,
        'hist': HistogramPlot,
        'heatmap': HeatmapPlot,
        'barcontainer': BarContainer,
        'histcontainer': HistogramContainer,
        'iterator': Iterator,
        'box': BoxPlot,
        'pie': PieChart,
        'annotation': Annotation,
        'timeline': TimelinePlot,
        'image': ImagePlot,
        'lines': Lines,
        'rectangles': Rectangles,
        'ellipses': Ellipses,
    }

    @classmethod
    def valid_children(cls):
        return frozenset(set(cls.PLOT_TYPES.values()) | {FigureProperty})

    def init(self, data):
        self.add_plots(data)

    def export_config(self, eval=False, extra_vars=None):
        """Export configuration for storage."""
        config = []
        for child in self.children:
            child_config = child.export_config(eval, extra_vars)
            if isinstance(child_config, list):
                config.extend(child_config)
            else:
                config.append(child_config)
        return config


class Legend(FigureBaseNode):
    icon = SvgIcon.legend
    node_type = 'legend'
    description = ('The Axes Legend. If defined outside of an Axes, all '
                   'Legends defined in different Axes will be joined into one '
                   'common Legend.')

    cls_tags = frozenset({NodeTags.unique,
                          NodeTags.deletable,
                          NodeTags.rearrangable})

    default_data = {'show': ('True', 'value')}

    NODE_LEAFS = OrderedDict([
        ('show', {'label': 'Visible',
                  'type': bool,
                  'icon': lambda v: create_icon(
                      SvgIcon.visible if v else SvgIcon.invisible),
                  'default': True,
                  'options': None,
                  'description': 'En/Disable if the Legend should be shown.',
                  'editor': tree_widgets.SyBoolComboBox}),
        ('loc', {'label': 'Location',
                 'type': 'options',
                 'icon': SvgIcon.location,
                 'default': 'upper right',
                 'options': list(mpl_utils.LEGEND_LOC.keys())
                            + mpl_utils.OUTSIDE_LEGEND_LOC,
                 'description': ('Specify the location of the Legend. '
                                 'If placing outside Axes you might need '
                                 'to also tweak the "distance" property.'),
                 'editor': tree_widgets.SyComboBox}),
        ('distance', {'label': 'Distance from Axes',
                      'type': float,
                      'icon': SvgIcon.ruler,
                      'default': 4.0,
                      'options': (0.0, None, 0.1),
                      'description': ('When placing the legend outide the '
                                      'plot, use this to specify the '
                                      'distance from the Axes in font-size '
                                      'units. If legend is placed '
                                      'inside the Axes, this property '
                                      'is ignored.'),
                      'editor': tree_widgets.SyDoubleSpinBox}),
        ('ncol', {'label': 'Number of columns',
                  'type': int,
                  'icon': SvgIcon.number_columns,
                  'default': 1,
                  'options': (1, None, 1),
                  'description': ('Specify the number of columns used ot list '
                                  'the artist labels.'),
                  'editor': tree_widgets.SyIntSpinBox}),
        ('fontsize', {'label': 'Font Size',
                      'type': 'options',
                      'icon': SvgIcon.text_size,
                      'default': 'medium',
                      'options': mpl_utils.FONTSIZE,
                      'description': 'Specify the fontsize of the labels',
                      'editor': tree_widgets.SyComboBox}),
        ('frameon', {'label': 'Frame',
                     'type': bool,
                     'icon': SvgIcon.frame,
                     'default': True,
                     'options': None,
                     'description': ('En/Disable the frame drawn around '
                                     'the Legend'),
                     'editor': tree_widgets.SyBoolComboBox}),
        ('title', {'label': 'Title',
                   'type': str,
                   'icon': SvgIcon.label,
                   'default': '',
                   'options': None,
                   'description': 'Specify the title of the Legend.',
                   'editor': tree_widgets.SyLabelEdit}),
    ])

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})


class Grid(FigureBaseNode):
    icon = SvgIcon.grid
    node_type = 'grid'
    description = ('A Grid defines the properties of a the grid lines plotted '
                   'for an Axes.')

    cls_tags = frozenset({NodeTags.unique,
                          NodeTags.deletable,
                          NodeTags.rearrangable})

    default_data = {'show': ('True', 'value')}

    NODE_LEAFS = OrderedDict([
        ('show', {'label': 'Visible',
                  'type': bool,
                  'icon': lambda v: create_icon(
                      SvgIcon.visible if v else SvgIcon.invisible),
                  'default': True,
                  'options': None,
                  'description': 'En/Disable if the Grid should be shown.',
                  'editor': tree_widgets.SyBoolComboBox}),
        ('color', SY_COLOR_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('which', {'label': 'Which',
                   'type': 'options',
                   'icon': SvgIcon.ticks,
                   'default': 'major',
                   'options': ['major', 'minor', 'both'],
                   'description': ('Specify for which ticks the grid lines '
                                   'should be drawn.'),
                   'editor': tree_widgets.SyComboBox}),
        ('axis', {'label': 'Axis',
                  'type': 'options',
                  'icon': SvgIcon.plot,
                  'default': 'both',
                  'options': ['x', 'y', 'both'],
                  'description': ('Specify for which axis (x, y, or both) the '
                                  'grid lines should be drawn.'),
                  'editor': tree_widgets.SyComboBox}),
    ])

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})


class BaseAxis(FigureBaseNode):
    """Definition of an axes dimension."""

    node_type = 'axis'
    description = ('An Axis defines the position, label and limit of an '
                   'x or y Axis.')

    valid_children = frozenset({FigureProperty})
    cls_tags = frozenset({NodeTags.unique})

    NODE_LEAFS = OrderedDict([
        ('position', {'label': 'Axis',
                      'type': 'axesposition',
                      'icon': None,
                      'default': 'bottom',
                      'options': None,
                      'description': 'Specify the position of this Axis.',
                      'editor': tree_widgets.SyComboBox}),
        ('label', SY_LABEL_PARAMS),
        ('major_ticks', SY_MAJOR_TICK_PARAMS),
        ('minor_ticks', SY_MINOR_TICK_PARAMS),
        ('min', {'label': 'Min',
                 'type': float,
                 'icon': SvgIcon.limit,
                 'default': 0.,
                 'options': None,
                 'description': 'Specify the lower limit of this Axis.',
                 'editor': tree_widgets.SyFloatLineEdit}),
        ('max', {'label': 'Max',
                 'type': float,
                 'icon': SvgIcon.limit,
                 'default': 1.,
                 'options': None,
                 'description': 'Specify the upper limit of this Axis.',
                 'editor': tree_widgets.SyFloatLineEdit}),
        ('inverted', {'label': 'Inverted',
                      'type': bool,
                      'icon': SvgIcon.limit,
                      'default': False,
                      'options': None,
                      'description': 'Invert the min and max limits of the axis.',
                      'editor': tree_widgets.SyBoolComboBox}),
        ('scale', {'label': 'Scale',
                   'type': 'options',
                   'icon': SvgIcon.scales,
                   'default': 'linear',
                   'options': ('linear', 'log'),
                   'description': ('Specify the scale (log or linear) of '
                                   'this Axis.'),
                   'editor': tree_widgets.SyComboBox}),
        ('visible', {'label': 'Visible',
                     'type': bool,
                     'icon': SvgIcon.visible,
                     'default': True,
                     'options': None,
                     'description': 'If this axis should be drawn.',
                     'editor': tree_widgets.SyBoolComboBox}),
        ('spinex', {'label': 'Bottom spine position',
                    'type': 'options',
                    'icon': SvgIcon.limit,
                    'default': 'center',
                    'options': ['center', 'default'],
                    'description': (
                        'Positions the bottom spine, valid expressions include'
                        ' ("axes", 0.5) or ("data", 0.5) to lock spine to '
                        'position 0.5 on screen or on the data'),
                    'editor': tree_widgets.SyComboBox}),
        ('spiney', {'label': 'Left spine position',
                    'type': 'options',
                    'icon': SvgIcon.limit,
                    'default': 'center',
                    'options': ['center', 'default'],
                    'description': (
                        'Positions the left spine, valid expressions include '
                        '("axes", 0.5) or ("data", 0.5) to lock spine to '
                        'position 0.5 on screen or on the data'),
                    'editor': tree_widgets.SyComboBox}),
        ('rot_tick_labels', {
            'label': 'Rotate Tick Labels',
            'type': 'options',
            'icon': SvgIcon.rotate,
            'default': 'Horizontal',
            'options': ['Horizontal', 'Vertical', 'Clockwise',
                        'Counter clockwise'],
            'description': 'Choose rotation of the tick '
                           'labels. This is especially '
                           'useful for long labels.',
            'editor': tree_widgets.SyComboBox}),
    ])

    REQUIRED_LEAFS = {'position'}

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})


class XAxis(BaseAxis):
    """Definiton of an x axis."""

    icon = SvgIcon.x_axis
    node_type = 'xaxis'

    NODE_LEAFS = OrderedDict([
        ('position', {'label': 'Position',
                      'type': 'axesposition',
                      'icon': lambda v: create_icon(
                          {'bottom': SvgIcon.x_axis_pos_bottom,
                           'top': SvgIcon.x_axis_pos_top}[v]),
                      'default': 'bottom',
                      'options': ['bottom', 'top'],
                      'description': 'Specify the position of this Axis.',
                      'editor': tree_widgets.SyComboBox}),
        ('label', SY_LABEL_PARAMS),
        ('major_ticks', SY_MAJOR_TICK_PARAMS),
        ('minor_ticks', SY_MINOR_TICK_PARAMS),
        ('min', {'label': 'Min',
                 'type': float,
                 'icon': SvgIcon.limit,
                 'default': 0.,
                 'options': None,
                 'description': 'Specify the lower limit of this Axis.',
                 'editor': tree_widgets.SyFloatLineEdit}),
        ('max', {'label': 'Max',
                 'type': float,
                 'icon': SvgIcon.limit,
                 'default': 1.,
                 'options': None,
                 'description': 'Specify the upper limit of this Axis.',
                 'editor': tree_widgets.SyFloatLineEdit}),
        ('inverted', {'label': 'Inverted',
                      'type': bool,
                      'icon': SvgIcon.limit,
                      'default': False,
                      'options': None,
                      'description': 'Invert the min and max limits of the axis.',
                      'editor': tree_widgets.SyBoolComboBox}),
        ('scale', {'label': 'Scale',
                   'type': 'options',
                   'icon': SvgIcon.scales,
                   'default': 'linear',
                   'options': ('linear', 'log'),
                   'description': ('Specify the scale (log or linear) of '
                                   'this Axis.'),
                   'editor': tree_widgets.SyComboBox}),
        ('visible', {'label': 'Visible',
                     'type': bool,
                     'icon': SvgIcon.visible,
                     'default': True,
                     'options': None,
                     'description': 'If this axis should be drawn.',
                     'editor': tree_widgets.SyBoolComboBox}),
        ('spinex', {'label': 'Bottom spine position',
                    'type': 'options',
                    'icon': SvgIcon.limit,
                    'default': 'center',
                    'options': ['center', 'default', 'zero'],
                    'description': (
                        'Positions the bottom spine, valid expressions '
                        'include ("axes", 0.5) or ("data", 0.5) to lock spine '
                        'to position 0.5 on screen or on the data'),
                    'editor': tree_widgets.SyComboBox}),
        ('rot_tick_labels', {
            'label': 'Rotate Tick Labels',
            'type': 'options',
            'icon': SvgIcon.rotate,
            'default': 'Horizontal',
            'options': ['Horizontal', 'Vertical', 'Clockwise',
                        'Counter clockwise'],
            'description': 'Choose rotation of the tick '
                           'labels. This is especially '
                           'useful for long labels.',
            'editor': tree_widgets.SyComboBox}),
    ])


class YAxis(BaseAxis):
    """Definiton of an x axis."""

    icon = SvgIcon.y_axis
    node_type = 'yaxis'

    NODE_LEAFS = OrderedDict([
        ('position', {'label': 'Position',
                      'type': 'axesposition',
                      'icon': lambda v: create_icon(
                          {'left': SvgIcon.y_axis_pos_left,
                           'right': SvgIcon.y_axis_pos_right}[v]),
                      'default': 'left',
                      'options': ['left', 'right'],
                      'description': 'Specify the position of this Axis.',
                      'editor': tree_widgets.SyComboBox}),
        ('label', SY_LABEL_PARAMS),
        ('major_ticks', SY_MAJOR_TICK_PARAMS),
        ('minor_ticks', SY_MINOR_TICK_PARAMS),
        ('min', {'label': 'Min',
                 'type': float,
                 'icon': SvgIcon.limit,
                 'default': 0.,
                 'options': None,
                 'description': 'Specify the lower limit of this Axis.',
                 'editor': tree_widgets.SyFloatLineEdit}),
        ('max', {'label': 'Max',
                 'type': float,
                 'icon': SvgIcon.limit,
                 'default': 1.,
                 'options': None,
                 'description': 'Specify the upper limit of this Axis.',
                 'editor': tree_widgets.SyFloatLineEdit}),
        ('inverted', {'label': 'Inverted',
                      'type': bool,
                      'icon': SvgIcon.limit,
                      'default': False,
                      'options': None,
                      'description': 'Invert the min and max limits of the axis.',
                      'editor': tree_widgets.SyBoolComboBox}),
        ('scale', {'label': 'Scale',
                   'type': 'options',
                   'icon': SvgIcon.scales,
                   'default': 'linear',
                   'options': ('linear', 'log'),
                   'description': ('Specify the scale (log or linear) of '
                                   'this Axis.'),
                   'editor': tree_widgets.SyComboBox}),
        ('visible', {'label': 'Visible',
                     'type': bool,
                     'icon': SvgIcon.visible,
                     'default': True,
                     'options': None,
                     'description': 'If this axis should be drawn.',
                     'editor': tree_widgets.SyBoolComboBox}),
        ('spiney', {'label': 'Left spine position',
                    'type': 'options',
                    'icon': SvgIcon.limit,
                    'default': 'center',
                    'options': ['center', 'default', 'zero'],
                    'description': (
                        'Positions the left spine, valid expressions include '
                        '("axes", 0.5) or ("data", 0.5) to lock spine to '
                        'position 0.5 on screen or on the data'),
                    'editor': tree_widgets. SyComboBox}),
    ])
