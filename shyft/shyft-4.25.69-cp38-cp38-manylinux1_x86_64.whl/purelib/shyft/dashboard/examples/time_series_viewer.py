"""
How we like things to be
"""
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import itertools

import bokeh
from bokeh.layouts import row, column
from bokeh.models.widgets import Button, RadioButtonGroup, Select
from shyft.dashboard.examples.test_data_generator import ExampleTsAdapterSine

from shyft.time_series import UtcPeriod, Calendar

from shyft.dashboard.base.ports import Sender, connect_ports, Receiver, States

from shyft.dashboard.time_series.ds_view_handle import DsViewHandle
from shyft.dashboard.time_series.sources.source import DataSource
from shyft.dashboard.time_series.tools.table_tools import ExportTableDataButton
from shyft.dashboard.time_series.ts_viewer import TsViewer
from shyft.dashboard.time_series.view import TableView, FillInBetween, Line, LegendItem
from shyft.dashboard.time_series.view_container.figure import Figure
from shyft.dashboard.time_series.view_container.table import Table, StatisticsTable
from shyft.dashboard.time_series.view_container.legend import Legend
from shyft.dashboard.time_series.axes_handler import DsViewTimeAxisType, TimePeriodSelectorTableViewTimeAxis
from shyft.dashboard.time_series.state import State
from shyft.dashboard.widgets.logger_box import LoggerBox
from shyft.dashboard.widgets.selector_models import LabelDataSelector
from shyft.dashboard.base.selector_presenter import SelectorPresenter
from shyft.dashboard.base.selector_views import MultiSelect
from shyft.dashboard.time_series.tools.ts_viewer_tools import ResetTool
from shyft.dashboard.time_series.tools.figure_tools import (ResetYRange, TimePeriodSelectorInFigure, WheelZoomDirection,
                                                            ExportLineDataButton, TimePeriodSelectorSlider)
from shyft.dashboard.time_series.tools.view_time_axis_tools import ViewPeriodSelector
from shyft.dashboard.time_series.axes import YAxis, YAxisSide

from shyft.dashboard.base.app import AppBase


class DsViewHandleGenerator:

    def __init__(self, plot, table, legend, async_on=False):
        self.async_on = async_on
        self.plot = plot
        self.table = table
        self.legend = legend
        self.units = itertools.cycle(['GW', 'km', 'MW', 'm', 'W', 'ft'])
        self.colors = itertools.cycle(["green", "magenta"])

        self.send_ds_view_handles_to_add = Sender(parent=self, name="Add DsViewHandle sender",
                                                  signal_type=List[DsViewHandle])
        self.send_ds_view_handles_to_remove = Sender(parent=self, name="Remove DsViewHandle sender",
                                                     signal_type=List[DsViewHandle])
        self.ds_view_handles = {}

        # add small widgets to control creation and deletion of the ds_view_handles
        # button to create ds view handles
        self.add_button = Button(label='Add DsViewHandle')
        self.add_button.on_click(self.create_and_send_ds_view_handle)

        # selector model for removing ds view handles
        self.dsvh_select_view = MultiSelect(title="choose DsViewHandle to remove")
        dsvh_selector_presenter = SelectorPresenter("dsvh select", view=self.dsvh_select_view)
        self.dsvh_selector_model = LabelDataSelector(presenter=dsvh_selector_presenter)

        self.receive_selected_dsvh_labels = Receiver(parent=self, name="dsvh labels to remove",
                                                     func=self.remove_ds_view_handle,
                                                     signal_type=List[str])
        connect_ports(self.dsvh_selector_model.send_selected_labels, self.receive_selected_dsvh_labels)
        # layout
        self.layout = column(self.add_button, self.dsvh_select_view.layout)

    def create_and_send_ds_view_handle(self) -> None:
        """ Create a new ds view handle and send it"""

        unit = next(self.units)
        color = next(self.colors)
        n_handles = len(self.ds_view_handles) + 1
        dsvh_tag = f'DsViewHandle {n_handles} {unit}'
        shift = 3600*24*n_handles*20
        time_range = UtcPeriod(-3600*24*100 + shift, 3600*24*100 + shift)
        data_source = DataSource(ts_adapter=ExampleTsAdapterSine(unit_to_decorate=unit, time_range=time_range,
                                                                 async_on=self.async_on),
                                 unit=unit, request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                 time_range=time_range)
        line_view = Line(color=color, unit=unit, label=f'test adapter line {n_handles}', visible=True,
                         view_container=self.plot,
                         index=1)
        table_view = TableView(view_container=self.table, columns={0: 'mer tull'}, label=f'bakvendtland {n_handles}',
                               unit='MW')
        legend_item = LegendItem(view_container=self.legend, label=dsvh_tag, views=[line_view])
        ds_view_handle = DsViewHandle(data_source=data_source, views=[line_view, legend_item])

        # save the ds view handle in a dict
        self.ds_view_handles[dsvh_tag] = ds_view_handle
        # update the selector model with the new tag
        self.dsvh_selector_model.receive_labels_to_add([dsvh_tag])
        # send the ds view handle to
        self.send_ds_view_handles_to_add([ds_view_handle])

    def remove_ds_view_handle(self, names: List[str]) -> None:
        """Remove a specific ds view handle"""
        dsvh_to_delete = []
        for name in names:
            if name in self.ds_view_handles:
                dsvh_to_delete.append(self.ds_view_handles[name])
        if not dsvh_to_delete:
            return
        # update selector model
        all_options = self.dsvh_selector_model.presenter.options
        new_options = [o for o in all_options if o not in names]
        self.dsvh_selector_model.receive_labels(new_options)
        self.send_ds_view_handles_to_remove(dsvh_to_delete)


class TsViewerExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]] = None):
        super().__init__(thread_pool=thread_pool)
        self.logger = None  # app_kwargs['logger']

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "ts_viewer_example"

    def get_layout(self, doc: bokeh.document.Document, logger: Optional[LoggerBox] = None) -> bokeh.layouts.LayoutDOM:
        """
        This function returns the full page layout for the app
        """
        # PRE RUNTIME
        doc.title = self.name
        figure_width = 800
        # Initialising the different tools for the app
        # ts viewer tools
        reset_tool = ResetTool(logger=logger)
        # figure tools
        reset_y_range_tool = ResetYRange(logger=logger)
        timeperiod_selector = TimePeriodSelectorInFigure(logger=logger)
        timeperiod_selector.receive_dt(2*Calendar.WEEK)
        wheel_zoom = WheelZoomDirection(logger=logger)
        download_button = ExportLineDataButton(logger=logger, label='Download Data Figure 1', width=150)
        timeperiod_selector_slider = TimePeriodSelectorSlider(slider_width=int(figure_width*0.82))
        timeperiod_selector_slider2 = TimePeriodSelectorSlider(slider_width=int(figure_width*0.82), color='#ffbf4a')
        # view time axis tools
        view_period_selector = ViewPeriodSelector(logger=logger)

        # Set up async thread pool
        async_on = True
        thread_pool_executor = ThreadPoolExecutor(5)  # self.thread_pool

        # Create our viewer app
        viewer = TsViewer(bokeh_document=doc, unit_registry=State.unit_registry,
                          tools=[reset_tool, view_period_selector],
                          time_step_restrictions=[Calendar.HOUR*3, Calendar.DAY, Calendar.WEEK],
                          thread_pool_executor=thread_pool_executor, logger=logger)

        # Create view containers
        # tools for the table
        export_table_data_tool = ExportTableDataButton()
        # create a table
        table1 = Table(viewer=viewer, logger=logger, tools=export_table_data_tool)

        alternative_view_time_axis = TimePeriodSelectorTableViewTimeAxis(time_period_selector=timeperiod_selector_slider, logger=logger)
        stats_table = StatisticsTable(viewer=viewer, logger=logger, height=150, width=figure_width + 200,
                                      alternative_view_time_axis=alternative_view_time_axis)

        alternative_view_time_axis2 = TimePeriodSelectorTableViewTimeAxis(
            time_period_selector=timeperiod_selector_slider2, logger=logger)
        stats_table2 = StatisticsTable(viewer=viewer, logger=logger, height=150, width=figure_width + 200,
                                       alternative_view_time_axis=alternative_view_time_axis2)

        # set up additional y-axes
        ax1_fig1 = YAxis(label="left nonsens axes", unit='MW', side=YAxisSide.LEFT)
        ax2_fig1 = YAxis(label="right nonsens axes", unit='GW', side=YAxisSide.RIGHT, color='green')
        ax3_fig1 = YAxis(label="right nonsens axes 2", unit='m', side=YAxisSide.RIGHT, color='magenta')
        # create first figure with all additional y-axes
        fig1 = Figure(viewer=viewer, tools=[reset_y_range_tool, timeperiod_selector, wheel_zoom, download_button,
                                            timeperiod_selector_slider, timeperiod_selector_slider2],
                      width=figure_width,
                      y_axes=[ax1_fig1, ax2_fig1, ax3_fig1], init_renderers={FillInBetween: 20, Line: 20}.items(),
                      logger=logger)
        # create second figure without any axis defined, default axis will get unit of first view assigned
        fig2 = Figure(viewer=viewer, tools=[reset_y_range_tool, wheel_zoom], logger=logger, width=figure_width)
        # create a legend container
        legend = Legend(viewer=viewer, title='One to control them all')

        # Initialise a data source
        time_range = UtcPeriod(-3600*24*100, 3600*24*100)
        data_source = DataSource(ts_adapter=ExampleTsAdapterSine(unit_to_decorate='MW', time_range=time_range,
                                                                 async_on=async_on),
                                 unit='MW', request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                 time_range=time_range)

        # Initialise views
        # create a fill in between view (for example a percentile)
        fill_in_between_view = FillInBetween(color='purple', unit='MW', label='test adapter fill in between', visible=True,
                                             view_container=fig1, indices=(0, 1), fill_alpha=0.3)
        # create 2 line views
        line_view = Line(color='blue', unit='MW', label='test adapter line', visible=True, view_container=fig1, index=1,
                         y_axis=ax1_fig1)

        line_view_fig2 = Line(color='red', unit='MW', label='test adapter line2', visible=True, view_container=fig2,
                              index=1)
        # create a table view
        table_view = TableView(view_container=table1, columns={0: 'tull', 1: 'ball'}, label='bakvendtland', unit='MW')
        table_view2 = TableView(view_container=stats_table, columns={0: 'tull', 1: 'ball'}, label='bakvendtland', unit='MW')
        table_view3 = TableView(view_container=stats_table2, columns={0: 'tull', 1: 'ball'}, label='bakvendtland',
                                unit='MW')
        # create the legend items
        # create legend item for line_view and fill_in_between_view
        legend_item_fig1 = LegendItem(view_container=legend, label='Original DsViewHandle Fig1',
                                      views=[line_view, fill_in_between_view])
        # create legend item for line_view_fig2
        legend_item_fig2 = LegendItem(view_container=legend, label='Original DsViewHandle Fig2', views=[line_view_fig2])
        # create a legend item for all views
        legend_item_all = LegendItem(view_container=legend, label='Original DsViewHandle All',
                                     views=[line_view, fill_in_between_view, table_view, line_view_fig2])

        # Connecting the views and a data source through a DsViewHandle
        ds_view_handle = DsViewHandle(data_source=data_source, views=[table_view, line_view, fill_in_between_view,
                                                                      legend_item_fig1, legend_item_fig2,
                                                                      legend_item_all, table_view2, table_view3,
                                                                      line_view_fig2])

        # Adding the ds_view_handle to the app
        viewer.add_ds_view_handles(ds_view_handles=[ds_view_handle])

        # IN RUNTIME
        # Setting up a DsViewHandle generator and connecting it to the app
        ds_view_handle_generator = DsViewHandleGenerator(plot=fig1, table=table1, legend=legend, async_on=async_on)
        connect_ports(ds_view_handle_generator.send_ds_view_handles_to_add, viewer.receive_ds_view_handles_to_add)
        connect_ports(ds_view_handle_generator.send_ds_view_handles_to_remove, viewer.receive_ds_view_handles_to_remove)

        def change_visibility():
            line_view.visible = bool([1, 0][line_view.visible])
            line_view_fig2.visible = bool([1, 0][line_view_fig2.visible])
            fill_in_between_view.visible = bool([1, 0][fill_in_between_view.visible])
            table_view.visible = bool([1, 0][table_view.visible])

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
        color_button = RadioButtonGroup(labels=["blue", "green", "red"])
        color_button.on_change("active", change_color)
        # create a button to change the visibility of all views
        visibility_button = Button(label='Change Visibility')
        visibility_button.on_click(change_visibility)
        # create a button to change which index to show in line_view
        index_selector = Select(title='Index Selector', options=['0', '1', '2'], value='1')
        index_selector.on_change('value', change_index)
        # font size selector
        font_size_selector = Select(title='Figure 1 fontsize', options=['10', '16'], value='10')
        font_size_selector.on_change('value', change_figure_font_size)

        layout = column(ds_view_handle_generator.layout,
                        row(viewer.layout, reset_tool.layout, reset_y_range_tool.layout),
                        row(wheel_zoom.layout, visibility_button, color_button, state_button, index_selector),
                        row(view_period_selector.layout, timeperiod_selector.layout, font_size_selector),
                        row(column(fig1.layout, timeperiod_selector_slider.layout, timeperiod_selector_slider2.layout),
                            legend.layout, download_button.layout),
                        row(stats_table.layout),
                        row(stats_table2.layout),
                        row(fig2.layout),
                        row(table1.layout, export_table_data_tool.layout),
                        )
        return layout
