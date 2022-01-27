from typing import Optional

from bokeh.models import Div

from bokeh.document import Document
from bokeh.layouts import LayoutDOM, column

from shyft.dashboard.apps.water_route_app.example_hps import get_example_hps

from shyft.dashboard.apps.water_route_app.simplified_water_route import SimplifiedWaterRouteGraph
from shyft.dashboard.util.find_free_port import find_free_port
from shyft.dashboard.widgets.logger_box import LoggerBox

from shyft.dashboard.base.app import AppBase, start_bokeh_apps
from shyft.dashboard.widgets.water_route_widget import WaterRouteWidget


class WaterRouteApp(AppBase):

    def __init__(self, thread_pool, app_kwargs):
        super().__init__(thread_pool=thread_pool)
        self.logger = None

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "water_course_graph_example"

    def get_layout(self, doc: Document, logger: Optional[LoggerBox] = None) -> LayoutDOM:
        doc.title = "Water course graph"

        # --------------------------------------------------------------------------------------------------------------
        #  Creating a simple water course
        # --------------------------------------------------------------------------------------------------------------
        hps = get_example_hps()
        # --------------------------------------------------------------------------------------------------------------
        # Using the custom water-route-graph-app to visualize the water course
        # --------------------------------------------------------------------------------------------------------------
        water_route_graph = SimplifiedWaterRouteGraph()
        water_route_widget = WaterRouteWidget(water_route_graph=water_route_graph)
        water_route_widget.receive_selected_water_route([hps])

        div = Div(text="Water course graph")
        layout = column(div, water_route_widget.layout)
        return layout


if __name__ == "__main__":
    start_bokeh_apps(apps=[WaterRouteApp], port=find_free_port())
