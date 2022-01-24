from calendar import Calendar
from typing import Optional, Dict, Any
from bokeh.layouts import column, row
import bokeh.models
import bokeh.plotting
from bokeh.models import MultiLine

import shyft.time_series as sa
from shyft.dashboard.base.ports import connect_ports
from shyft.dashboard.time_series.axes import YAxis, YAxisSide
from shyft.dashboard.time_series.axes_handler import DsViewTimeAxisType
from shyft.dashboard.time_series.ds_view_handle import DsViewHandle
from shyft.dashboard.time_series.sources.source import DataSource
from shyft.dashboard.time_series.state import State

from shyft.dashboard.time_series.tools.figure_tools import TimePeriodSelectorInFigure, WheelZoomDirection, ResetYRange
from shyft.dashboard.base.app import AppBase
from shyft.dashboard.time_series.tools.ts_viewer_tools import ResetTool
from shyft.dashboard.time_series.tools.view_time_axis_tools import ViewPeriodSelector
from shyft.dashboard.time_series.view import Line, FillInBetween, LegendItem, MultiLine
from shyft.dashboard.time_series.view_container.legend import Legend
from shyft.time_series import UtcPeriod, Calendar

from shyft.dashboard.time_series.view_container.figure import Figure
from shyft.dashboard.time_series.ts_viewer import TsViewer
from shyft.dashboard.widgets.logger_box import LoggerBox
from shyft.dashboard.time_series.tools.figure_tools import HoverTool
from shyft.dashboard.examples.time_series_viewer import DsViewHandleGenerator, ExampleTsAdapterSine


class HoverToolExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "hover tool example"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name
        # PRE RUNTIME
        figure_width = 800
        # Initializing different tools for the app
        # ts viewer tools
        reset_tool = ResetTool(logger=logger)
        # figure tools
        reset_y_range_tool = ResetYRange(logger=logger)
        wheel_zoom = WheelZoomDirection(logger=logger)
        hover = HoverTool(logger=logger, tooltips=[("t", "$t")])
        # view time axis tools
        view_period_selector = ViewPeriodSelector(logger=logger)

        # Create our viewer app
        viewer = TsViewer(bokeh_document=doc, unit_registry=State.unit_registry,
                          tools=[reset_tool, view_period_selector],
                          time_step_restrictions=[Calendar.HOUR * 3, Calendar.DAY, Calendar.WEEK], logger=logger)

        # Create view containers

        # set up additional y-axes
        ax1_fig1 = YAxis(label="left nonsens axes", unit='MW', side=YAxisSide.LEFT)
        ax2_fig1 = YAxis(label="right nonsens axes", unit='GW', side=YAxisSide.RIGHT, color='green')
        ax3_fig1 = YAxis(label="right nonsens axes 2", unit='m', side=YAxisSide.RIGHT, color='magenta')
        # create first figure with all additional y-axes
        fig1 = Figure(viewer=viewer, tools=[reset_y_range_tool, wheel_zoom, hover],
                      width=figure_width,
                      y_axes=[ax1_fig1, ax2_fig1, ax3_fig1], init_renderers={FillInBetween: 20, MultiLine: 20, Line: 1},
                      logger=logger)
        # create a legend container
        legend = Legend(viewer=viewer, title='One to control them all')

        # Initialise a data source
        time_range = UtcPeriod(-3600 * 24 * 100, 3600 * 24 * 100)
        data_source = DataSource(ts_adapter=ExampleTsAdapterSine(unit_to_decorate='MW', time_range=time_range),
                                 unit='MW', request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                 time_range=time_range)

        # Initialise views
        # create a fill in between view (for example a percentile)
        tooltips = [("label", "@label"), ("color", "@color")]
        fill_in_between_view = FillInBetween(color='purple', unit='MW', label='test adapter fill in between',
                                             visible=True,
                                             view_container=fig1, indices=(0, 1), fill_alpha=0.3, tooltips=tooltips)
        # create a line view
        tooltips = [("color", "@color")]
        line_view = MultiLine(colors=['blue'], unit='MW', labels=['test adapter line'], visible=True,
                              view_container=fig1,
                              indices=[1], y_axis=ax1_fig1, tooltips=tooltips)

        # create the legend items
        # create legend item for line_view and fill_in_between_view
        legend_item_fig1 = LegendItem(view_container=legend, label='Original DsViewHandle Fig1',
                                      views=[line_view, fill_in_between_view])

        # create a legend item for all views
        legend_item_all = LegendItem(view_container=legend, label='Original DsViewHandle All',
                                     views=[line_view, fill_in_between_view])

        # Connecting the views and a data source through a DsViewHandle
        ds_view_handle = DsViewHandle(data_source=data_source, views=[line_view, fill_in_between_view,
                                                                      legend_item_fig1,
                                                                      legend_item_all])

        # Adding the ds_view_handle to the app
        viewer.add_ds_view_handles(ds_view_handles=[ds_view_handle])

        # IN RUNTIME
        # Setting up a DsViewHandle generator and connecting it to the app
        ds_view_handle_generator = DsViewHandleGenerator(plot=fig1, table=None, legend=legend)
        connect_ports(ds_view_handle_generator.send_ds_view_handles_to_add, viewer.receive_ds_view_handles_to_add)
        connect_ports(ds_view_handle_generator.send_ds_view_handles_to_remove, viewer.receive_ds_view_handles_to_remove)

        layout = column(ds_view_handle_generator.layout,
                        row(viewer.layout, reset_tool.layout, reset_y_range_tool.layout),
                        row(wheel_zoom.layout),
                        row(view_period_selector.layout),
                        row(column(fig1.layout), legend.layout),
                        )
        return layout
