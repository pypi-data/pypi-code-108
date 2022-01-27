from calendar import Calendar
from concurrent.futures import ThreadPoolExecutor
from tkinter import Button
from typing import Optional, Dict, Any
from bokeh.layouts import column, row
import bokeh.models
import bokeh.plotting
from bokeh.models import MultiLine

from bokeh.models.widgets import Button, RadioButtonGroup, Select

import shyft.time_series as sa
from shyft.dashboard.base.ports import connect_ports, States
from shyft.dashboard.base.selector_views import RadioButtonGroup, Select
from shyft.dashboard.time_series.axes import YAxis, YAxisSide
from shyft.dashboard.time_series.axes_handler import DsViewTimeAxisType, TimePeriodSelectorTableViewTimeAxis
from shyft.dashboard.time_series.ds_view_handle import DsViewHandle
from shyft.dashboard.time_series.sources.source import DataSource
from shyft.dashboard.time_series.state import State

from shyft.dashboard.time_series.tools.figure_tools import WheelZoomDirection, ResetYRange, TimeIntervalSelectorSlider
from shyft.dashboard.base.app import AppBase
from shyft.dashboard.time_series.tools.ts_viewer_tools import ResetTool
from shyft.dashboard.time_series.tools.view_time_axis_tools import ViewPeriodSelector
from shyft.dashboard.time_series.view import Line, FillInBetween, LegendItem, MultiLine, TableView
from shyft.dashboard.time_series.view_container.legend import Legend
from shyft.dashboard.time_series.view_container.table import StatisticsTable
from shyft.time_series import UtcPeriod, Calendar

from shyft.dashboard.time_series.view_container.figure import Figure
from shyft.dashboard.time_series.ts_viewer import TsViewer
from shyft.dashboard.widgets.logger_box import LoggerBox
from shyft.dashboard.time_series.tools.figure_tools import HoverTool
from shyft.dashboard.examples.time_series_viewer import DsViewHandleGenerator, ExampleTsAdapterSine


class TimeIntervalSliderExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "Time-period slider example"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name

        # PRE RUNTIME
        figure_width = 800
        # Initialising the different tools for the app
        # ts viewer tools
        reset_tool = ResetTool(logger=logger)
        # figure tools
        reset_y_range_tool = ResetYRange(logger=logger)
        wheel_zoom = WheelZoomDirection(logger=logger)
        timeperiod_selector_slider = TimeIntervalSelectorSlider(width=int(figure_width * 0.82))
        # view time axis tools
        view_period_selector = ViewPeriodSelector(logger=logger)

        # Set up async thread pool
        async_on = True
        thread_pool_executor = ThreadPoolExecutor(5)  # self.thread_pool

        # Create our viewer app
        viewer = TsViewer(bokeh_document=doc, title='Test Ts Viewer', unit_registry=State.unit_registry,
                          tools=[reset_tool, view_period_selector],
                          time_step_restrictions=[Calendar.HOUR * 3, Calendar.DAY, Calendar.WEEK],
                          thread_pool_executor=thread_pool_executor, logger=logger)

        # Create view containers
        alternative_view_time_axis = TimePeriodSelectorTableViewTimeAxis(
            time_period_selector=timeperiod_selector_slider, logger=logger)
        stats_table = StatisticsTable(viewer=viewer, logger=logger, height=150, width=figure_width + 200,
                                      alternative_view_time_axis=alternative_view_time_axis)

        # set up additional y-axes
        ax1_fig1 = YAxis(label="left nonsens axes", unit='MW', side=YAxisSide.LEFT)
        ax2_fig1 = YAxis(label="right nonsens axes", unit='GW', side=YAxisSide.RIGHT, color='green')
        ax3_fig1 = YAxis(label="right nonsens axes 2", unit='m', side=YAxisSide.RIGHT, color='magenta')
        # create first figure with all additional y-axes
        fig1 = Figure(viewer=viewer, tools=[reset_y_range_tool, wheel_zoom, timeperiod_selector_slider],
                      width=figure_width,
                      y_axes=[ax1_fig1, ax2_fig1, ax3_fig1],
                      init_renderers={FillInBetween: 20, Line: 20, MultiLine: 20},
                      logger=logger)
        # # create second figure without any axis defined, default axis will get unit of first view assigned
        # fig2 = Figure(viewer=viewer, tools=[reset_y_range_tool, wheel_zoom], logger=logger, width=figure_width)
        # # create a legend container
        legend = Legend(viewer=viewer, title='One to control them all')

        # Initialise a data source
        time_range = UtcPeriod(-3600 * 24 * 100, 3600 * 24 * 100)
        data_source = DataSource(ts_adapter=ExampleTsAdapterSine(unit_to_decorate='MW', time_range=time_range,
                                                                 async_on=async_on),
                                 unit='MW', request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                 time_range=time_range)

        # Initialise views
        # create a fill in between view (for example a percentile)
        fill_in_between_view = FillInBetween(color='purple', unit='MW', label='test adapter fill in between',
                                             visible=True,
                                             view_container=fig1, indices=(0, 1), fill_alpha=0.3)
        # create 2 line views
        line_view = Line(color='blue', unit='MW', label='test adapter line', visible=True, view_container=fig1, index=1,
                         y_axis=ax1_fig1)

        # create a table view
        table_view2 = TableView(view_container=stats_table, columns={0: 'tull', 1: 'ball'}, label='bakvendtland',
                                unit='MW')
        # create the legend items
        # create legend item for line_view and fill_in_between_view
        legend_item_fig1 = LegendItem(view_container=legend, label='Original DsViewHandle Fig1',
                                      views=[line_view, fill_in_between_view])

        # Connecting the views and a data source through a DsViewHandle
        ds_view_handle = DsViewHandle(data_source=data_source, views=[line_view, fill_in_between_view,
                                                                      legend_item_fig1, table_view2])

        # Adding the ds_view_handle to the app
        viewer.add_ds_view_handles(ds_view_handles=[ds_view_handle])

        # IN RUNTIME
        # Setting up a DsViewHandle generator and connecting it to the app
        ds_view_handle_generator = DsViewHandleGenerator(plot=fig1, table=None, legend=legend, async_on=async_on)
        connect_ports(ds_view_handle_generator.send_ds_view_handles_to_add, viewer.receive_ds_view_handles_to_add)
        connect_ports(ds_view_handle_generator.send_ds_view_handles_to_remove, viewer.receive_ds_view_handles_to_remove)

        def change_visibility():
            line_view.visible = bool([1, 0][line_view.visible])
            fill_in_between_view.visible = bool([1, 0][fill_in_between_view.visible])

        def change_color(attr, old, new):
            line_view.color = color_button.labels[new]

        def change_index(attr, old, new):
            line_view.index = int(new)

        def change_viewer_state():
            if viewer._state == States.ACTIVE:
                viewer.state_port.receive_state(States.DEACTIVE)
                state_button.label = 'Change ts_viewer State: DEACTIVE'
            elif viewer._state == States.DEACTIVE:
                viewer.state_port.receive_state(States.ACTIVE)
                state_button.label = 'Change ts_viewer State: ACTIVE'

        def change_figure_font_size(attr, old, new):
            font_size = f'{int(new)}pt'
            fig1.bokeh_figure.title.text_font_size = font_size
            fig1.bokeh_figure.axis.axis_label_text_font_size = font_size
            fig1.bokeh_figure.axis.major_label_text_font_size = font_size

        # Add buttons to test on_change_callback of view
        # create a state changing button for the whole app
        state_button = Button(label='Change ts_viewer State')
        state_button.on_click(change_viewer_state)
        # create a button to change the color of line_view
        # color_button = RadioButtonGroup(title='Zirt', labels=["blue", "green", "red"])
        # color_button.on_change("active", change_color)
        # create a button to change the visibility of all views
        visibility_button = Button(label='Change Visibility')
        visibility_button.on_click(change_visibility)
        # create a button to change which index to show in line_view
        # index_selector = Select(title='Index Selector', options=['0', '1', '2'], value='1')
        # index_selector.on_change('value', change_index)
        # font size selector
        # font_size_selector = Select(title='Figure 1 fontsize', options=['10', '16'], value='10')
        # font_size_selector.on_change('value', change_figure_font_size)

        layout = column(ds_view_handle_generator.layout,
                        row(viewer.layout, reset_tool.layout, reset_y_range_tool.layout),
                        row(wheel_zoom.layout, visibility_button, state_button),
                        row(view_period_selector.layout),
                        row(column(fig1.layout, timeperiod_selector_slider.layout),
                            legend.layout),
                        row(stats_table.layout)
                        )
        return layout
