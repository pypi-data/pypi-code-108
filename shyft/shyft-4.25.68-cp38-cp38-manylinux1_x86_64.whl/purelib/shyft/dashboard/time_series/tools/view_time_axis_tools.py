import abc

from typing import Any, List, Optional
from collections import OrderedDict
from packaging import version

from shyft.time_series import Calendar, UtcPeriod

import bokeh
from bokeh.models import Button, Div
from bokeh.layouts import row, column

from shyft.dashboard.base import constants
from shyft.dashboard.base.selector_views import Select
from shyft.dashboard.base.selector_presenter import SelectorPresenter
from shyft.dashboard.base.ports import connect_ports, connect_state_ports, States, Receiver, Sender
from shyft.dashboard.time_series.dt_selector import DeltaTSelector
from shyft.dashboard.time_series.tools.base import BaseTool
from shyft.dashboard.base.app import LayoutComponents
from shyft.dashboard.widgets.selector_models import LabelDataSelector, LabelDataSelectorClickPolicy


class ViewTimeAxisToolError(RuntimeError):
    pass


class ViewTimeAxisTool(BaseTool):
    """
    Base tool class for view time axis
    """

    def __init__(self, logger=None, *, parent_limit=None):
        """
        Parameters
        ----------
        logger:
            Optional logger
        parent_limit:
            number of max parents to use
        """
        super().__init__(logger=logger, parent_limit=parent_limit)

    @abc.abstractmethod
    def on_bind(self, *, parent: Any):
        pass


class DeltaTSelectorTool(ViewTimeAxisTool):
    """
    A tool to manually select the time step
    """

    def __init__(self,
                 title,
                 width: int = 150,
                 height: Optional[int] = None,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger=None):
        """
        Parameters
        ----------
        title:
            title of the widget
        logger:
            optional logger
        """
        super().__init__(logger=logger)

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        self.dt_view: Select = Select(title=title, width=width, height=height, padding=padding, sizing_mode=sizing_mode, logger=logger)
        dt_presenter = SelectorPresenter(name=title, view=self.dt_view, default='Auto', logger=logger)
        self.dt_select: DeltaTSelector = DeltaTSelector(presenter=dt_presenter, logger=logger)
        self.dt_select.state_port.receive_state(States.ACTIVE)
        self.layout: bokeh.layouts.LayoutDOM = self.dt_view.layout

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.dt_view.layout], 'figures': [], 'tables': []}

    def on_bind(self, *, parent: Any) -> None:
        connect_ports(parent.send_dt_options, self.dt_select.receive_selection_options)
        connect_ports(self.dt_select.send_dt, parent.receive_dt)
        connect_state_ports(parent.state_port, self.dt_select.state_port)


class ViewPeriodSelector(ViewTimeAxisTool):
    """
    Tool to set the time interval to step forward or backward in the graph by pushing a button 'Previous' and 'Next'
    """

    def __init__(self, logger=None):
        """
        Parameters
        ----------
        logger:
            Optional logger
        """
        super().__init__(logger=logger, parent_limit=1)
        self.cal = Calendar()

        button_width = 70
        button_height = 30

        self.previous_period = Button(label='Previous', width=button_width, height=button_height)
        self.previous_period.on_click(self.jump_to_previous_period)

        self.next_period = Button(label='Next', width=button_width, height=button_height)
        self.next_period.on_click(self.jump_to_next_period)

        self.select_periods = OrderedDict([('Auto', 0), ('Year', self.cal.YEAR), ('Month', self.cal.MONTH),
                                           ('Week', self.cal.WEEK)])

        self.selected_period = "Auto"
        self.dt_period: int = 0

        # create period selector sub-widget
        select_width = 110
        self.period_selector_view = Select(title='Select shift period', width=select_width, height=button_height,
                                           logger=logger, padding=7)
        self.period_selector_presenter = SelectorPresenter(name='Select shift period', view=self.period_selector_view,
                                                           default="Auto", logger=logger)
        self.period_selector = LabelDataSelector(presenter=self.period_selector_presenter, sort=False,
                                                 on_click_policy=LabelDataSelectorClickPolicy.SEND_SELECTED,
                                                 logger=logger)
        # connect period_selector to receiver
        receive_period_selection = Receiver(parent=self, name='receive period selection',
                                            func=self._receive_period_selection, signal_type=List[str])
        connect_ports(self.period_selector.send_selected_labels, receive_period_selection)

        # initialize sub-widget
        self.period_selector.receive_labels(self.select_periods.keys())  # set options
        self.period_selector_presenter.set_selector_value(self.selected_period, callback=False)  # set default option
        self.send_time_period = Sender(parent=self, name='Send selected time period', signal_type=UtcPeriod)

        if version.parse(bokeh.__version__) < version.parse("1.1"):
            button_spacer = row(width=0, height=15, sizing_mode="fixed")
            button_padding = 5
            widget_width = (2 * button_width + select_width + 3 * button_padding)
            widget_height = button_height
            self._layout = row(column(button_spacer, self.previous_period,
                                      width=button_width + button_padding,
                                      height=widget_height),
                               column(self.period_selector_view.layout,
                                      width=select_width + button_padding,
                                      height=widget_height),
                               column(button_spacer, self.next_period,
                                      width=button_width + button_padding,
                                      height=widget_height),
                               width=widget_width + 20, height=widget_height, sizing_mode="fixed")
        else:
            self._layout = row(column(row(height=19), self.previous_period),
                               self.period_selector_view.layout,
                               column(row(height=19), self.next_period))

    def on_bind(self, *, parent: Any):
        pass

    @property
    def layout(self) -> row:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        lc = {'widgets': [self.previous_period, self.period_selector_view.layout, self.next_period], 'figures': []}
        return lc

    def jump_to_next_period(self):
        if self._state == States.DEACTIVE:
            return
        parent = self.parents[0]
        view_range = parent.view_range
        start = view_range.start
        end = view_range.end
        if self.dt_period == 0:
            dt_period = view_range.timespan()
            # print('Auto', (end - start)/int(self.cal.DAY), 'days')
        else:
            dt_period = self.dt_period
        # calculate new x_range start and end
        parent.set_view_range(UtcPeriod(self.cal.add(int(start), int(dt_period), 1),
                                        self.cal.add(int(end), int(dt_period), 1)),
                              padding=False)

    def jump_to_previous_period(self):
        if self._state == States.DEACTIVE:
            return
        parent = self.parents[0]
        view_range = parent.view_range
        start = view_range.start
        end = view_range.end
        if self.dt_period == 0:
            dt_period = view_range.timespan()
            # print('Auto', (end - start)/int(self.cal.DAY), 'days')
        else:
            dt_period = self.dt_period
        # calculate new x_range start and end
        parent.set_view_range(UtcPeriod(self.cal.add(int(start), int(dt_period), -1),
                                        self.cal.add(int(end), int(dt_period), -1)),
                              padding=False)

    def _receive_period_selection(self, selection: List[str]):
        self.dt_period = self.select_periods[selection[0]]
