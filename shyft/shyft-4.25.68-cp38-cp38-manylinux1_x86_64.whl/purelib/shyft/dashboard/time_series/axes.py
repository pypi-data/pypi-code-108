from enum import Enum
from typing import Optional, Tuple
from pint.errors import UndefinedUnitError
import logging

import bokeh.models

from shyft.dashboard.base.app import update_value_factory
from shyft.dashboard.time_series.state import Unit, UnitRegistry
from shyft.dashboard.base.hashable import Hashable
from shyft.dashboard.time_series.bindable import Bindable
from shyft.dashboard.time_series.attr_callback_manager import AttributeCallbackManager


class YAxisError(RuntimeError):
    pass


class YAxisSide(Enum):
    LEFT = 'left'
    RIGHT = 'right'


class YAxis(Hashable, Bindable, AttributeCallbackManager):
    """
    This object represents the y axis definition
    """
    def __init__(self, *,
                 label: str,
                 unit: Unit,
                 color: str='black',
                 side: YAxisSide=YAxisSide.LEFT,
                 default_y_range: Optional[Tuple[float, float]]=None,
                 dynamic_unit_prefix: bool=False,
                 auto_unit_change: bool=True) -> None:
        """
        Representation of a y-axis for a figure.

        Parameters
        ----------
        label: y axis lable
        unit: unit of the axis
        color: color of the axis incl. tixs and numbers
        side: YAxisSide either YAxisSide.LEFT or YAxisSide.RIGHT
        default_y_range: set the default range to use if no renderer on axis
        dynamic_unit_prefix: NOT IN USE, used dynamic axis scaling
        auto_unit_change: allow that the figure changes the axis units if the axis is empty
        """
        AttributeCallbackManager.__init__(self)
        Hashable.__init__(self)
        Bindable.__init__(self)

        self.label = label
        self.unit = unit
        self.color = color
        self.y_range_pad = 0.1
        self.auto_unit_change = auto_unit_change

        self.__dynamic_unit_prefix = False  # dynamic_unit_prefix
        self.__default_y_range = default_y_range or (0, 1)
        self.__side = side

    @property
    def side(self) -> YAxisSide:
        return self.__side

    @property
    def default_y_range(self) -> Tuple[float, float]:
        return self.__default_y_range

    @property
    def dynamic_unit_prefix(self) -> bool:
        return self.__dynamic_unit_prefix

    def __repr__(self) -> str:
        return f"YAxis(label='{self.label}', unit='{self.unit}', color='{self.color}', side={self.side})"


class FigureYAxis(Bindable):
    """
    This Object represents actual y axis for a Figure class
    """
    def __init__(self, *,
                 axis: YAxis,
                 unit_registry: UnitRegistry,
                 bokeh_axis: Optional[bokeh.models.LinearAxis]=None,
                 y_axis_format: Optional[str]=None,
                 logger: Optional['logging.Logger']=None) -> None:
        """
        Figure Y Axis for the figure view container

        Parameters
        ----------
        axis: YAxis object which to represent
        unit_registry: unit registry to use for unit converison
        bokeh_axis: bokeh axis to use
        """
        Bindable.__init__(self)
        if axis.bound:
            raise YAxisError(f"{axis} is already bound to {axis.parent}")

        try:
            unit_registry.Unit(axis.unit)
        except UndefinedUnitError as u:
            raise YAxisError(f"{axis}: Incompatible unit!: {u}")

        axis.bind(parent=self)
        self.logger = logger or logging.getLogger()
        self.axis_view = axis
        self.unit_registry = unit_registry

        self.bokeh_range = bokeh.models.Range1d(axis.default_y_range[0], axis.default_y_range[1])
        self.bokeh_range.on_change('end', self.check_axis_dimensions)
        self.bokeh_range.on_change('start', self.check_axis_dimensions)
        self.set_bokeh_range_start = update_value_factory(self.bokeh_range, 'start')
        self.set_bokeh_range_end = update_value_factory(self.bokeh_range, 'end')

        self.is_default_axis = False
        if bokeh_axis:
            self.bokeh_axis = bokeh_axis
            self.is_default_axis = True
        else:
            self.bokeh_axis = bokeh.models.LinearAxis()
            self.bokeh_axis.y_range_name = str(self.uid)
        self.bokeh_axis.axis_label_text_font = 'monospace'
        self.bokeh_axis.axis_label_text_font_style = 'normal'
        f = self.axis_format(self.unit_registry.Unit(self.axis_view.unit))
        self.bokeh_axis.formatter = bokeh.models.NumeralTickFormatter(rounding='nearest',
                                                                      language='en',
                                                                      format=f)

        self.axis_view.on_change(obj=self, attr='label', callback=self.label_callback)
        self.axis_view.on_change(obj=self, attr='unit', callback=self.unit_callback)
        self.axis_view.on_change(obj=self, attr='color', callback=self.color_callback)

        # init the axis
        self.label_callback(self.axis_view, 'label', '', self.axis_view.label)
        self.unit_callback(self.axis_view, 'unit', '', self.axis_view.unit)
        self.color_callback(self.axis_view, 'color', '', self.axis_view.color)

    def label_callback(self, obj, attr, old_value, new_value) -> None:
        """
        Sets the label for the bokeh Axis
        """
        if attr != 'label':
            return
        if obj != self.axis_view:
            obj.remove_all_callbacks(self)
            return
        self.bokeh_axis.axis_label = ' '.join([new_value,
                                               self.unit_view_format(self.unit_registry.Unit(self.axis_view.unit))])

    def unit_callback(self, obj, attr, old_value, new_value) -> None:
        """
        Sets the color for the bokeh axis
        """
        if attr != 'unit':
            return
        if obj != self.axis_view:
            obj.remove_all_callbacks(self)
            return
        try:
            self.unit_registry.Unit(new_value)
        except UndefinedUnitError as u:
            self.logger.error(f"{self.axis_view}: Incompatible unit!: {u}")

        if self.parent and self.parent.has_renderer_on_y_axis(self.axis_view):
            view_dimensionality = self.unit_registry.Unit(old_value).dimensionality
            axis_dimensionality = self.unit_registry.Unit(new_value).dimensionality
            if view_dimensionality != axis_dimensionality:
                raise YAxisError(f"{self.axis_view}: Cannot change unit!: to {new_value} Since Renderer with different unit are "
                             f"defined on this axis!")
        self.bokeh_axis.axis_label = ' '.join([self.axis_view.label,
                                               self.unit_view_format(self.unit_registry.Unit(new_value))])
        self.bokeh_axis.formatter.format = self.axis_format(self.unit_registry.Unit(new_value))

    def color_callback(self, obj, attr, old_value, new_value) -> None:
        """
        This function sets the color for the bokeh axis
        """
        if attr != 'color':
            return
        if obj != self.axis_view:
            obj.remove_all_callbacks(self)
            return
        self.bokeh_axis.axis_line_color = new_value
        self.bokeh_axis.major_label_text_color = new_value
        self.bokeh_axis.axis_label_text_color = new_value
        self.bokeh_axis.major_tick_line_color = new_value
        self.bokeh_axis.minor_tick_line_color = new_value

    @staticmethod
    def axis_format(unit: Unit) -> str:
        """
        This functions sets the y axis number format
        """
        if str(unit) == 'percent':
            return '0.[00]'
        else:
            return '0.[000]'

    @staticmethod
    def unit_view_format(unit: Unit) -> str:
        """
        This function converts the Unit of the y axis
        """
        return '%' if str(unit) == 'percent' else f'{unit:~P}'

    @property
    def uid(self) -> str:
        """
        This function returns the uid of the axis_view, used to identify this axis
        """
        if self.is_default_axis:
            return 'default'
        return str(self.axis_view.uid)

    @property
    def side(self) -> str:
        """
        This function returns the side of the axis
        """
        if self.is_default_axis:
            return YAxisSide.LEFT.value
        return self.axis_view.side.value

    def set_y_range(self, start: float, end: float) -> None:
        """
        This function sets the axis range to start and end
        """
        #self.bokeh_axis.visible = True
        if abs(end) < 1.e-4 and abs(start) < 1.e-4:
            end = 1
            start = -1
        if self.axis_view.dynamic_unit_prefix:
            start, end, axis_unit = self.get_dynamic_axis_unit(start, end)
            self.axis_view.unit = axis_unit
        extra_pad = (end - start)*self.axis_view.y_range_pad
        self.set_bokeh_range_start(start - extra_pad)
        self.set_bokeh_range_end(end + extra_pad)
        #self.bokeh_range.start = start - extra_pad
        #self.bokeh_range.end = end + extra_pad

    def check_axis_dimensions(self, attr, old, new) -> None:
        """
        This function checks if y range has changed enough order of magnitude to trigger unit change
        """
        if self.axis_view.dynamic_unit_prefix:
            start, end, unit = self.get_dynamic_axis_unit(self.bokeh_range.start, self.bokeh_range.end)
            if unit != self.unit_registry.Unit(self.axis_view.unit):
                self.set_bokeh_range_start(start)
                self.set_bokeh_range_end(end)
                self.axis_view.unit = unit
                # TODO: is not updating the graph correctly
                self.parent.draw_figure(y_axis=self.axis_view)

    def get_dynamic_axis_unit(self, start: float, end: float) -> Tuple[float, float, str]:
        """
        This function checks if the order of magnitude of the axis should change and returns the changes
        """
        # TODO check if unit gets outside pints unit prefix definitions > yotta, < yocto
        axis_length = abs(start) + abs(end)
        axis_unit = (self.unit_registry.Unit(self.axis_view.unit) * axis_length).to_compact().u
        start = (start*self.unit_registry.Unit(self.axis_view.unit)).to(axis_unit).magnitude
        end = (end*self.unit_registry.Unit(self.axis_view.unit)).to(axis_unit).magnitude
        return start, end, str(axis_unit)

    def reset_y_range(self) -> None:
        """
        This function resets the y range to the default y range defined by YAxis
        """
        self.set_bokeh_range_start(self.axis_view.default_y_range[0])
        self.set_bokeh_range_end(self.axis_view.default_y_range[1])
        #self.bokeh_range.start = self.axis_view.default_y_range[0]
        #self.bokeh_range.end = self.axis_view.default_y_range[1]
        #self.bokeh_axis.visible = False
