from bokeh.models import Panel, Tabs
from typing import List

from shyft.dashboard.time_series.view_container.view_container_base import BaseViewContainer


class ViewContainerTabsError(RuntimeError):
    pass


class ViewContainerTabs:
    """
    Object is a helper layout, creating a bokeh Tabs layout from provided Panels, as the bokeh Tabs does.
    Additional to bokeh tabs, a callback is implemented which can trigger the visibilty of view_container
    in the panels provided.
    Whenever a panel is activated all view_container in the Panel will be set to visible.

    Since the bokeh.panels can take a big layouts with buttons etc. we need to provide the view_container for which
    the visibility should be changed in a separate argument.
    This is the visibility_view_containers list. It should be as long as panels.
    The elements of visibility_view_containers should be of type List, they may view_container or be empty.

    Exemplified:
        If a Panel is activated, lets say the second panel (with index 1), all view_container in
        visibility_view_containers[1] will be set to visible=True, all other view_container will be set to
        visible = False
    """
    def __init__(self, panels: List[Panel],
                 visibility_view_containers: List[List[BaseViewContainer]],
                 width: int, height: int, active: int) -> None:
        """
        Bokeh Tabs layout controlling the visibility of the view_container inside the tabs

        Parameters
        ----------
        panels: List of bokeh.models.Panel which we  want to show in the tables
        visibility_view_containers: List of Lists with view_container matching with panels
        width: width of the Tabs widget
        height: height of the Tabs widget
        active: active Panel to start with
        """
        if len(panels) != len(visibility_view_containers) or len(panels) == 0:
            raise ViewContainerTabsError(
                f"nr. panels {len(panels)} not equal nr. visibility_view_containers {len(visibility_view_containers)}")
        if active >= len(panels):
            raise ViewContainerTabsError(
                f"nr. panels {len(panels)} < active Panel {active}")
        self.tabs = panels
        self.view_container = visibility_view_containers

        self.viewer_table = Tabs(tabs=panels, active=active, width=width, height=height)
        self.viewer_table.on_change('active', self.on_active_tabs)
        # initialize the visibility of all table components
        self.on_active_tabs('attr', '', active)

    def on_active_tabs(self, attr, old, new) -> None:
        """
        Callback to change on activating a tab
        """
        for i, vc_list in enumerate(self.view_container):
            for vc in vc_list:
                vc.visible = (i == new)

    @property
    def layout(self) -> Tabs:
        """ Layout, returns the bokeh.models.tabs  LayoutDom"""
        return self.viewer_table
