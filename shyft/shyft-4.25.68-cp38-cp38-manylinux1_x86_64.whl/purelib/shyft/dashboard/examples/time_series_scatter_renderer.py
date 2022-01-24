import itertools

from bokeh.models import ResetTool
from typing import Optional, Dict, Any
import numpy as np

import bokeh
from bokeh.layouts import row, column
from shyft.time_series import UtcPeriod, Calendar
from shyft.dashboard.time_series.ds_view_handle import DsViewHandle
from shyft.dashboard.examples.test_data_generator import ExampleTsAdapterSine
from shyft.dashboard.time_series.renderer import DiamondScatterRenderer, TriangleScatterRenderer, CircleScatterRenderer, \
    SquareScatterRenderer
from shyft.dashboard.time_series.sources.source import DataSource
from shyft.dashboard.time_series.tools.figure_tools import ResetYRange
from shyft.dashboard.time_series.tools.ts_viewer_tools import ResetTool
from shyft.dashboard.time_series.ts_viewer import TsViewer
from shyft.dashboard.time_series.view import DiamondScatter, LegendItem, Scatter
from shyft.dashboard.time_series.view_container.figure import Figure
from shyft.dashboard.time_series.view_container.legend import Legend
from shyft.dashboard.time_series.axes_handler import DsViewTimeAxisType
from shyft.dashboard.time_series.state import State
from shyft.dashboard.widgets.logger_box import LoggerBox
from shyft.dashboard.time_series.axes import YAxis, YAxisSide

from shyft.dashboard.base.app import AppBase


class TsScatterViewerExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]] = None):
        super().__init__(thread_pool=thread_pool)
        self.logger = None  # app_kwargs['logger']

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "scatter_renderer"

    def get_layout(self, doc: bokeh.document.Document, logger: Optional[LoggerBox] = None) -> bokeh.layouts.LayoutDOM:
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name

        reset_tool = ResetTool(logger=logger)
        # figure tools
        reset_y_range_tool = ResetYRange(logger=logger)

        # PRE RUNTIME
        figure_width = 800

        # Create our viewer app
        viewer = TsViewer(bokeh_document=doc, unit_registry=State.unit_registry,
                          time_step_restrictions=[Calendar.HOUR*3, Calendar.DAY, Calendar.WEEK],
                          thread_pool_executor=self.thread_pool, logger=logger, tools=[reset_tool])

        # set up additional y-axes
        ax1_fig1 = YAxis(label="left nonsens axes", unit='MW', side=YAxisSide.LEFT)
        # create first figure with all additional y-axes
        fig1 = Figure(viewer=viewer,
                      width=figure_width,
                      y_axes=[ax1_fig1],
                      logger=logger,
                      tools=[reset_y_range_tool])

        # create a legend container
        legend = Legend(viewer=viewer, title='One to control them all')

        # Initialise a data source
        time_range = UtcPeriod(-3600*24*100, 3600*24*100)
        data_source = DataSource(ts_adapter=ExampleTsAdapterSine(unit_to_decorate='MW', time_range=time_range,
                                                                 async_on=True),
                                 unit='MW', request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                 time_range=time_range)

        # create scatter view can be used either directly with the view class
        diamond_scatter = DiamondScatter(color='blue', unit='MW', label='test adapter line', visible=True,
                                         view_container=fig1, index=1,
                                         y_axis=ax1_fig1, size=20)

        # or the Scatter view can be used by providing the renderer_class
        # available are CircleScatterRenderer, DiamondScatterRenderer, TriangleScatterRenderer
        diamond_scatter2 = Scatter(color='red', unit='MW', label='test adapter line', visible=True,
                                   view_container=fig1, index=2,
                                   y_axis=ax1_fig1, size=10, renderer_class=SquareScatterRenderer)

        # create the legend items
        # create legend item for line_view and fill_in_between_view
        legend_item_fig1 = LegendItem(view_container=legend, label='Original DsViewHandle Fig1',
                                      views=[diamond_scatter])

        # Connecting the views and a data source through a DsViewHandle
        ds_view_handle = DsViewHandle(data_source=data_source, views=[diamond_scatter,
                                                                      legend_item_fig1,
                                                                      diamond_scatter2])

        # Adding the ds_view_handle to the app
        viewer.add_ds_view_handles(ds_view_handles=[ds_view_handle])

        # add some buttons and selectors to test the callbacks

        # size callback

        change_size = bokeh.models.widgets.Button(label='Random scatter size')

        def change_size_function():
            new_size = np.random.randint(1, 20)
            while diamond_scatter.size == new_size:
                new_size = np.random.randint(1, 20)
            diamond_scatter.size = new_size

        change_size.on_click(change_size_function)

        # color callback
        change_color = bokeh.models.widgets.Button(label='Change scatter color')

        colors = itertools.cycle(bokeh.palettes.Colorblind8)

        def change_color_function():
            diamond_scatter.color = next(colors)

        change_color.on_click(change_color_function)

        # color callback
        change_fill_color = bokeh.models.widgets.Button(label='Change scatter fill color')

        fill_colors = itertools.cycle(bokeh.palettes.Colorblind8)

        def change_color_function():
            diamond_scatter.fill_color = next(fill_colors)

        change_fill_color.on_click(change_color_function)

        # fill alpha
        change_fill_alpha = bokeh.models.widgets.Button(label='Random scatter fill alpha')

        def change_fill_alpha_function():
            new = abs(np.random.randn(1)[0])
            while diamond_scatter.fill_alpha == new:
                new = abs(np.random.randn(1)[0])
            diamond_scatter.fill_alpha = new

        change_fill_alpha.on_click(change_fill_alpha_function)

        # fill alpha
        change_line_alpha = bokeh.models.widgets.Button(label='Random scatter line alpha')

        def change_line_alpha_function():
            new = abs(np.random.randn(1)[0])
            while diamond_scatter.line_alpha == new:
                new = abs(np.random.randn(1)[0])
            diamond_scatter.line_alpha = new

        change_line_alpha.on_click(change_line_alpha_function)

        layout = column(row(viewer.layout, reset_tool.layout, reset_y_range_tool.layout, height=80),
                        row(fig1.layout, legend.layout),
                        row(bokeh.models.widgets.Div(text='Some Buttons to test the on change callbacks')),
                        row(change_size, change_color, change_fill_color),
                        row(change_fill_alpha, change_line_alpha))

        return layout
