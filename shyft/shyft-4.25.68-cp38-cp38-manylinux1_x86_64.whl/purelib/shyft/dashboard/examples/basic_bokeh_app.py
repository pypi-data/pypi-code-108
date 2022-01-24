from typing import Optional, Dict, Any
from bokeh.layouts import column
import bokeh.models
import bokeh.plotting
import shyft.time_series as sa

from shyft.dashboard.time_series.tools.figure_tools import TimePeriodSelectorInFigure, WheelZoomDirection
from shyft.dashboard.base.app import AppBase

from shyft.dashboard.time_series.view_container.figure import Figure
from shyft.dashboard.time_series.ts_viewer import TsViewer
from shyft.dashboard.widgets.logger_box import LoggerBox


class BasicBokeh(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "basic_bokeh_app"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name
        figure = bokeh.plotting.figure(width=500, height=299, x_axis_type="datetime")
        diamonds = bokeh.models.markers.DiamondCross(x='x', y='y', size=10)
        line = bokeh.models.Line(x='x', y='y')

        data = {'x':[1,2,3,4,5], 'y':[1,2,3,4,5]}
        ds = bokeh.models.ColumnDataSource(data)
        if logger:
            logger.debug(f'Add data for diamond scatter {data}')

        data2 = {'x': [1,2,3,4,5], 'y': [5,4,3,2,1]}
        ds2 = bokeh.models.ColumnDataSource(data2)

        if logger:
            logger.debug(f'Add data for line {data}')

        figure.add_glyph(ds, diamonds)
        figure.add_glyph(ds2, line)

        return column(figure)
