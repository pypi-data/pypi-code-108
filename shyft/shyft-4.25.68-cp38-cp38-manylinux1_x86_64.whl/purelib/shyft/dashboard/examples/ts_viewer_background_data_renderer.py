"""
How we like things to be
"""
from typing import Optional, Dict, Any
import numpy as np

import bokeh
from bokeh.layouts import row, column

from shyft.time_series import (UtcPeriod, point_interpretation_policy, TimeSeries, DoubleVector, TsVector, TimeAxis,
                               Calendar)

from shyft.dashboard.time_series.ds_view_handle import DsViewHandle
from shyft.dashboard.time_series.sources.source import DataSource
from shyft.dashboard.time_series.ts_viewer import TsViewer
from shyft.dashboard.time_series.view import BackgroundData, Line
from shyft.dashboard.time_series.view_container.figure import Figure
from shyft.dashboard.time_series.axes_handler import DsViewTimeAxisType
from shyft.dashboard.time_series.state import State, Unit, Quantity
from shyft.dashboard.time_series.sources.ts_adapter import TsAdapter
from shyft.dashboard.widgets.logger_box import LoggerBox
from shyft.dashboard.time_series.tools.ts_viewer_tools import ResetTool
from shyft.dashboard.time_series.tools.figure_tools import (ResetYRange)

from shyft.dashboard.base.app import AppBase


# -- DEFINITION OF DATA

class ExampleTsAdapterBackgroundData(TsAdapter):

    def __init__(self, unit_to_decorate: Unit, time_range: UtcPeriod) -> None:
        self.cal = Calendar()
        self.point_interpretation = point_interpretation_policy.POINT_AVERAGE_VALUE
        self.unit_to_decorate = unit_to_decorate
        # generate a time series with random data with dt 1h
        n = time_range.diff_units(self.cal, self.cal.HOUR)
        ta = TimeAxis(time_range.start, self.cal.HOUR, n)
        vals = np.random.randint(8, size=n)
        vals[20:100] = 2
        vals[200:500] = 1
        vals[1000:1500] = 3
        self.ts1 = TimeSeries(ta, DoubleVector.from_numpy(vals), self.point_interpretation)

    def __call__(self, *, time_axis, unit) -> Quantity[TsVector]:
        # average the known values to fit to the current given time axis

        ts_input = TimeSeries(time_axis, DoubleVector.from_numpy(time_axis.time_points[:-1]), self.point_interpretation)

        ts1 = self.ts1.use_time_axis_from(ts_input)
        ts1.set_point_interpretation(self.point_interpretation)
        tsv = TsVector([ts1])
        return State.unit_registry.Quantity(tsv, self.unit_to_decorate)


class BackgroundDataRendererExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]] = None):
        super().__init__(thread_pool=thread_pool)
        self.logger = None  # app_kwargs['logger']

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "background_renderer_example"

    def get_layout(self, doc: bokeh.document.Document, logger: Optional[LoggerBox] = None) -> bokeh.layouts.LayoutDOM:
        """
        This function returns the full page layout for the app
        """
        # PRE RUNTIME
        figure_width = 800
        doc.title="ts-bg-rendering"
        # Initialising the different tools for the app
        # ts viewer tools
        reset_tool = ResetTool(logger=logger)
        # figure tools
        reset_y_range_tool = ResetYRange(logger=logger)

        # Create our viewer app
        viewer = TsViewer(bokeh_document=doc, unit_registry=State.unit_registry,
                          tools=[reset_tool],
                          time_step_restrictions=[Calendar.HOUR*3, Calendar.DAY, Calendar.WEEK],
                          thread_pool_executor=self.thread_pool, logger=logger)

        # create first figure with all additional y-axes
        fig1 = Figure(viewer=viewer, tools=[reset_y_range_tool],
                      width=figure_width,
                      logger=logger)

        # Initialise a data source
        time_range = UtcPeriod(-3600*24*100, 3600*24*100)
        data_source = DataSource(ts_adapter=ExampleTsAdapterBackgroundData(unit_to_decorate='MW', time_range=time_range),
                                 unit='MW', request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                 time_range=time_range)

        # Initialise views
        # the view creates random data but some values are fixed to 2, 1 and 1.3 this one should be highlighted
        #color_map = {3: "blue", 2: "purple", 1: "green"}

        values_color_map = {3: {'color': "blue", 'label': 'the machine is on'},
                            2: {'color': "purple", 'label': 'the machine is off'},
                            1: {'color': "green", 'label': 'the machine is starting'}}

        # create a back ground data view
        background_data_view = BackgroundData(unit='MW', label='test adapter fill in between', visible=True,
                                              default_color='red',
                                              view_container=fig1, index=0,
                                              fill_alpha=0.3, values_color_map=values_color_map,
                                              y_max=10, y_min=-10, show_not_defined=False)
        # create a line view to show the same data
        line = Line(view_container=fig1, color='black', line_width=1, index=0, unit='MW', label='data as a line')

        # Connecting the views and a data source through a DsViewHandle
        ds_view_handle = DsViewHandle(data_source=data_source, views=[background_data_view, line])

        # Adding the ds_view_handle to the app
        viewer.add_ds_view_handles(ds_view_handles=[ds_view_handle])


        # add some buttons and selctors to test the callbacks

        not_defiend_button = bokeh.models.widgets.Button(label='Show not defined')

        def change_show_not_defined():
            background_data_view.show_not_defined = [True, False][background_data_view.show_not_defined]

        not_defiend_button.on_click(change_show_not_defined)

        fill_alpha_button = bokeh.models.widgets.Button(label='Change fill_alpha: 0.3')

        def change_fill_alpha():
            if background_data_view.fill_alpha == 0.3:
                background_data_view.fill_alpha = 0.6
                fill_alpha_button.label = 'Change fill_alpha: 0.6'
            else:
                background_data_view.fill_alpha = 0.3
                fill_alpha_button.label = 'Change fill_alpha: 0.3'

        fill_alpha_button.on_click(change_fill_alpha)

        color_map_button = bokeh.models.widgets.Button(label=f'mix up color map {values_color_map}')

        def mix_up_color_map():
            if background_data_view.values_color_map[3]['color'] != "blue":
                values_color_map = {3: {'color': "blue", 'label': 'the machine is on'},
                                    2: {'color': "purple", 'label': 'the machine is off'},
                                    1: {'color': "green", 'label': 'the machine is starting'}}
                background_data_view.values_color_map = values_color_map
                color_map_button.label = f'mix up color map {values_color_map}'
            else:
                values_color_map = {3: {'color': "green", 'label': 'the machine is on'},
                                    2: {'color': "orange", 'label': 'the machine is off'},
                                    1: {'color': "black", 'label': 'the machine is starting'}}
                background_data_view.values_color_map = values_color_map
                color_map_button.label = f'mix up color map {values_color_map}'

        color_map_button.on_click(mix_up_color_map)

        layout = column(row(viewer.layout, reset_tool.layout, reset_y_range_tool.layout),
                        row(fig1.layout),
                        row(bokeh.models.widgets.Div(text="Callbacks to change view properties:")),
                        row(not_defiend_button, fill_alpha_button, color_map_button)
                        )

        return layout
