from typing import Any, Optional
import abc

from bokeh.models import Button
from bokeh.layouts import column

from shyft.dashboard.time_series.tools.base import BaseTool
from shyft.dashboard.base import constants
from shyft.dashboard.base.app import LayoutComponents
from shyft.dashboard.base.ports import States


class TsViewerTool(BaseTool):
    """
    Base tool class for TsViewer
    """
    def __init__(self, logger=None):
        """
        Parameters
        ----------
        logger:
            Optional logger
        """
        super().__init__(logger=logger)

    @abc.abstractmethod
    def on_bind(self, *, parent: Any) -> None:
        pass


class ResetTool(TsViewerTool):
    """
    A tool to reset the views back to the default viewing
    """

    def __init__(self,
                 width: int=80,
                 height: int=30,
                 padding: Optional[int]=None,
                 sizing_mode: Optional[str]=None,
                 logger=None):
        """
        Parameters
        ----------
        logger:
            Optional logger
        width:
            Optional width of the button
        """
        super().__init__(logger=logger)
        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode
        self.reset_button = Button(label='Reset', width=width, height=height)
        self.reset_button.on_click(self.on_click)

        self.layout = column(self.reset_button, height=height, width=width+padding, sizing_mode=sizing_mode)

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.reset_button],
                'figures': []}

    def on_bind(self, *, parent: Any) -> None:
        pass

    def on_click(self) -> None:
        """ If Reset button is clicked"""
        if self._state == States.DEACTIVE:
            return
        for parent in self.parents:
            parent.plot()
