import itertools
import numpy as np
from typing import Optional, Dict, Any
from bokeh.layouts import row
from bokeh.palettes import Set1
from shyft.dashboard.time_series.axes_handler import DsViewTimeAxisType  #, TimePeriodSelectorTableViewTimeAxis
from shyft.dashboard.time_series.state import State, Unit, Quantity
from shyft.dashboard.time_series.view import Line, LegendItem, MultiLine
from shyft.time_series import UtcPeriod, point_interpretation_policy, TimeSeries, DoubleVector, TsVector, TimeAxis, Calendar

from shyft.dashboard.time_series.ds_view_handle import DsViewHandle
from shyft.dashboard.time_series.sources.source import DataSource
from shyft.dashboard.time_series.sources.ts_adapter import TsAdapter

from shyft.dashboard.base.app import AppBase
from shyft.dashboard.time_series.view_container.legend import Legend
from shyft.dashboard.time_series.view_container.figure import Figure
from shyft.dashboard.time_series.ts_viewer import TsViewer
from shyft.dashboard.widgets.logger_box import LoggerBox
# from shyft.dashboard.time_series.renderer import LineRenderer, DiamondScatterRenderer


class TsAdapterSine(TsAdapter):

    def __init__(self, unit_to_decorate: Unit, time_range: UtcPeriod,
                 point_interpretation: point_interpretation_policy = None, async_on=False) -> None:
        self.async_on = async_on
        self.cal = Calendar()
        self.point_interpretation = point_interpretation or point_interpretation_policy.POINT_INSTANT_VALUE
        self.unit_to_decorate = unit_to_decorate
        # generate a time series with random data with dt 1h
        dt=60*10
        n = time_range.diff_units(self.cal, dt)
        self._ta: TimeAxis = TimeAxis(time_range.start, dt, n)
        self._ts: TimeSeries = None

    @property
    def ts(self):
        if not self._ts:
            t = self._ta.time_points[:-1]
            n = self._ta.size()
            f1 = int(1./self._ta.total_period().timespan())
            f2 = int(4./self._ta.total_period().timespan())
            vals = np.sin(2.*np.pi*f1*t) + np.cos(2.*np.pi*f2*t) + np.random.randn(n)*0.25 + np.random.rand(1)*10
            self._ts = TimeSeries(self._ta, DoubleVector.from_numpy(vals), self.point_interpretation) - 1
        return self._ts

    def __call__(self, *, time_axis, unit) -> Quantity[TsVector]:
        tsv = TsVector([self.ts]).average(time_axis).evaluate()
        tsv[0].set_point_interpretation(self.point_interpretation)
        return State.unit_registry.Quantity(tsv, self.unit_to_decorate)


class MultiTsAdapterSine(TsAdapter):

    def __init__(self, unit_to_decorate: Unit, time_range: UtcPeriod,
                 point_interpretation: point_interpretation_policy = None, async_on=False) -> None:
        self.async_on = async_on
        self.cal = Calendar()
        self.point_interpretation = point_interpretation or point_interpretation_policy.POINT_INSTANT_VALUE
        self.unit_to_decorate = unit_to_decorate
        # generate a time series with random data with dt 1h
        self._ta: TimeAxis = TimeAxis(time_range.start, self.cal.HOUR, time_range.diff_units(self.cal, self.cal.HOUR))
        self._tsv:TsVector = None
        # random singal with sin + cos + white noise

    @property
    def tsv(self)->TsVector:
        if not self._tsv:
            t = self._ta.time_points[:-1]
            n = self._ta.size()
            f1 = int(1./self._ta.total_period().timespan())
            f2 = int(4./self._ta.total_period().timespan())
            vals = np.sin(2.*np.pi*f1*t) + np.cos(2.*np.pi*f2*t) + np.random.randn(n)*0.25 + np.random.rand(1)*10
            vals1 = np.sin(2.*np.pi*f1*t) + np.cos(2.*np.pi*f2*t) + np.random.randn(n)*0.25 + np.random.rand(1)*10
            vals2 = np.sin(2.*np.pi*f1*t) + np.cos(2.*np.pi*f2*t) + np.random.randn(n)*0.25 + np.random.rand(1)*10
            self._tsv= TsVector([
                TimeSeries(self._ta, DoubleVector.from_numpy(vals), self.point_interpretation) - 1,
                TimeSeries(self._ta, DoubleVector.from_numpy(vals1), self.point_interpretation),
                TimeSeries(self._ta, DoubleVector.from_numpy(vals2), self.point_interpretation) + 1
            ])
        return self._tsv

    def __call__(self, *, time_axis, unit) -> Quantity[TsVector]:
        # average the known values to fit to the current given time axis
        r= self.tsv.average(time_axis).evaluate()  # do the math fast and multithreaded
        for ts in r:
            ts.set_point_interpretation(self.point_interpretation) # set presentation layer curve-type(hmm)
        return State.unit_registry.Quantity(r, self.unit_to_decorate) # wrap to a unit


class FigureLegend(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]] = None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "ts_legend"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox] = None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name
        ts_viewer = TsViewer(bokeh_document=doc,thread_pool_executor=self.thread_pool,
                             unit_registry=State.unit_registry,
                             time_step_restrictions=[60*10,Calendar.HOUR,Calendar.HOUR*3, Calendar.DAY, Calendar.WEEK], )
        fig = Figure(viewer=ts_viewer)
        legend = Legend(viewer=ts_viewer)

        unit = 'MW'
        color_generator = itertools.cycle(Set1[9])
        shift = 3600*24*3*20
        time_range = UtcPeriod(-3600*24*100 + shift, 3600*24*100 + shift)

        ts_adapter1 = TsAdapterSine(unit_to_decorate=unit, time_range=time_range, async_on=True)
        ts_adapter2 = TsAdapterSine(unit_to_decorate=unit, time_range=time_range, async_on=True)
        ts_adapter3 = TsAdapterSine(unit_to_decorate=unit, time_range=time_range, async_on=True)
        ts_adapter4 = MultiTsAdapterSine(unit_to_decorate=unit, time_range=time_range, async_on=True)
        ts_adapter5 = MultiTsAdapterSine(unit_to_decorate=unit, time_range=time_range, async_on=True)
        ts_adapter6 = MultiTsAdapterSine(unit_to_decorate=unit, time_range=time_range, async_on=True)

        data_source1 = DataSource(ts_adapter=ts_adapter1,
                                  unit=unit,
                                  request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                  time_range=time_range)
        data_source2 = DataSource(ts_adapter=ts_adapter2,
                                  unit=unit,
                                  request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                  time_range=time_range)
        data_source3 = DataSource(ts_adapter=ts_adapter3,
                                  unit=unit,
                                  request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                  time_range=time_range)
        data_source4 = DataSource(ts_adapter=ts_adapter4,
                                  unit=unit,
                                  request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                  time_range=time_range)
        data_source5 = DataSource(ts_adapter=ts_adapter5,
                                  unit=unit,
                                  request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                  time_range=time_range)
        data_source6 = DataSource(ts_adapter=ts_adapter6,
                                  unit=unit,
                                  request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
                                  time_range=time_range)

        line_view_1 = Line(color=next(color_generator), unit=unit, label='line 1', visible=True, view_container=fig, index=0)
        line_view_2 = Line(color=next(color_generator), unit=unit, label='line 2', visible=True, view_container=fig, index=0)
        line_view_3 = Line(color=next(color_generator), unit=unit, label='line 3', visible=True, view_container=fig, index=0)

        multi_line_view_1 = MultiLine(view_container=fig,
                                      unit=unit,
                                      labels=['multi label 1', 'multi label 2', 'multi label 3'],
                                      line_widths=[2, 2, 2],
                                      line_styles=['solid', 'dashed', 'solid'],
                                      colors=[next(color_generator), next(color_generator), next(color_generator)],
                                      indices=[0, 1, 2],
                                      expandable=True)

        multi_line_view_2 = MultiLine(view_container=fig,
                                      unit=unit,
                                      labels=['multi label 1', 'multi label 2', 'multi label 3'],
                                      line_widths=[2, 2, 2],
                                      line_styles=['solid', 'dashed', 'solid'],
                                      colors=[next(color_generator), next(color_generator), next(color_generator)],
                                      indices=[0, 1, 2],
                                      expandable=False)

        multi_line_view_3 = MultiLine(view_container=fig,
                                      unit=unit,
                                      labels=['a single line'],
                                      line_widths=[2],
                                      line_styles=['solid'],
                                      colors=[next(color_generator)],
                                      indices=[0])

        legend_item_1 = LegendItem(view_container=legend, label='line 1', views=[line_view_1])
        legend_item_2 = LegendItem(view_container=legend, label='line 2', views=[line_view_2])
        legend_item_3 = LegendItem(view_container=legend, label='line 3', views=[line_view_3])
        legend_item_4 = LegendItem(view_container=legend, label='expandable multiline', views=[multi_line_view_1],
                                   expanded=False)
        legend_item_5 = LegendItem(view_container=legend, label='regular multiline', views=[multi_line_view_2],
                                   expanded=True)
        legend_item_6 = LegendItem(view_container=legend, label='single multiline', views=[multi_line_view_3])

        ds_view1 = DsViewHandle(data_source=data_source1, views=[line_view_1, legend_item_1], tag='handle1')
        ds_view2 = DsViewHandle(data_source=data_source2, views=[line_view_2, legend_item_2], tag='handle2')
        ds_view3 = DsViewHandle(data_source=data_source3, views=[line_view_3, legend_item_3], tag='handle3')
        ds_view4 = DsViewHandle(data_source=data_source4, views=[multi_line_view_1, legend_item_4])
        ds_view5 = DsViewHandle(data_source=data_source5, views=[multi_line_view_2, legend_item_5])
        ds_view6 = DsViewHandle(data_source=data_source6, views=[multi_line_view_3, legend_item_6])

        ts_viewer.add_ds_view_handles(ds_view_handles=[ds_view1, ds_view2, ds_view3, ds_view4, ds_view5, ds_view6])

        return row(fig.layout, legend.layout)
