from shyft.dashboard.base.ports import connect_ports, Receiver
from typing import Optional, Dict, Any
from bokeh.layouts import column, row

import shyft.time_series as sa

from shyft.dashboard.time_series.tools.figure_tools import TimePeriodSelectorInFigure, WheelZoomDirection
from shyft.dashboard.base.app import AppBase

from shyft.dashboard.time_series.view_container.figure import Figure
from shyft.dashboard.time_series.ts_viewer import TsViewer
from shyft.dashboard.widgets.logger_box import LoggerBox
import numpy as np


class TsPeriodSelectorExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "ts_period_select_example"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name

        start = sa.utctime_now()
        end = start+sa.Calendar().MONTH*5

        ts_restrictions = np.array([sa.Calendar.HOUR * 3,
                                    sa.Calendar.DAY,
                                    sa.Calendar.WEEK,
                                    sa.Calendar.MONTH,
                                    sa.Calendar.QUARTER,
                                    sa.Calendar.YEAR])

        timeperiod_selector = TimePeriodSelectorInFigure(logger=logger)
        timeperiod_selector.receive_dt(sa.Calendar.WEEK)
        wheel_zoom = WheelZoomDirection(logger=logger)
        # Create our viewer app
        viewer = TsViewer(bokeh_document=doc,
                          time_step_restrictions=ts_restrictions,
                          init_view_range=sa.UtcPeriod(start, end),
                          logger=logger)
        # create first figure with all additional y-axes
        fig1 = Figure(viewer=viewer, tools=[wheel_zoom, timeperiod_selector], width=1400, logger=logger)

        def _receive_utc_period(period: sa.UtcPeriod):
            print(f'Received selected period {period}')
            if logger:
                logger.info(f'Received selected period {period}')

        receive_utc_period = Receiver(parent=self, func=_receive_utc_period, signal_type=sa.UtcPeriod,
                                      name='receive period')
        connect_ports(timeperiod_selector.send_time_period, receive_utc_period)

        return column(timeperiod_selector.layout,
                      row(wheel_zoom.layout, viewer.layout), fig1.layout)
