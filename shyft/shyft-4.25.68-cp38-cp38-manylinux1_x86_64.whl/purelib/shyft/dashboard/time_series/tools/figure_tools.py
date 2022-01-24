import abc
from enum import Enum
from typing import Tuple, Any, Optional, List, Dict
# from collections import OrderedDict
from sys import maxsize

from bokeh.models import ColumnDataSource, Quad, RadioButtonGroup, Button, PreText, CustomJS, Rect, HoverTool
from bokeh.models.widgets.buttons import Toggle, Dropdown
from bokeh.layouts import row, column
from bokeh.events import Pan, PanStart, PanEnd
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models.widgets.markups import Div

import shyft.time_series as sa
import numpy as np

from shyft.dashboard.time_series.view import FigureView
from shyft.dashboard.widgets.sliders import RangeSliderSelect, RangeSliderData

from shyft.dashboard.base import constants
from shyft.dashboard.base.selector_views import RadioGroup
from shyft.dashboard.base.selector_presenter import SelectorPresenter
from shyft.dashboard.time_series.renderer import LineRenderer, BaseFigureRenderer
from shyft.dashboard.widgets.selector_models import LabelData
from shyft.dashboard.time_series.data_utility import find_nearest, merge_convert_ts_vectors_to_numpy
from shyft.dashboard.time_series.tools.view_time_axis_tools import ViewTimeAxisTool
from shyft.dashboard.base.app import LayoutComponents, Widget
from shyft.dashboard.base.ports import Sender, Receiver, connect_ports
from shyft.dashboard.widgets.selector_models import LabelDataSelector
from shyft.dashboard.base.ports import States
import bokeh.plotting

from shyft.dashboard.time_series.tools.base import BaseTool
from shyft.dashboard.time_series.formatter import basic_time_formatter


class FigureToolError(RuntimeError):
    pass


class FigureTool(BaseTool):
    """
    This object represents the base class of all figure tools
    """

    def __init__(self, logger=None):
        """
        Parameters
        ----------
        logger:
            optional logger
        """
        super().__init__(logger=logger)

    @abc.abstractmethod
    def on_bind(self, *, parent: Any):
        pass


class ResetYRange(FigureTool):
    """
    Tool to reset the y-range of a figure to the default view
    """

    def __init__(self,
                 width: int = 120,
                 height: int = 30,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger=None):
        """
        Parameters
        ----------
        logger:
            optional logger
        """
        super().__init__(logger=logger)

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        self.reset_y_range_button = Button(label='Reset y-range', width=width, height=height)
        self.reset_y_range_button.on_click(self.on_click)

        self.layout = column(self.reset_y_range_button, width=width + padding, height=height, sizing_mode=sizing_mode)

    def on_bind(self, *, parent: Any) -> None:
        pass

    def on_click(self) -> None:
        if self._state == States.DEACTIVE:
            return
        for parent in self.parents:
            parent.update_y_range()

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.reset_y_range_button], 'figures': []}


class ActiveScroll(Enum):
    X_axis = 1
    Y_axis = 2


class WheelZoomDirection(FigureTool, Widget):
    """
    Tool to change the direction of zooming when scrolling the mouse wheel between x and y direction
    """

    def __init__(self,
                 height: int = 30,
                 width: int = 140,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger=None):
        """
        Parameters
        ----------
        logger:
            optional logger
        """
        FigureTool.__init__(self, logger=logger)
        Widget.__init__(self, logger=logger)

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        self.bokeh_figures = []
        self.wheel_zooms = []
        self.scroll_button = RadioButtonGroup(labels=['x-scroll', 'y-scroll'], width=width, height=height, active=0)
        self.scroll_button.on_change('active', self.change_active_scroll)
        self.set_scroll_button_active = self.update_value_factory(self.scroll_button, 'active')
        self._layout = column(self.scroll_button, width=width + padding, height=height, sizing_mode=sizing_mode)

    @property
    def layout(self) -> bokeh.models.LayoutDOM:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.scroll_button], 'figures': []}

    def on_bind(self, *, parent: Any):
        if parent.bokeh_figure in self.bokeh_figures:
            raise FigureToolError(f'bokeh figure {parent.bokeh_figure} is already bound to {self} tool')

        if parent.wheel_zoom in self.wheel_zooms:
            raise FigureToolError(f'wheel zoom {parent.wheel_zoom} is already bound to {self} tool')

        self.bokeh_figures.append(parent.bokeh_figure)
        self.wheel_zooms.append(parent.wheel_zoom)

    def set_active_scroll(self, active_scroll: ActiveScroll):
        if active_scroll == ActiveScroll.X_axis:
            for wz in self.wheel_zooms:
                wz.dimensions = 'width'
        elif active_scroll == ActiveScroll.Y_axis:
            for wz in self.wheel_zooms:
                wz.dimensions = 'height'
        else:
            for bf in self.bokeh_figures:
                bf.toolbar.active_scroll = None

    def change_active_scroll(self, attr: str, old: int, new: int) -> None:
        if self._state == States.DEACTIVE:
            self.set_scroll_button_active(old)
            return
        if not self.scroll_button.disabled:
            if self.scroll_button.active == 0:  # 'x_scroll'
                self.set_active_scroll(ActiveScroll.X_axis)
            elif self.scroll_button.active == 1:  # 'y_scroll'
                self.set_active_scroll(ActiveScroll.Y_axis)
        else:
            self.set_scroll_button_active(None)


class ExportLineDataButton(FigureTool, Widget):
    """
    Tool to download all data shown in all figures where this tool is attached to!

    Two obstacles:
    - each obj/renderer in a figure has its own data source with own amount of time, value tuples
    - js callbacks and python callbacks in bokeh are not sync

    Therefore:
    - for each renderer one separate csv file is downloaded
    - we create a bokeh PreText obj in addition to the download button, to which we attach a js callback for the download
    after the download the callback is removed again
    """

    def __init__(self,
                 label: str = 'Download Figure Data',
                 height: int = 50,
                 width: int = 150,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger=None):
        """
        Parameters
        ----------
        logger:
            optional logger
        """
        FigureTool.__init__(self, logger=logger)
        Widget.__init__(self, logger=logger)

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        self.download_button = Button(label=label, width=width, height=height)
        self.download_button.on_click(self.on_click)
        self.download_text = PreText(text="")

        self._layout = column(self.download_text, self.download_button, width=width + padding, height=height,
                              sizing_mode=sizing_mode)

    def on_bind(self, *, parent: Any) -> None:
        pass

    def on_click(self) -> None:
        for parent in self.parents:
            # create the data content
            sources = []
            names = []
            for renderer in parent.renderers.values():
                if not isinstance(renderer, LineRenderer):
                    continue
                sources.append(renderer.bokeh_data_source)
                # name: replace all white_spaces with underscore while removing multiple underscores
                if parent.title:
                    name = f"{parent.title}-{renderer.view.label} unit: {renderer.view.unit}"
                else:
                    name = f"{renderer.view.label} unit-{renderer.view.unit}"
                # replacing some bad characters of the unit
                name = '_'.join(
                    name.replace('_', ' ').replace('/', 'per').replace('**', 'p').replace('*', '').strip().split())
                names.append(name)
            # add js callback
            self.download_text.js_on_change("text", self.js_callback(sources=sources,
                                                                     names=names))
            # trigger js callback
            self.download_text.text = 'downloading'
            # remove js callback
            for k, v in self.download_text.js_property_callbacks.items():
                if 'text' in k:
                    self.download_text.js_property_callbacks[k] = []
            # reset download text
            self.download_text.text = ''

    @staticmethod
    def js_callback(*, sources: List[ColumnDataSource], names: List[str]) -> str:
        """Creates js to download all data from multiple data sources to multiple csv files"""
        java_script = """
        function table_to_csv(source) {
            const columns = Object.keys(source.data)
            const nrows = source.get_length()
            const lines = [columns.join(',')]

            for (let i = 0; i < nrows; i++) {
                let multi = false;
                let nrows_multi = 0;
                for (let j = 0; j < columns.length; j++) {
                    const column = columns[j]
                    if (Array.isArray(source.data[column][i])) {
                        multi = true
                        nrows_multi = source.data[column][i].length
                        break
                    }
                }
                if (multi) {
                    for (let k = 0; k < nrows_multi; k++) {
                        let row = []
                        for (let j = 0; j < columns.length; j++) {
                            const column = columns[j]
                            let data = source.data[column][i]
                            if (Array.isArray(data) || typeof(data) === 'object'){
                                row.push(data[k].toString())
                            }
                            else {
                                row.push(data.toString())
                            }                            
                        }
                        lines.push(row.join(','))    
                    }
                } else {
                    let row = [];
                    for (let j = 0; j < columns.length; j++) {
                        const column = columns[j]
                        row.push(source.data[column][i].toString())
                    }
                    lines.push(row.join(','))
                }
            }
            return lines.join('\\n').concat('\\n')
        }


        for (var i = 0; i < sources.length; i++){

            var source = sources[i]
            var name = names[i]
            
            try {
                const filename = `data-${name}.csv`
                var filetext = table_to_csv(source)
                const blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' })
            
                const link = document.createElement('a')
                link.href = URL.createObjectURL(blob)
                link.download = filename
                link.target = '_blank'
                link.style.visibility = 'hidden'
                link.dispatchEvent(new MouseEvent('click'))
                } catch (error) {
                    console.error(error)
                }
        }
"""
        return CustomJS(args=dict(sources=sources, names=names), code=java_script)

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.download_text, self.download_button], 'figures': []}

    @property
    def layout(self) -> bokeh.models.LayoutDOM:
        return self._layout


class HoverToolToggleDropdown:
    """
        Tool to toggle the information shown by tooltips.
        The three modes are:
        - info and data
        - data
        - no tooltip
        Info and data should be provided as the default tooltip-mode in the supplied hover tools.
    """
    def __init__(self, hover_tools: List[HoverTool]):
        """
        Args:
            hover_tools: hover tools which are to interact with toggle dropdown.
        """
        self._original_hover_tools = hover_tools
        self._extract_real_hover_tools()
        self._hover_tooltips = {}
        self._tooltip_modes = {}
        self._hovertool_info_selector = Dropdown(label='Hover tool', width=100,
                                                 menu=[('Info and data', 'default'),
                                                       ('Data only', 'data'),
                                                       ('None', 'none')])

        self._hovertool_info_selector.on_click(self.callback_hovertool_info)
        self._setup_hover_tools(self._extract_real_hover_tools())

        self.layout = column(self._hovertool_info_selector)

    def _extract_real_hover_tools(self):
        real_hover_tools = [tool.get_all_hover_tools() for tool in self._original_hover_tools]
        # Flatten list of all hover tools.
        return [tool for hover_tools in real_hover_tools for tool in hover_tools]

    def callback_hovertool_info(self, event):
        # New renderers with tooltips may have been added since last interaction.
        all_hover_tools = self._extract_real_hover_tools()

        self._setup_hover_tools(all_hover_tools)
        for tool in all_hover_tools:
            tool.tooltips = self._hover_tooltips[tool][event.item]

    def _setup_hover_tools(self, all_hover_tools):
        for hover_tool in all_hover_tools:
            if hover_tool not in self._hover_tooltips:
                self._hover_tooltips[hover_tool] = self._create_tooltips_modes(hover_tool)

    def _create_tooltips_modes(self, hover_tool):
        data_only_tooltips = [("", value) for _, value in (hover_tool.tooltips or [])]
        tooltips_modes = {'default': hover_tool.tooltips, 'data': data_only_tooltips, 'none': None}
        self._tooltip_modes[hover_tool] = tooltips_modes

        return tooltips_modes


class HoverTool(FigureTool):
    """
    Tool to display the label, x, and y values of a glyph contained in a figure
    """
    def __init__(self, *,
                 point_policy: str = 'snap_to_data',
                 tooltips: List[Tuple[str, str]] = None,
                 formatters: Dict[str, str] = None,
                 show_arrow: bool = False,
                 mode: str = 'mouse',
                 logger=None):
        """

        Args:
            point_policy: 'snap_to_data' or 'follow_mouse'
            tooltips: a list of tooltips where each row contains a label, and its associated value
            formatters: how the tooltips will be formatted: available formatters: "printf", "datetime", and "numeral"
            show_arrow: to show the arrow
            mode: if 'mouse', then only when the mouse is directly over the glyph, 
                  if 'vline' and 'hline': whenever the vertical or horizontal line from the mouse position 
                  intersects the glyph
            logger: the logger
        """
        super().__init__(logger=logger)
        self.bokeh_figure = None
        self.hover_tools = {}
        self.point_policy = point_policy
        self.tooltips = tooltips
        self.formatters = formatters
        self.show_arrow = show_arrow
        self.mode = mode

    def on_bind(self, *, parent: Any):
        self.bokeh_figure = parent.bokeh_figure
        for renderer in parent.idle_renderer:
            self._setup_hover_tool(renderer)

    def register_view_renderer(self, view: FigureView, renderer: BaseFigureRenderer):
        if renderer not in self.hover_tools:
            self._setup_hover_tool(renderer)

        if not self.tooltips:
            self.hover_tools[renderer].tooltips = view.tooltips

    def remove_renderer(self, renderer: BaseFigureRenderer) -> None:
        self.hover_tools.pop(renderer, None)

    def get_all_hover_tools(self):
        return [tools for _, tools in self.hover_tools.items()]

    def _setup_hover_tool(self, renderer):
        hover = bokeh.models.HoverTool(renderers=renderer.get_bokeh_renderers(), show_arrow=self.show_arrow, 
                                       point_policy=self.point_policy, tooltips=self.tooltips,
                                       formatters=self.formatters, mode=self.mode)
        self.bokeh_figure.add_tools(hover)
        self.hover_tools[renderer] = hover


class TimePeriodSelectorInFigure(FigureTool, Widget):
    """
    Tool to select a specific time period visually in the view container
    """

    def __init__(self, time_zone='Europe/Oslo', logger=None):
        """
        All x parameters are in the shyft native coordinates, i.e in epoch time seconds

        Parameters
        ----------
        time_zone:
            time zone to use for period calculations
        logger:
            optional logger
        """
        super().__init__(logger=logger)
        self.cal = sa.Calendar(time_zone)
        self.bokeh_figure = None
        # center x of our selector tool box
        self.left_x = int(sa.utctime_now())
        self.right_x = int(sa.utctime_now() + self.cal.YEAR)
        self.min_width = int(self.cal.HOUR)

        self.pan_start_x = 0
        self.pan_start_left_x = 0
        self.pan_start_right_x = 0

        self.expand_scale_default = 0.20
        self.expand_scale = self.expand_scale_default
        self.top = 10
        self.bottom = 0

        self.snap_to = False
        self.snap_to_dt = None
        self.fixed_dt = False

        self.action = Actions.freeze

        self.bokeh_figure = None
        self.parent_figure_tools = None
        self.parent_figure_subscribed_events = []
        self.active_scroll_tool = None

        # edit toggle button
        self.edit_button = Toggle(label='Edit Time period')
        self.edit_button.on_click(self.manipulate_period)
        self.set_edit_button = self.update_value_factory(self.edit_button, 'active')

        # fixed dt period checkbox
        self.mode = Modes.free_range
        self.mode_view = RadioGroup(width=100)
        self.mode_pres = SelectorPresenter(name='fixed dt pres', view=self.mode_view)
        self.mode_model = LabelDataSelector(presenter=self.mode_pres)
        self.mode_model.receive_labels([Modes.fixed_dt, Modes.snap_to_dt, Modes.free_range])

        # view selection
        self.period_div = Div(text=self.period_to_str())

        # data source
        self.basic_color = '#b3de69'
        self.selected_color = '#e3863a'
        left, right, bottom, top = self.calculate_coordinates(y_axis=True)
        self.patch_coordinates = dict(left=left * 1000, right=right * 1000, bottom=bottom, top=top,
                                      colors=[self.basic_color, self.basic_color, self.basic_color])
        self.source = ColumnDataSource(data=self.patch_coordinates)
        self.visible = False
        self.quad = Quad(left="left", right="right", top="top", bottom="bottom", fill_color="colors", fill_alpha=0.2,
                         line_alpha=0.2, line_color='#67a9f0')
        self.quad_renderer = None  # inside bokeh bokeh_figure

        self.deactivated = False

        self.receive_visibility = Receiver(parent=self, name='receive selector visibility', signal_type=bool,
                                           func=self._receive_visibility)
        self.receive_dt = Receiver(parent=self, name='receive dt to snap to', signal_type=int,
                                   func=self._receive_snap_to_dt)
        self.receive_mode = Receiver(parent=self, name='receive mode of operation', signal_type=LabelData,
                                     func=self._receive_mode)
        self.send_time_period = Sender(parent=self, name='Send selected time period', signal_type=sa.UtcPeriod)
        self.receive_manipulate_period = Receiver(parent=self, name='receive edit time period button state',
                                                  signal_type=bool, func=self.manipulate_period)

        connect_ports(self.mode_model.send_selected_labels, self.receive_mode)
        self.mode_model.presenter.set_selector_value(self.mode)

        self._layout = row(column(self.edit_button, self.period_div), column(self.mode_view.layout))

    @property
    def layout(self) -> bokeh.models.LayoutDOM:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        lc = self.mode_view.layout_components
        lc['widgets'].extend([self.edit_button, self.period_div])
        return lc

    def _receive_visibility(self, visibility: bool) -> None:
        self.visible = visibility
        if self.quad_renderer:
            self.quad_renderer.visible = self.visible

    def _receive_snap_to_dt(self, dt: int) -> None:
        self.snap_to_dt = int(np.ceil(float(dt)))
        if self.snap_to or self.fixed_dt:
            self.min_width = self.snap_to_dt
        self.update_plot()

    def _receive_mode(self, labels: LabelData) -> None:
        mode = labels[0]
        if mode == Modes.fixed_dt and self.snap_to_dt is not None:
            self.fixed_dt = True
            self.snap_to = True
            self.expand_scale = 0
            self.min_width = self.snap_to_dt
            self.mode = mode
        elif mode == Modes.snap_to_dt and self.snap_to_dt is not None:
            self.snap_to = True
            self.fixed_dt = False
            self.expand_scale = self.expand_scale_default
            self.min_width = self.snap_to_dt
            self.mode = mode
        else:
            self.snap_to = False
            self.fixed_dt = False
            self.expand_scale = self.expand_scale_default
            self.min_width = int(self.cal.HOUR)
            self.mode = Modes.free_range
            self.mode_pres.set_selector_value(self.mode, callback=False)
        self.update_plot()

    def period_to_str(self) -> str:
        start = self.cal.to_string(self.left_x).replace('T', '  ').replace('Z', '')
        end = self.cal.to_string(self.right_x).replace('T', '  ').replace('Z', '')
        return f"""From: <b>{start}</b></br>Until:  <b>{end}</b>"""

    def on_bind(self, *, parent: Any) -> None:
        figure = parent.bokeh_figure
        if self.bokeh_figure is not None:
            raise FigureToolError(f"A TimePeriodSelector already added to bokeh_figure {self.bokeh_figure}! ")
        if not isinstance(figure.xaxis[0].formatter, DatetimeTickFormatter):
            raise FigureToolError(f"TimePeriodSelector provided bokeh_figure@s xasis is not a time-axis, use "
                                  "DatetimeTickFormatter!")
        self.bokeh_figure = figure
        self.parent_figure_tools = [t for t in self.bokeh_figure.toolbar.tools]
        self.quad_renderer = self.bokeh_figure.add_glyph(self.source, self.quad)
        self.bokeh_figure.on_event(PanStart, self.pan_start_event_callback)
        self.bokeh_figure.on_event(Pan, self.pan_event_callback)
        self.bokeh_figure.on_event(PanEnd, self.pan_end_event_callback)
        self.bokeh_figure.y_range.on_change('start', self.update_on_change_y_range)
        self.bokeh_figure.y_range.on_change('end', self.update_on_change_y_range)
        self.quad_renderer.visible = self.visible
        self.deactivated = True
        # connect to dt selector
        parent.parent.connect_to_dt_selector(self.receive_dt)

    def manipulate_period(self, clicked: bool) -> None:
        if self._state == States.DEACTIVE:
            self.set_edit_button(not clicked)
            return
        if not self.quad_renderer:
            self.set_edit_button(not clicked)
            return
        if clicked:
            self.deactivated = False
            self.parent_figure_tools = [t for t in self.bokeh_figure.toolbar.tools]
            self.active_scroll_tool = self.bokeh_figure.toolbar.active_scroll
            self.bokeh_figure.toolbar.active_scroll = None
            self.bokeh_figure.toolbar.tools = []
            if not self.bokeh_figure.x_range.start/1000 <= self.left_x <= self.bokeh_figure.x_range.end / 1000:
                self.left_x = int((self.bokeh_figure.x_range.start + self.bokeh_figure.x_range.end) / 1000. / 2.)
                self.right_x = self.left_x + int((self.bokeh_figure.x_range.end -
                                                  self.bokeh_figure.x_range.start) / 1000. / 4.)

            self.set_time_period_restrictions()

            self.bottom = self.bokeh_figure.y_range.start
            self.top = self.bokeh_figure.y_range.end
            self.update_plot(y_axis=True)
            self.visible = True
            self.quad_renderer.visible = self.visible
        else:
            self.bokeh_figure.add_tools(*self.parent_figure_tools)
            self.bokeh_figure.toolbar.active_scroll = self.active_scroll_tool

            self.deactivated = True
            self.visible = False
            self.quad_renderer.visible = self.visible
        self.set_edit_button(clicked)

    def pan_start_event_callback(self, event: bokeh.events.PanStart) -> None:
        if self.deactivated:
            return
        self.pan_start_x = int(event.x / 1000.)
        self.pan_start_left_x = self.left_x
        self.pan_start_right_x = self.right_x

        left, right, bottom, top = self.calculate_coordinates()
        if self.mode == Modes.fixed_dt or right[0] < self.pan_start_x < left[2]:  # middle quad block
            self.action = Actions.move
            patches = {'colors': [(slice(3), [self.basic_color, self.selected_color, self.basic_color])]}
            self.source.patch(patches=patches)
        elif self.pan_start_x <= right[0]:  # left[0] <=
            self.action = Actions.extend_left
            patches = {'colors': [(slice(3), [self.selected_color, self.basic_color, self.basic_color])]}
            self.source.patch(patches=patches)
        elif left[2] <= self.pan_start_x:  # <= right[2]
            self.action = Actions.extend_right
            patches = {'colors': [(slice(3), [self.basic_color, self.basic_color, self.selected_color])]}
            self.source.patch(patches=patches)
        else:
            self.action = Actions.freeze
            patches = {'colors': [(slice(3), [self.basic_color, self.basic_color, self.basic_color])]}
            self.source.patch(patches=patches)

    def pan_event_callback(self, event: bokeh.events.Pan) -> None:
        if self.deactivated:
            return
        if self.action == Actions.freeze:
            return
        current_x = int(event.x / 1000.)
        dx = current_x - self.pan_start_x
        if self.action == Actions.move:
            self.left_x = self.pan_start_left_x + dx
            self.right_x = self.pan_start_right_x + dx

        elif self.action == Actions.extend_right:
            new_right = self.pan_start_right_x + dx
            if new_right - self.left_x < self.min_width:
                return
            self.right_x = new_right

        elif self.action == Actions.extend_left:
            new_left = self.pan_start_left_x + dx
            if self.right_x - new_left < 0:
                return
            self.left_x = new_left

        self.update_plot()

    def set_time_period_restrictions(self) -> None:
        if self.snap_to or self.fixed_dt and self.snap_to_dt is not None:
            self.left_x = float(self.cal.trim(self.left_x, self.snap_to_dt))
            if not self.fixed_dt:
                new_right = int(self.cal.trim(self.right_x, self.snap_to_dt))
                if new_right - self.left_x < self.snap_to_dt:
                    new_right = self.cal.trim(self.right_x + self.snap_to_dt // 2, self.snap_to_dt)
                self.right_x = int(new_right)
            else:
                self.right_x = float(self.cal.trim(self.left_x + self.snap_to_dt + self.snap_to_dt // 2, self.snap_to_dt))

    def calculate_coordinates(self, *, y_axis: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        # Snap to time grid here!
        self.set_time_period_restrictions()

        expand_width = (self.right_x - self.left_x) * self.expand_scale
        left = np.array([self.left_x, self.left_x, self.right_x - expand_width])
        right = np.array([self.left_x + expand_width, self.right_x, self.right_x])

        if y_axis:
            bottom = np.ones(3) * self.bottom
            top = np.ones(3) * self.top
        else:
            bottom = None
            top = None
        return left, right, bottom, top

    def update_plot(self, *, y_axis=False) -> None:
        left, right, bottom, top = self.calculate_coordinates(y_axis=y_axis)
        patches = {'right': [(slice(3), right * 1000.)], 'left': [(slice(3), left * 1000.)]}
        if y_axis:
            patches['bottom'] = [(slice(3), bottom)]
            patches['top'] = [(slice(3), top)]
        self.source.patch(patches=patches)
        self.period_div.text = self.period_to_str()

    def pan_end_event_callback(self, event: bokeh.events.PanEnd) -> None:
        if self.deactivated:
            return
        patches = {'colors': [(slice(3), [self.basic_color, self.basic_color, self.basic_color])]}
        self.source.patch(patches=patches)
        # snap to grid those as well
        left, right, bottom, top = self.calculate_coordinates()
        time_period = sa.UtcPeriod(int(left[1]), int(right[1]))
        self.send_time_period(time_period)

    def update_on_change_y_range(self, attr, old, new) -> None:
        if not self.visible:
            return
        if attr == 'start':
            self.bottom = new
            self.update_plot(y_axis=True)
        elif attr == 'end':
            self.top = new
            self.update_plot(y_axis=True)

    def _receive_state(self, state: States) -> None:
        """
        State port function on receiving state, can be overwritten by inherited class
        """
        if self._state == state:
            return
        if state == States.ACTIVE:
            self.bottom = self.bokeh_figure.y_range.start
            self.top = self.bokeh_figure.y_range.end
            self.update_plot(y_axis=True)
            self._state = state
            self.state_port.send_state(self._state)
        elif state == States.DEACTIVE:
            self._state = state
            self.state_port.send_state(self._state)


class ShowTsLabel(FigureTool, Widget):
    """
    Hover tool to display the label of a time series.
    """

    def __init__(self,
                 label: str = 'show label',
                 height: int = 30,
                 width: int = 140,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger=None):
        """
        Parameters
        ----------
        label: the label
        height: the height
        width: the width
        padding: optional padding
        sizing_mode: optional sizing mode
        logger: optional logger
        """
        FigureTool.__init__(self, logger=logger)
        Widget.__init__(self, logger=logger)

        self.bokeh_figures = []
        self.hover_tool = []

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        self.show_label_button = Button(label=label, width=width, height=height)
        self.show_label_button.on_click(self.on_click)
        # self.set_show_label_button_active = self.update_value_factory(self.show_label_button, 'active')

        self._layout = column(self.show_label_button, width=width + padding, height=height,
                              sizing_mode=sizing_mode)

    @property
    def layout(self) -> bokeh.models.LayoutDOM:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.show_label_button], 'figures': []}

    def on_bind(self, *, parent: Any) -> None:
        if parent.bokeh_figure in self.bokeh_figures:
            raise FigureToolError(f'bokeh figure {parent.bokeh_figure} is already bound to {self} tool')

        if parent.hover_tool in self.hover_tool:
            raise FigureToolError(f'wheel zoom {parent.hover_tool} is already bound to {self} tool')

        self.bokeh_figures.append(parent.bokeh_figure)
        self.hover_tool.append(parent.hover_tool)

        # figure = parent.bokeh_figure
        # if self.bokeh_figure is not None:
        #    raise FigureToolError(f"A Hoover tool already added to bokeh_figure {self.bokeh_figure}! ")
        # self.bokeh_figure = figure
        # self.parent_figure_tools = [t for t in self.bokeh_figure.toolbar.tools]
        # self.hover_tool = HoverTool()
        # figure.hover.tooltips = [("index", "@index"), ("label", "@label")]
        # self.hover_tool.renderers = [bokeh.models.renderers.Renderer]
        # figure.hover=self.hover_tool

    def on_click(self) -> None:
        if self._state == States.DEACTIVE:
            return
        for parent in self.parents:
            # parent.show_hover()
            pass


class Actions(Enum):
    freeze = 0
    move = 1
    extend_right = 2
    extend_left = 3


class Modes:
    fixed_dt = 'Fixed dt'
    snap_to_dt = 'Snap to dt'
    free_range = 'Free range'



class TimePeriodSelectorSlider(FigureTool, Widget):
    """
    Tool to reset the y-range of a figure to the default view
    """

    def __init__(self,
                 slider_width: int,
                 width: int = 120,
                 height: int = 120,
                 time_zone='Europe/Oslo',
                 color: str = '#b3de69',
                 title="Select time period selector",
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 layout_margin: Tuple[int, int, int, int] = None,
                 logger=None):
        """
        Parameters
        ----------
        logger:
            optional logger
        """
        super().__init__(logger=logger)

        self.cal = sa.Calendar()  # time_zone

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        self.activate_button = Toggle(label='Activate', width=width, height=40)
        self.activate_button.on_click(self.on_click)
        self.set_activate_button = self.update_value_factory(self.activate_button, 'active')

        x = int(sa.utctime_now()*1000)
        width = 100*1000
        self.x_start = x - width
        self.x_end = x + width
        self.selection_start = None
        self.selection_end = None

        self.bokeh_figure = None
        self.title = title

        kwargs = {'show_value': False, 'tooltips': False}
        self.range_slider_view = RangeSliderSelect(width=int(slider_width),
                                                   height=50,
                                                   title=title,
                                                   value=(self.x_start, self.x_end),
                                                   start=self.x_start,
                                                   step=1,
                                                   end=self.x_end,
                                                   **kwargs)

        self.patch_coordinates = dict(x_center=[x], x_width=[width])
        self.source = ColumnDataSource(data=self.patch_coordinates)
        self.visible = False
        self.area = Rect(x='x_center',
                         y=0,
                         width='x_width',
                         height=maxsize,
                         fill_alpha=0.25,
                         fill_color=color,
                         line_alpha=0.2,
                         line_color='#67a9f0'
                         )
        self.area_renderer = None  # inside bokeh bokeh_figure

        self.receive_range = Receiver(parent=self,
                                      name='receive range to highlight',
                                      signal_type=Tuple[float, float],
                                      func=self.update_selected_area)

        self.send_time_period = Sender(parent=self,
                                       name='send utc period of selected values',
                                       signal_type=sa.UtcPeriod)

        connect_ports(self.range_slider_view.send_slider_value, self.receive_range)

        self._layout = row(self.range_slider_view.layout,
                           self.activate_button,
                           width=slider_width + width + padding,
                           height=40 + padding,
                           sizing_mode=sizing_mode)
        self._layout.margin = layout_margin or (0, 0, 0, 50)

    def on_bind(self, *, parent: Any) -> None:

        self.bokeh_figure = parent.bokeh_figure

        self.x_start = self.bokeh_figure.x_range.start
        self.x_end = self.bokeh_figure.x_range.end
        x_center = (self.x_start + self.x_end)/2
        range = ((self.x_start + x_center)/2, (self.x_end + x_center)/2)

        self.range_slider_view.receive_param(RangeSliderData(start=self.x_start,
                                                             end=self.x_end,
                                                             step=1,
                                                             range=range,
                                                             callback=False))

        self.area_renderer = self.bokeh_figure.add_glyph(self.source, self.area)
        parent.view_time_axis.on_change_view_range(self, self._update_range)

        self.area_renderer.visible = self.visible

        self.update_selected_area((self.selection_start, self.selection_end))
        self.range_slider_view.state_port.receive_state(States.DEACTIVE)

    def on_click(self, clicked) -> None:
        if self._state == States.DEACTIVE:
            return
        if not self.area_renderer:
            self.set_activate_button(not clicked)
            return
        if clicked:
            self.range_slider_view.state_port.receive_state(States.ACTIVE)
            if self.selection_start is None or self.selection_end is None:
                x_center = (self.x_start + self.x_end)/2
                self.selection_start = (self.x_start + x_center)/2
                self.selection_end = (self.x_end + x_center)/2
                self.range_slider_view.set_slider_value((self.selection_start, self.selection_end))

            self.visible = True
            self.range_slider_view.slider.start = self.x_start
            self.range_slider_view.slider.end = self.x_end
            self.update_selected_area((self.selection_start, self.selection_end))
        else:
            self.visible = False
            self.send_time_period(sa.UtcPeriod(0, 0))
            self.range_slider_view.state_port.receive_state(States.DEACTIVE)
            self.update_title()
        self.area_renderer.visible = self.visible

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.range_slider_view.layout_components['widgets'],
                            self.activate_button], 'figures': []}

    @property
    def layout(self):
        return self._layout

    def update_selected_area(self, range: Tuple[float, float]):
        self.selection_start = range[0]
        self.selection_end = range[1]
        if self.visible:
            x_center = (self.selection_start + self.selection_end)/2
            x_width = self.selection_end - self.selection_start
            self.source.data = dict(x_center=[x_center], x_width=[x_width])
            self.send_time_period(sa.UtcPeriod(self.selection_start/1000., self.selection_end/1000.))
        self.update_title()

    def _update_range(self):
        self.x_start = self.bokeh_figure.x_range.start
        self.x_end = self.bokeh_figure.x_range.end
        if self.visible:
            self.range_slider_view.slider.start = self.x_start
            self.range_slider_view.slider.end = self.x_end

    def update_title(self) -> str:
        if self.visible:
            start = self.cal.to_string(int(self.selection_start/1000.)).replace('T', '  ').replace('Z', '')
            end = self.cal.to_string(int(self.selection_end/1000.)).replace('T', '  ').replace('Z', '')
            self.range_slider_view.slider.title = f"""{self.title}: {start} -> {end}"""
        else:
            self.range_slider_view.slider.title = f"""{self.title}"""

    @property
    def layout(self):
        return self._layout


class TimeIntervalSelectorSlider(FigureTool, Widget):
    """
    Range slider used to select an interval along the time-axis in a given figure
    """

    def __init__(self,
                 width: int,
                 title: str = "Time period",
                 time_zone: str = 'Europe/Oslo',
                 color: str = '#b3de69',
                 sizing_mode: Optional[str] = None,
                 show_value: bool = False,
                 tooltips: bool = False,
                 layout_margin: Tuple[int, int, int, int] = None,
                 logger=None):
        """
        Parameters
        ----------
        width: width of the slider
        title: slider title
        time_zone: time zone to use for period calculations, default: 'Europe/Oslo'
        color: color of the box (selected area)
        sizing_mode:  the mode used for the items of slider to resize to fill the available space
        show_value: show the the value of slider along the title
        tooltips: slider tooltips
        layout_margin: margin
        logger: optional logger
        """
        super().__init__(logger=logger)
        self.title = title
        self.time_zone = time_zone
        sizing_mode = sizing_mode or constants.sizing_mode

        self.bokeh_figure = None
        self.area_renderer = None  # area inside bokeh bokeh_figure
        self.visible = False

        self.cal = sa.Calendar(self.time_zone)  # Shyft calendar
        self.mill_sec = 1000.  # conversion parameter from bokeh time step (milli seconds) to Shyft time step (seconds)

        # Activate toggle button
        self.activate_button = Toggle(label='Activate', width=100)
        self.activate_button.on_click(self.on_click)
        self.set_activate_button = self.update_value_factory(self.activate_button, 'active')

        # Rest toggle button
        self.reset_button = Toggle(label='Reset', width=100)
        self.reset_button.on_click(self.reset_on_click)
        self.set_reset_button = self.update_value_factory(self.reset_button, 'active')

        # RangeSliderSelect
        x = int(sa.utctime_now() * 1000)
        slider_width = width    # slider width
        self.x_start = x - slider_width  # start value for the slider
        self.x_end = x + slider_width    # end value for the slider
        self.selection_start = None      # left value of range slider
        self.selection_end = None        # left value of selected range
        self.slider_range = None         # right value of selected range
        self.step = int(self.cal.WEEK)   # step size for the slider

        self.range_slider_view = RangeSliderSelect(width=int(slider_width),
                                                   height=50,
                                                   title=title,
                                                   value=(int(self.x_start), int(self.x_end)),
                                                   start=int(self.x_start),
                                                   step=self.step,
                                                   end=int(self.x_end),
                                                   show_value=show_value, tooltips=tooltips)

        # Rectangle - selected area in figure
        self.patch_coordinates = dict(x_center=[x], x_width=[width], label=[''])
        self.source = ColumnDataSource(data=self.patch_coordinates)
        self.area = Rect(x='x_center', y=0, width='x_width', height=maxsize, fill_alpha=0.25, fill_color=color,
                         line_alpha=0.2, line_color='#67a9f0')

        # Receivers, senders, and port connections
        self.receive_range = Receiver(parent=self, name='receive range to highlight', signal_type=Tuple[float, float],
                                      func=self.update_selected_area)
        self.send_time_period = Sender(parent=self, name='send utc period of selected values', signal_type=sa.UtcPeriod)
        self.receive_dt = Receiver(parent=self, name='receive dt to snap to', signal_type=int, func=self._receive_dt)
        self.receive_manipulate_period = Receiver(parent=self, name='receive edit time period button state',
                                                  signal_type=bool, func=self.on_click)
        self.receive_manipulate_reset = Receiver(parent=self, name='receive reset time period button state',
                                                 signal_type=bool, func=self.reset_on_click)
        connect_ports(self.range_slider_view.send_slider_value, self.receive_range)

        # Layout
        self._layout = column(self.range_slider_view.layout,
                              row(self.activate_button, self.reset_button, height=30),
                              width=width,
                              sizing_mode=sizing_mode)

        self._layout.margin = layout_margin or (0, 0, 0, 45)

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.range_slider_view.layout_components['widgets'],
                            self.activate_button, self.reset_button], 'figures': []}

    @property
    def layout(self):
        return self._layout

    def on_bind(self, *, parent: Any) -> None:
        self.bokeh_figure = parent.bokeh_figure

        self.x_start = self.bokeh_figure.x_range.start
        self.x_end = self.bokeh_figure.x_range.end
        x_center = (self.x_start + self.x_end) / 2
        selected_slider_range = ((self.x_start + x_center) / 2, (self.x_end + x_center) / 2)

        self.range_slider_view.receive_param(RangeSliderData(start=self.x_start,
                                                             end=self.x_end,
                                                             step=self.step,
                                                             range=selected_slider_range,
                                                             callback=False))

        self.area_renderer = self.bokeh_figure.add_glyph(self.source, self.area)
        parent.view_time_axis.on_change_view_range(self, self._update_range)

        self.area_renderer.visible = self.visible

        self.update_selected_area((self.selection_start, self.selection_end))
        self.range_slider_view.state_port.receive_state(States.DEACTIVE)

        parent.parent.connect_to_dt_selector(self.receive_dt)

    def on_click(self, clicked: bool) -> None:
        if self._state == States.DEACTIVE:
            self.set_activate_button(not clicked)
            return
        if not self.area_renderer:
            self.set_activate_button(not clicked)
            return
        if clicked:
            self.range_slider_view.state_port.receive_state(States.ACTIVE)
            if self.selection_start is None or self.selection_end is None:
                x_center = (self.x_start + self.x_end) / 2
                self.selection_start = (self.x_start + x_center) / 2
                self.selection_end = (self.x_end + x_center) / 2
                self.set_time_period_restrictions()
                self.range_slider_view.set_slider_value((self.selection_start, self.selection_end))

            self.visible = True
            self.range_slider_view.slider.start = self.x_start
            self.range_slider_view.slider.end = self.x_end
            self.range_slider_view.slider.step = 1# self.step
            self.update_selected_area((self.selection_start, self.selection_end))
        else:
            self.visible = False
            self.send_time_period(sa.UtcPeriod(0, 0))
            self.range_slider_view.state_port.receive_state(States.DEACTIVE)
            self.update_title()
        self.area_renderer.visible = self.visible

    def reset_on_click(self, clicked: bool) -> None:
        if clicked:
            self.set_reset_button(clicked)
            x_center = (self.x_start + self.x_end) / 2
            self.selection_start = (self.x_start + x_center) / 2
            self.selection_end = (self.x_end + x_center) / 2
            self.set_time_period_restrictions()
            self.range_slider_view.set_slider_value((self.selection_start, self.selection_end))

            self.range_slider_view.slider.start = self.x_start
            self.range_slider_view.slider.end = self.x_end
            self.range_slider_view.slider.step = self.step
            self.update_selected_area((self.selection_start, self.selection_end))
        self.set_reset_button(not clicked)

    def _receive_dt(self, dt: int) -> None:
        self.step = int(np.ceil(float(dt) * self.mill_sec))
        # self.range_slider_view.slider.step = self.step
        if self.visible:
            self.x_start = self.bokeh_figure.x_range.start
            self.x_end = self.bokeh_figure.x_range.end
            self.set_time_period_restrictions()
            self.range_slider_view.slider.start = self.x_start
            self.range_slider_view.slider.end = self.x_end
            self.range_slider_view.set_slider_value((self.selection_start, self.selection_end))
            self.update_selected_area((self.selection_start, self.selection_end))

    def update_slider(self):
        x_center = (self.x_start + self.x_end) / 2
        self.selection_start = int((self.x_start + x_center) / 2 / self.mill_sec)
        self.selection_end = int((self.x_end + x_center) / 2 / self.mill_sec)
        self.set_time_period_restrictions()
        slider_range = (self.selection_start, self.selection_end)
        self.range_slider_view.set_slider_value((self.selection_start, self.selection_end))
        self.range_slider_view.receive_param(RangeSliderData(start=int(self.x_start),
                                                             end=int(self.x_end),
                                                             step=self.step,
                                                             range=slider_range,
                                                             callback=False))

    def set_slider_range_restrictions(self) -> None:
        self.x_start /= self.mill_sec
        self.x_end /= self.mill_sec
        self.step /= self.mill_sec

        self.x_start = float(self.cal.trim(self.x_start, self.step))
        new_end = int(self.cal.trim(self.x_end, self.step))
        if new_end - self.x_end < self.step:
            new_end = self.cal.trim(self.x_end + self.step // 2, self.step)
        self.x_end = int(new_end)

        self.x_start *= self.mill_sec
        self.x_end *= self.mill_sec
        self.step *= self.mill_sec

    def set_time_period_restrictions(self) -> None:
        self.step /= self.mill_sec
        self.selection_start /= self.mill_sec
        self.selection_end /= self.mill_sec

        self.selection_start = float(self.cal.trim(self.selection_start, self.step))
        new_end = int(self.cal.trim(self.selection_end, self.step))
        if new_end - self.selection_end < self.step:
            new_end = self.cal.trim(self.selection_end + self.step // 2, self.step)
        self.selection_end = int(new_end)

        self.step *= self.mill_sec
        self.selection_start *= self.mill_sec
        self.selection_end *= self.mill_sec

    def update_selected_area(self, selected_area: Tuple[float, float]):
        if self.visible:
            self.selection_start = selected_area[0]
            self.selection_end = selected_area[1]
            self.set_time_period_restrictions()
            x_center = (self.selection_start+self.selection_end)/2
            x_width = self.selection_end-self.selection_start
            self.source.data = dict(x_center=[x_center], x_width=[x_width], label=['Selected time period'])
            self.send_time_period(sa.UtcPeriod(self.selection_start/self.mill_sec, self.selection_end/self.mill_sec))
            self.update_title()

    def _update_range(self):
        self.x_start = self.bokeh_figure.x_range.start
        self.x_end = self.bokeh_figure.x_range.end
        # self.set_slider_range_restrictions()
        if self.visible:
            self.range_slider_view.slider.start = self.x_start
            self.range_slider_view.slider.end = self.x_end
            self.set_time_period_restrictions()
            slider_range = (self.selection_start, self.selection_end)

            self.range_slider_view.receive_param(RangeSliderData(start=int(self.x_start),
                                                                 end=int(self.x_end),
                                                                 step=self.step,
                                                                 range=slider_range,
                                                                 callback=False))
            self.update_selected_area(slider_range)

    def update_title(self) -> str:
        if self.visible:
            start = basic_time_formatter([self.selection_start / self.mill_sec], self.time_zone or None)[0]
            end = basic_time_formatter([self.selection_end / self.mill_sec], self.time_zone or None)[0]
            self.range_slider_view.slider.title = f"""{self.title}: {start} -> {end}"""
        else:
            self.range_slider_view.slider.title = f"""{self.title}"""
