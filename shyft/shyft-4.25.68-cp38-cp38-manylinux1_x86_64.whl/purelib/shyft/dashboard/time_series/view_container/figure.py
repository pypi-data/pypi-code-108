from typing import List, Optional, Dict, Union, Type
import itertools
import logging
# import uuid

import numpy as np
from shyft.time_series import TsVector, UtcPeriod

import bokeh.plotting
import bokeh.models
import bokeh.layouts
from collections import Counter

from shyft.dashboard.base.ports import States, Receiver, connect_state_ports

from shyft.dashboard.time_series.dt_selector import dt_to_str
from shyft.dashboard.time_series.view import FigureView
from shyft.dashboard.time_series.renderer import BaseFigureRenderer, LineRenderer, FillInBetweenRenderer, \
    MultiLineRenderer
from shyft.dashboard.time_series.view_container.view_container_base import BaseViewContainer
from shyft.dashboard.time_series.state import Quantity
from shyft.dashboard.time_series.axes_handler import BokehViewTimeAxis
from shyft.dashboard.time_series.tools.figure_tools import FigureTool, HoverTool
from shyft.dashboard.time_series.axes import YAxis, FigureYAxis, YAxisSide


class FigureError(RuntimeError):
    pass


class Figure(BaseViewContainer):
    """
    Figure class is the view container for a figure

    Examples
    --------
    | # create the viewer app
    | viewer = TsViewer(bokeh_document=doc, title='Test Ts Viewer')
    |
    | # create view container
    | figure = Figure(viewer=viewer)
    |
    | # create a data source
    | data_source = DataSource(ts_adapter=A_time_series_adapter(unit_to_decorate='MW'), unit='MW',
    |                          request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
    |                          time_range=UtcPeriod(start_time, end_time))
    |
    | # create a view in where we put the view container
    | line_view = Line(view_container=figure, color="blue", label="test line", unit="MW")
    |
    | # create a handle for the data source and list of views connected to the data source
    | ds_view_handle = DsViewHandle(data_source=data_source, views=[line_view])
    |
    | # add views and data source to the viewer
    | viewer.add_ds_view_handle(ds_view_handles=[ds_view_handle]
    """

    def __init__(self, *,
                 viewer: 'shyft.dashboard.time_series.ts_viewer.TsViewer',
                 y_axes: Optional[Union[List[YAxis], YAxis]] = None,
                 width: int = 600,
                 height: int = 300,
                 title: Optional[str] = '',
                 tools: Optional[Union[List['FigureTool'], 'FigureTool']] = None,
                 x_axis_formatter: Optional[bokeh.models.DatetimeTickFormatter] = None,
                 min_border_top: int = 0,
                 min_border_left: int = 0,
                 min_border_right: int = 0,
                 min_border_bottom: int = 0,
                 show_grid: bool = True,
                 show_x_axis_label: bool = True,
                 text_font: str = 'monospace',
                 title_text_font_style: str = 'bold',
                 title_text_font_size: int = 10,
                 figure_font_size: int = 10,
                 init_renderers: Optional[Dict[Type[BaseFigureRenderer], int]] = None,
                 logger: Optional['logging.Logger'] = None) -> None:
        """
        Parameters
        ----------
        viewer:
            the TsViewer this figure belongs to
        y_axes:
            additional y-axes for this figure
        width:
            width of the figure in pixels
        height:
            height of the figure in pixels
        title:
            title of the figure
        tools:
            tools connected to this figure
        x_axis_formatter:
            ticker format of the x-axis
        min_border_top:
            the minimum padding in pixels above the central plotting region
        min_border_left:
            the minimum padding in pixels left of the central plotting region
        min_border_right:
            the minimum padding in pixels right of the central plotting region
        min_border_bottom:
            the minimum padding in pixels below the central plotting region
        show_grid:
            switch to turn on/off a grid in the figure
        show_x_axis_label:
            switch to turn on/off label of x-axis
        text_font:
            text font for the figure
        title_text_font_style:
            title text font style (bold, italic, ...)
        title_text_font_size:
            title text font size, in pixels
        figure_font_size:
            font size of axes, in pixels
        init_renderers:
            how many of each renderer type to initialise at start
        """
        self.figure_width = width
        super().__init__(viewer=viewer)
        self.logger = logger or logging.getLogger(f"Figure {title}")

        self.views = []
        self.renderers: Dict[FigureView: BaseFigureRenderer] = {}

        self.idle_renderer = []
        self._glyph_renderers = {}

        self.tools = []
        self.receive_selected_period = Receiver(parent=self, name='receive selected period', signal_type=UtcPeriod,
                                                func=self._receive_set_selected_period)
        self.receive_fontsize = Receiver(parent=self, name='receive fontsize', signal_type=int, func=self._receive_fontsize)

        self.title = title

        if not isinstance(self.view_time_axis, BokehViewTimeAxis):
            raise (RuntimeError(f'Figure {title} is connected to a Viewer with no BokehViewTimeAxis'))

        self.wheel_zoom = bokeh.models.WheelZoomTool(dimensions="width")
        self.bokeh_figure = bokeh.plotting.figure(plot_width=width, plot_height=height, x_axis_type="datetime",
                                                  toolbar_location=None, title=title,
                                                  x_range=self.view_time_axis.shared_x_range, output_backend="webgl",
                                                  tools=[bokeh.models.PanTool(),
                                                         bokeh.models.BoxZoomTool(dimensions="width"), 'xzoom_in',
                                                         'xzoom_out', self.wheel_zoom],
                                                  )
        self.bokeh_figure.toolbar.active_scroll = self.wheel_zoom
        if not show_grid:
            self.bokeh_figure.grid.grid_line_color = None

        # self.axes = axes
        # add x axis format
        tax = bokeh.models.DatetimeTickFormatter()
        tax.microseconds = ['%fus']
        tax.milliseconds = ['%3Nms', '%S.%3Ns']
        tax.seconds = ['%Ss']
        tax.minsec = [':%M:%S']
        tax.minutes = [':%M', '%Mm']
        tax.hourmin = ['%H:%M']
        tax.hours = ['%Hh', '%H:%M']
        tax.days = ['%a-w%V-%g', '%x']  # day-w<isoweek>-<isoyear>
        tax.months = ['%m/%Y', '%b%y']
        tax.years = ['%Y']
        self.bokeh_figure.xaxis.formatter = x_axis_formatter or tax
        if show_x_axis_label:
            self.bokeh_figure.xaxis.axis_label = 'Time'
        self.bokeh_figure.xaxis.axis_label_text_font = text_font
        self.bokeh_figure.xaxis.axis_label_text_font_style = 'normal'

        # set figure text
        self.bokeh_figure.title.text_font = text_font
        self.bokeh_figure.title.text_font_style = title_text_font_style

        # Figure font size:
        self.bokeh_figure.title.text_font_size = f'{int(title_text_font_size)}pt'
        self.bokeh_figure.axis.axis_label_text_font_size = f'{int(figure_font_size)}pt'
        self.bokeh_figure.axis.major_label_text_font_size = f'{int(figure_font_size)}pt'

        # yaxis
        self.y_axes = {}
        self.default_y_axis = YAxis(label='', unit='', color='black', side=YAxisSide.LEFT)
        self.default_y_axis_unit_set = False
        if y_axes:
            if not isinstance(y_axes, list):
                y_axes = [y_axes]
            for i, y_axis in enumerate(y_axes):
                bokeh_axis = None
                if i == 0:
                    bokeh_axis = self.bokeh_figure.yaxis[0]
                fig_axis = FigureYAxis(axis=y_axis, unit_registry=self.unit_registry, bokeh_axis=bokeh_axis, logger=logger)
                fig_axis.bind(parent=self)
                fig_axis.bokeh_axis.axis_label_text_font = text_font
                if i == 0:
                    self.bokeh_figure.y_range = fig_axis.bokeh_range
                else:
                    self.bokeh_figure.extra_y_ranges[fig_axis.uid] = fig_axis.bokeh_range
                    self.bokeh_figure.add_layout(fig_axis.bokeh_axis, place=fig_axis.side)
                self.y_axes[y_axis] = fig_axis
        else:
            fig_axis = FigureYAxis(axis=self.default_y_axis,
                                   unit_registry=self.unit_registry,
                                   bokeh_axis=self.bokeh_figure.yaxis[0],
                                   logger=logger)
            fig_axis.bind(parent=self)
            fig_axis.bokeh_axis.axis_label_text_font = text_font
            self.y_axes[self.default_y_axis] = fig_axis
            self.bokeh_figure.y_range = fig_axis.bokeh_range

        applied_side_counter = Counter([y_axis.side.value for y_axis in self.y_axes])
        axis_left_border = int(50*applied_side_counter['left'])
        axis_right_border = int(50*applied_side_counter['right'])
        # set min, max border
        if title:  # set title border if title available
            min_border_top = max(30, min_border_top)
        self.bokeh_figure.min_border_top = int(min_border_top)
        self.bokeh_figure.min_border_left = int(max(min_border_left, axis_left_border))
        # TODO: add after upgrade bokeh version
        self.bokeh_figure.min_border_right = max(min_border_right, axis_right_border)
        self.bokeh_figure.min_border_bottom = min_border_bottom

        if init_renderers:
            # initialize first fill between such that they are plotted below lines
            if FillInBetweenRenderer in init_renderers:
                self.generate_renderers(renderer_type=FillInBetweenRenderer,
                                        number=init_renderers[FillInBetweenRenderer])
            if LineRenderer in init_renderers:
                self.generate_renderers(renderer_type=LineRenderer,
                                        number=init_renderers[LineRenderer])
            if MultiLineRenderer in init_renderers:
                self.generate_renderers(renderer_type=MultiLineRenderer,
                                        number=init_renderers[MultiLineRenderer])

        if tools:
            if not isinstance(tools, list):
                tools = [tools]
            for tool in tools:
                self.add_tool(tool=tool)

        # connect to dt-selector of viewer if available:
        viewer.connect_to_dt_selector(self.receive_dt)


    # --- LAYOUT
    @property
    def layout(self):
        """
        This property returns the preferred layout of the figure
        """
        return self.bokeh_figure

    @property
    def layout_components(self) -> Dict[str, List]:
        """
        This property returns all layout components of the figure
        """
        return {"widgets": [],
                "figures": [self.bokeh_figure]}

    # --- RENDERERS and VIEWS in bokeh

    def clear(self) -> None:
        """
        This function removes all renderers and views from the figure
        """
        # for bokeh_axis in self.y_axes.values():
        #    bokeh_axis.visible = False
        # self.bokeh_figure.xaxis.visible = False
        self.clear_views()
        self.set_title(title='')

    def add_view(self, *, view: FigureView) -> None:
        """
        This function adds a view to the figure i.e. it will add a corresponding renderer to the figure.
        """
        if view in self.views:
            self.logger.info(
                f"Figure '{self.uid}': not adding view {view} since it is already registered")
            return

        # check if there is an y axis defined with view unit, if not create one
        # auto created axes will be created only by dimensionality
        # print(f"Adding view {view.label}, {view.y_axis} {view.unit}")
        view_y_axis = None
        if self.default_y_axis in self.y_axes and not self.default_y_axis_unit_set:
            # print("add to default axis")
            self.default_y_axis_unit_set = True
            self.default_y_axis.unit = view.unit
            view_y_axis = self.default_y_axis

        # if view has axis definition, check if we know it
        if view_y_axis is None and view.y_axis in self.y_axes:
            # print("add to defined axis")
            view_y_axis = view.y_axis
        # check first if  axis with exact same unit exists, e.g view.unit = m and axis.unit = m
        if view_y_axis is None:
            for y_axis in self.y_axes.keys():
                if self.unit_registry.Unit(view.unit) == self.unit_registry.Unit(y_axis.unit):
                    view_y_axis = y_axis
                    # print("add to exiting axis with same unit")
                    break
        # if not same_unit_y_axis check if axis with same dimensionality exists,
        # eg. view.unit = m and axis.unit = km
        if view_y_axis is None:
            for y_axis in self.y_axes.keys():
                view_dimensionality = self.unit_registry.Unit(view.unit).dimensionality
                axis_dimensionality = self.unit_registry.Unit(y_axis.unit).dimensionality
                if view_dimensionality == axis_dimensionality:
                    view_y_axis = y_axis
                    # print("add to axis with same dimensionality")
                    break
        # check if we can re assign unit on one of the axes we have
        if view_y_axis is None:
            for y_axis in self.y_axes.keys():
                if y_axis.auto_unit_change and not self.has_renderer_on_y_axis(y_axis=y_axis):
                    y_axis.unit = view.unit
                    view_y_axis = y_axis
                    break
        # no axis available so we need to add one with the unit to the figure
        if view_y_axis is None:
            self.logger.info(
                f"Figure '{self.uid}': Dynamically adding axis does not work currently due to bokeh version")
            return
            # TODO: try again add after upgrade bokeh version, not working in 1.0.2
            # add a new axis with this unit
            # applied_side_couter = Counter([y_axis.side.value for y_axis in self.y_axes])
            # side = YAxisSide.LEFT
            # if applied_side_couter['left'] > applied_side_couter['right']:
            #     side = YAxisSide.RIGHT
            # view_y_axis = YAxis(label='', unit=view.unit, color='black', side=side)
            # fig_axis = FigureYAxis(axis=view_y_axis, unit_registry=self.unit_registry)
            # fig_axis.bind(parent=self)
            # self.bokeh_figure.extra_y_ranges[fig_axis.uid] = fig_axis.bokeh_range
            # self.bokeh_figure.add_layout(fig_axis.bokeh_axis, place=fig_axis.side)
            # self.y_axes[view_y_axis] = fig_axis
            # print("created new axis")
        # print(view_y_axis)
        # get ilde renderer
        new_renderer = self.get_idle_renderer(view=view)
        new_renderer.set_view(view=view, y_axis=view_y_axis)
        # if isinstance(new_renderer, FillInBetweenRenderer):
        #    new_renderer.set_bokeh_renderers(bokeh_renderers=self._glyph_renderers[new_renderer])

        # set the visibility of renderer
        for bokeh_renderer in self._glyph_renderers[new_renderer]:
            bokeh_renderer.visible = view.visible
            bokeh_renderer.y_range_name = self.y_axes[view_y_axis].uid

        # save renderer and view
        self.views.append(view)
        self.renderers[view] = new_renderer

        if view.tooltips:
            for tool in self.tools:
                if isinstance(tool, HoverTool):
                    tool.register_view_renderer(view, new_renderer)

    def _receive_fontsize(self, fontsize: int) -> None:
        font_size = f'{int(fontsize)}pt'
        self.bokeh_figure.title.text_font_size = font_size
        self.bokeh_figure.axis.axis_label_text_font_size = font_size
        self.bokeh_figure.axis.major_label_text_font_size = font_size

    def has_renderer_on_y_axis(self, y_axis: YAxis) -> bool:
        """"
        This function checks if figure has at least one renderer with the given y_axis
        """
        for renderer in self.renderers.values():
            if y_axis == renderer.y_axis:
                return True
        return False

    def clear_views(self, *, specific_views: Optional[List[FigureView]] = None) -> None:
        """
        This function removes views from figure and clears the renderer
        """
        if specific_views:
            views = [v for v in specific_views if v in self.views]
            self.views = [v for v in self.views if v not in views]
        else:
            views = [v for v in self.views]
            self.views = []
        for view in views:
            renderer = self.renderers.pop(view)
            renderer.clear_view()
            self.idle_renderer.append(renderer)

        self.update_y_range()

    def update_view_data(self, *, view_data: Dict[FigureView, Quantity[TsVector]]) -> None:
        """
        This port function to update plots if the dt in the widget selection box is triggered
        """
        # dt_cur = 0
        for view, ts_vector in view_data.items():
            if view not in self.renderers:
                continue
            self.renderers[view].update_view_data(ts_vector=ts_vector)
            # dt = self.renderers[view].dt
            # if not dt:
            #     continue
            # dt_cur = max(dt_cur, dt)

        # update title
        # self.update_title(dt_cur)

    # renderer orchestration
    def get_idle_renderer(self, *, view: FigureView) -> BaseFigureRenderer:
        """
        This function returns an idle renderer
        """
        # get ilde renderer for view
        renderer = next(itertools.chain((r for r in self.idle_renderer
                                         if isinstance(r, view.renderer_class)),
                                        [None]))

        # generate new renderer for view
        if not renderer:
            renderer = self.generate_renderers(renderer_type=view.renderer_class, number=1)[0]
        self.idle_renderer.remove(renderer)
        return renderer

    def generate_renderers(self, *, renderer_type: Type[BaseFigureRenderer], number: int = 1) -> List[BaseFigureRenderer]:
        """
        This function generates new renderers and adds them to bokeh
        """
        new_renderers = [renderer_type(unit_registry=self.unit_registry,
                                       notify_figure_y_range_update=self.update_y_range,
                                       logger=self.logger) for _ in range(number)]
        for renderer in new_renderers:
            renderer.bind(parent=self)
            connect_state_ports(self.state_port, renderer.state_port)
            renderer.state_port.receive_state(self._state)
        self.add_renderer_to_bokeh(new_renderers=new_renderers)
        self.idle_renderer.extend(new_renderers)
        return new_renderers

    def add_renderer_to_bokeh(self, *, new_renderers: List[BaseFigureRenderer]) -> None:
        """
        This function adds a new renderer to bokeh figure
        """
        for new_renderer in new_renderers:
            # add patches_category for the new actor
            self._glyph_renderers[new_renderer] = []
            for glyph_ds in new_renderer.glyphs:
                render = self.bokeh_figure.add_glyph(glyph_ds[0], glyph_ds[1])
                self._glyph_renderers[new_renderer].append(render)
                render.visible = True
            new_renderer.set_bokeh_renderers(bokeh_renderers=self._glyph_renderers[new_renderer])

    def remove_renderer_from_bokeh(self, *, renderer) -> None:
        """
        This function removes a renderer from bokeh figure
        """
        if renderer not in self._glyph_renderers:
            return
        bokeh_renderer_list = self._glyph_renderers.pop(renderer)
        for bokeh_renderer in bokeh_renderer_list:
            self.bokeh_figure.renderers.remove(bokeh_renderer)
            for tool in self.tools:
                if isinstance(tool, HoverTool):
                    tool.remove_renderer(renderer)
    # --- FORMAT AND VIEW

    # general canvas functions
    def set_title(self, *, title: str) -> None:
        """
        This function updates the figure meta info
        """
        if title != self.title:
            self.title = title
            self.update_title(None)

    def update_title(self, dt: Optional[int]) -> None:
        """
        This function updates the figure title showing the lowest dt int the figure
        """
        if not dt:
            new_title = self.title
        else:
            new_title = f'dt: {dt_to_str(dt)} - {self.title}'
        self.bokeh_figure.title.text = new_title

    def _receive_dt(self, dt: int) -> None:
        """
        This function is the re-implementation of the dt-receiving function from the base class.
        When receiving a dt we update the title
        """
        self.update_title(dt=dt)

    def draw_figure(self, y_axis: Optional[YAxis] = None) -> None:
        """
        This function triggers redrawing of all renderers in the figure or y axis provided
        """
        if not y_axis:
            renderers = [r for r in self.renderers.values() if r.y_axis == y_axis]
        else:
            renderers = self.renderers.values()
        for renderer in renderers:
            renderer.draw()

    def update_y_range(self) -> None:
        """
        This function updates the figure y-range according to available data
        """
        if self.renderers.values():
            for y_axis_view, bokeh_y_axis in self.y_axes.items():
                view_range = self.view_time_axis.view_range
                vals = np.array([r.y_range(view_range) for r in self.renderers.values() if r.visible and
                                 r.y_axis == y_axis_view])
                if len(vals) == 0 or np.isnan(vals).all():
                    bokeh_y_axis.reset_y_range()
                    continue
                bokeh_y_axis.set_y_range(start=float(np.nanmin(vals.T[0, :])), end=float(np.nanmax(vals.T[1, :])))

    def next_new_data_update_y_range(self) -> None:
        """
        This function triggers data update for all renderes for the next new data
        """
        for renderer in self.renderers.values():
            if not renderer.visible:
                continue
            renderer.next_new_data_update_y_range = True

    # --- EXTERNAL CONTROL/ TOOLS

    def add_tool(self, tool: FigureTool) -> None:
        """
        This function adds a FigureTool to the figure
        """
        if not isinstance(tool, FigureTool):
            raise FigureError(f'Figure {self.title}: tool {tool} not of type FigureTool')
        if tool not in self.tools:
            tool.bind(parent=self)
            self.tools.append(tool)
            connect_state_ports(self.state_port, tool.state_port)

    def _receive_set_selected_period(self, signal: UtcPeriod):
        """
        This function sets the view range of the axis
        """
        self.view_time_axis.set_view_range(view_range=signal)
        self.view_time_axis.evaluate_view_range()

    # --- STATE

    def _receive_state(self, state: States) -> None:
        """
        This function sets the state of the figure
        """
        if state == self._state:
            return
        self._state = state
        if state == States.LOADING:
            color = "#fcf9ef"
            self.bokeh_figure.border_fill_color = color
            self.bokeh_figure.background_fill_color = color
            if self.title:
                self.bokeh_figure.title.text = ' '.join([self.title, 'LOADING DATA ...'])
            self._state = States.ACTIVE
            self.state_port.send_state(state)
        elif state == States.READY:
            self.bokeh_figure.border_fill_color = 'white'
            self.bokeh_figure.background_fill_color = 'white'
            self._state = States.ACTIVE
            self.state_port.send_state(state)
        elif state == States.ACTIVE:
            self.state_port.send_state(state)
            self.bokeh_figure.border_fill_color = 'white'
            self.bokeh_figure.background_fill_color = 'white'
        elif state == States.DEACTIVE:
            color = "#fcf9ef"
            self.state_port.send_state(state)
            self.bokeh_figure.border_fill_color = color
            self.bokeh_figure.background_fill_color = color
