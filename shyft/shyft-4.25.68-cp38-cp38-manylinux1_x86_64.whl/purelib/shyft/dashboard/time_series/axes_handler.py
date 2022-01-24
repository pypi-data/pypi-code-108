import abc
from typing import Optional, Union, List, Tuple, Callable, Any
import logging
from enum import Enum

import numpy as np

from shyft.dashboard.time_series.view_time_axes import create_view_time_axis, extend_time_axis, ViewTimeAxisProperties
from shyft.time_series import Calendar, utctime_now, TimeAxis, deltahours, UtcPeriod, min_utctime, max_utctime, time

from bokeh.models import Range1d

from shyft.dashboard.base import constants
from shyft.dashboard.base.ports import (Sender, Receiver, States, StatePorts, connect_ports)
from shyft.dashboard.base.app import update_value_factory
from shyft.dashboard.time_series.bindable import Bindable
from shyft.dashboard.time_series.tools.view_time_axis_tools import ViewTimeAxisTool, DeltaTSelectorTool


class TimeAxisHandlerError(RuntimeError):
    pass


class DsViewTimeAxisType(Enum):
    padded_view_time_axis = 0
    view_time_axis = 1


class BaseViewTimeAxis(Bindable):
    """
    This object represents the link between time axis handle and actual view time axis in the figures.

    Implemented as a Base object but now only one figure type from bokeh is used ..

    Attributes
    ----------
    receive_view_period: Port to receive UtcPeriod to set view to

    Methods
    -------
    trigger_update: triggers the update method of parent, a TimeAxisHandle should be used to
                    trigger update machinery of
                    the time axis and all views, i.e. when the figure range changed

    Abstract methods/properties
    ----------------
    set_view_period: function to set the view of the figures and the time axis
    view_range: a property to get the current view range as a shyft.time_series.UtcPeriod
    """

    def __init__(self, logger: Optional['logging.Logger'] = None):
        """
        Parameters
        ----------
        logger: optional logger
        """
        super().__init__()
        self.logger = logger or logging.getLogger()

        self.receive_view_period: Receiver = Receiver(parent=self, name="receive view time axis utc period",
                                                      signal_type=UtcPeriod, func=self._receive_view_period)

        self._state: States = States.ACTIVE
        self.state_port: StatePorts = StatePorts(parent=self, _receive_state=self._receive_state)
        self._time_axis_update_callbacks = {}

    def _receive_view_period(self, view_period: UtcPeriod) -> None:
        """
        This function is the port function of the self.receive_view_period port.
        It sets the received view period with padding, triggering the callback
        """
        self.set_view_range(view_period, padding=True, callback=True)

    def trigger_update(self):
        """
        This function triggers the update method of the parent calls
        """
        if self.bound:
            self.parent.trigger_time_axis_update()
            for callback in self._time_axis_update_callbacks.values():
                callback()

    def on_change_view_range(self, obj, callback) -> None:
        """
        This function can be used to add on change view range callbacks, which informs the obj
        that the view range was changed

        Callback should have the form
        def callback():
            ..
        """
        self._time_axis_update_callbacks.update({obj: callback})

    def remove_on_change_view_range(self, obj) -> None:
        """
        This function removes an on change view range callback
        """
        self._time_axis_update_callbacks.pop(obj, None)

    @abc.abstractmethod
    def set_view_range(self, view_range: UtcPeriod, callback: bool = True, padding: bool = True) -> None:
        """
        This function sets the view period of the view time axis and thus of all adjoint figures

        Parameters
        ----------
        view_range: UtcPeriod of start and end of view range
        callback: trigger update callback or not
        padding: add padding to the view range or not
        """
        pass

    @property
    @abc.abstractmethod
    def view_range(self) -> UtcPeriod:
        """
        This property returns current view as a shyft.time_series.UtcPeriod
        :return:
        """
        pass

    def _receive_state(self, state: States) -> None:
        """
        This function sets the object into the received state
        """
        if state == self._state:
            return
        self._state = state
        if state == States.DEACTIVE:
            self.state_port.send_state(state)
        elif state == States.LOADING or state == States.READY:
            self._state = States.ACTIVE
        elif state == States.ACTIVE:
            pass
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)


class BokehViewTimeAxis(BaseViewTimeAxis):
    """
    This object represents the link between time axis handle and actual view time axis in bokeh figures.

    It has a periodic callback to check the figure view and triggers the update of data whenever the time axis is
    changed

    Attributes
    ----------
    shared_x_range: Range1d bokeh visual slider to select what to view
    """

    def __init__(self, bokeh_document: 'bokeh.document.Document',
                 init_view_range: Optional[UtcPeriod] = None,
                 zoom_in_interval: Optional[int] = None,
                 zoom_out_interval: Optional[int] = None,
                 x_range_padding: int = 0.05,
                 time_zone: Optional[str] = None,
                 logger: Optional['logging.Logger'] = None) -> None:
        """
        Parameters
        ----------
        bokeh_document: the bokeh document where the ts viewer resides
        init_view_range: initial view range
        zoom_in_interval: range in UTC s of the minimal range (end-start) when zooming into a figure
        zoom_out_interval: range in UTC s of the maximal range (end-start) when zooming out of a figure
        x_range_padding: view padding added (extra_pad = (end - start)*x_range_padding) added to the range i.e. %
        time_zone: the time zone for applying a UTC offset in the view
        logger: logger
        """
        super().__init__(logger)
        self.sec_to_milli: float = 1000.0  # Currently we use bokeh timedate formatter, that uses epoch ms resolution
        if zoom_in_interval:
            zoom_in_interval = float(zoom_in_interval)*self.sec_to_milli
        if zoom_out_interval:
            zoom_out_interval = float(zoom_out_interval)*self.sec_to_milli

        self._view_range: UtcPeriod = init_view_range or UtcPeriod(0, 1)  # note range 0,1 _is_ a special range checked for other places..
        self._current_view_range: UtcPeriod = self._view_range  # note: used by the bokeh timer, if it fires, and find something here it triggers update

        self.utc_offset: time = Calendar(time_zone).tz_info.utc_offset(utctime_now()) if time_zone is not None else time(0)
        self.shared_x_range: Range1d = Range1d(start=float(self._view_range.start + self.utc_offset)*self.sec_to_milli,
                                               end=float(self._view_range.end + self.utc_offset)*self.sec_to_milli,
                                               min_interval=zoom_in_interval,
                                               max_interval=zoom_out_interval)
        self.shared_x_range.on_change('end', self.x_range_callback)
        self.x_rang_pad: float = x_range_padding

        # setter without callbacks that we need when we want to update the visual widget with value (no callback-circles)
        self.set_x_range_start: Callable[[Any], None] = update_value_factory(self.shared_x_range, 'start')
        self.set_x_range_end: Callable[[Any], None] = update_value_factory(self.shared_x_range, 'end')

        bokeh_document.add_periodic_callback(self.x_range_data_updater, 100)

    def x_range_callback(self, attrn: str, old: int, new: int) -> None:
        """
        This callback triggers a reload on bokeh figure x-range changes.
        Note that it only set the ._current_view_range that is
        picked up by the timer-driven x_range_data_updater every 100ms

        """
        if self._state == States.ACTIVE:
            self._current_view_range = UtcPeriod(int(round(self.shared_x_range.start/self.sec_to_milli) - self.utc_offset),
                                                 int(round(self.shared_x_range.end/self.sec_to_milli) - self.utc_offset))

    def x_range_data_updater(self) -> None:
        """
        This periodic callback is added to tornado event loop to trigger update of the hole TsViewer machinery
        """
        if self._current_view_range and self._state == States.ACTIVE:
            self._view_range = self._current_view_range
            self._current_view_range = None
            # reset view
            self.trigger_update()

    def set_view_range(self, view_range: UtcPeriod, callback: bool = True, padding: bool = True) -> None:
        """
        This function sets the view period of the view time axis and thus of all adjoint figures

        Parameters
        ----------
        start: start view time point in UTC s
        end: end view time point in UTC s
        callback: trigger update callback or not
        padding: add padding to the view range or not
        """
        if padding:
            extra_pad = (view_range.end - view_range.start)*self.x_rang_pad
        else:
            extra_pad = 0

        self.set_x_range_start(int(round((view_range.start - extra_pad + self.utc_offset)*self.sec_to_milli)))
        self.set_x_range_end(int(round((view_range.end + extra_pad + self.utc_offset)*self.sec_to_milli)))
        self._view_range = UtcPeriod(int(round(self.shared_x_range.start/self.sec_to_milli) - self.utc_offset),
                                     int(round(self.shared_x_range.end/self.sec_to_milli) - self.utc_offset))
        self._current_view_range = self._view_range
        if callback:
            self.trigger_update()


    @property
    def view_range(self) -> UtcPeriod:
        """
        This property returns current view range as shyft.time_series.UtcPeriod
        """
        return self._view_range


class TimePeriodSelectorTableViewTimeAxis(BaseViewTimeAxis):

    def __init__(self,
                 time_period_selector: 'shyft.dashboard.time_series.tools.figure_tools.TimePeriodSelector',
                 logger: Optional['logging.Logger'] = None):
        super().__init__(logger=logger)
        self._view_range: UtcPeriod = UtcPeriod(0, 0)
        self.time_period_selector = time_period_selector
        connect_ports(time_period_selector.send_time_period, self.receive_view_period)

    def set_view_range(self, view_range: UtcPeriod, callback: bool = True, padding: bool = True) -> None:
        """
        This function sets the view period of the view time axis and thus of all adjoint figures

        Parameters
        ----------
        view_range: UtcPeriod of start and end of view range
        callback: trigger update callback or not
        padding: add padding to the view range or not
        """
        self._view_range = view_range
        if callback:
            for callback in self._time_axis_update_callbacks.values():
                callback()

    @property
    def view_range(self) -> UtcPeriod:
        """
        This property returns current view as a shyft.time_series.UtcPeriod
        :return:
        """
        return self._view_range


class TimeAxisHandler(Bindable):
    """
    The TimeAxisHandler object calculates time axis for the current view.
    The time axis handler uses seconds s since epoch in utc.

    It provides two methods to request the current time axes:
        - current view time axis (shyft.time_series.TimeAxis)
        - current data padded time axis (shyft.time_series.TimeAxis), time axis with extra padding to the left and right

    DataSources will use these methods to get the current time axis when they update the data.

    The minimal dt which is reasonable to view on the figures based on the plot_width is applied.

    Time step restrictions can be provided to ensure only certain time steps are chosen (round up/down)

    A dt selector can be connected to the TimeAxisHandler to take user defined dt input.


    """

    def __init__(self, *,
                 auto_dt_multiple: int,
                 view_time_axis: BaseViewTimeAxis,
                 estimate_default_view: Optional[bool] = True,
                 time_step_restrictions: Optional[Union[List[Union[int, float]], np.ndarray]] = None,
                 add_dt_selector: Optional[bool] = True,
                 title: Optional[str] = None,
                 width: int = 130,
                 height: Optional[int] = None,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger: Optional['logging.Logger'] = None,
                 tools: Optional[List[ViewTimeAxisTool]] = None,
                 full_view: Optional[bool] = False,
                 time_zone: Optional[str] = 'Europe/Oslo',
                 historical_mode: Optional[bool] = False) -> None:
        """
        Parameters
        ----------
        auto_dt_multiple: sets the lowest resolution of the time series
        view_time_axis: The bokeh view time axis it should be connected to
        estimate_default_view: switch to allow for changing the default view range
        time_step_restrictions: which time steps should be available
        add_dt_selector: switch to add a time step selector tool
        title: title often passed from TsViewer and is passed to the time step selector tool
        logger: python logger
        tools: list of tools to be added
        full_view: switch to create time axis for the whole data set and not the cropped
        time_zone: not in use
        historical_mode: if set true, fiddle clip time-axis rhs to utctime_now
        ----------
        Notes
        -----
        in _calculate_auto_dt() smallest dt is 1 hour ... this should be changed to 1 s bound by auto_dt_multiple
        """
        super().__init__()
        self.logger = logger

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        self.estimate_default_view: bool = estimate_default_view
        self.default_view_range: UtcPeriod = view_time_axis.view_range

        # false if trimming range to nearest dt that fits the calendar
        self.full_view: bool = full_view

        # TimeAxisHandle all in s
        self.view_time_axis: BaseViewTimeAxis = view_time_axis
        self.view_time_axis.bind(parent=self)

        self.cal: Calendar = Calendar(str(time_zone))  # pass on time-zone to get .. tz semantics hmm.
        self.view_range: UtcPeriod = self.default_view_range
        self.pad = 0
        self.zoom_threshold_factor: float = 1.375
        self.pan_threshold_factor: float = 0.3
        self.padded_view_range: UtcPeriod = self.default_view_range

        # s snap time data to
        self.snap_time_to: time = self.cal.WEEK
        self.dt_restriction: list = sorted(time_step_restrictions) if isinstance(time_step_restrictions,
                                                                                 (list, np.ndarray)) else None
        # dt selector box options
        self.dt_options: List[time] = []

        # for data with half infinite data [ -inf, now] like historical data
        t_now = self.cal.trim(utctime_now(), 3600)
        self.historical_view_range: UtcPeriod = UtcPeriod(t_now - 2*self.cal.WEEK, t_now)
        self.historical_mode: bool = historical_mode

        self._auto_dt_figure_width = None
        self.default_auto_dt_width: int = 600

        self.auto_dt_multiple: time = auto_dt_multiple or self.cal.HOUR
        self.auto_dt = 0

        self.user_selected_dt: time = self.cal.HOUR

        self.time_axes_hist = {}

        self.send_dt_options: Sender = Sender(parent=self, name='send dt options', signal_type=List[int])
        self.receive_dt: Receiver = Receiver(parent=self, name='receive dt', func=self._receive_dt, signal_type=int)

        self._state: States = States.ACTIVE
        self.state_port: StatePorts = StatePorts(parent=self, _receive_state=self._receive_state)
        self.dt_selector: DeltaTSelectorTool = None
        self.dt_view = None
        self.tools: List[DeltaTSelectorTool] = []
        if add_dt_selector:
            self.dt_selector = DeltaTSelectorTool(title=title, width=width, height=height, padding=padding,
                                                  sizing_mode=sizing_mode, logger=self.logger)
            self.dt_selector.bind(parent=self)
            self.tools = [self.dt_selector]
            self.dt_view = self.dt_selector.dt_view

        if tools:
            [self.add_tool(tool) for tool in tools]

    @property
    def auto_dt_figure_width(self) -> float:
        """ """
        if self._auto_dt_figure_width is not None:
            return self._auto_dt_figure_width
        else:
            return self.default_auto_dt_width

    @auto_dt_figure_width.setter
    def auto_dt_figure_width(self, value: int) -> None:
        self._auto_dt_figure_width = value

    # --- INITIALISATION

    def set_default_view_period(self, min_max_range: UtcPeriod, reset_view: bool = True) -> None:
        """
        This function sets the time axis handler to a default view, the one with all data visible
        """
        # TODO check if min_max_range is from min_utctime to max_utctime .. what to do? with estimate_default_view
        if self.estimate_default_view:
            self.default_view_range = min_max_range
        if reset_view:
            self.reset_view()

    def initialize(self, reset_view: bool = True) -> None:  # reset_view
        """
        This function resets the view to its initial range
        """
        view_range_larger_init_range = (self.view_time_axis.view_range.start < self.default_view_range.start and
                                        self.view_time_axis.view_range.end > self.default_view_range.end)
        view_range_outside_init_range = (self.view_time_axis.view_range.start >= self.default_view_range.end or
                                         self.view_time_axis.view_range.end <= self.default_view_range.start)
        first_time_plotting = (self.view_time_axis.view_range.start == 0 and self.view_time_axis.view_range.end == 1)
        if (reset_view or self._state == States.DEACTIVE or view_range_larger_init_range or first_time_plotting or
                view_range_outside_init_range):
            self.set_view_range(self.default_view_range, callback=False)
            self.reset_view()
        self.evaluate_view_range()

    def reset_view(self):  # clear time_axis_handle
        """
        This function resets the time axis handler
        """
        self.padded_view_range = UtcPeriod(min_utctime, min_utctime)
        self.auto_dt = 0
        self.view_range = UtcPeriod(min_utctime, min_utctime)
        self.user_selected_dt = self.cal.HOUR
        self.time_axes_hist = {}
        self.dt_options = []

    def set_figure_width(self, figure_width):
        """
        TODO: .figure_width is NOT used inside this class, check if there is any other use of it(and move/remove it)
        """
        self.figure_width = figure_width

    # --- EVALUATION OF THE VIEW RANGE, DT CALCULATION

    def set_view_range(self, view_range: UtcPeriod, callback=False, padding=True):
        """
        This function sets the actual view period
        """
        if self._state == States.ACTIVE:
            self.view_time_axis.set_view_range(view_range=view_range, callback=callback, padding=padding)

    def trigger_time_axis_update(self):
        """
        This function triggers the update process:
        - updating the view time axis and padded view time axis
        - trigger data update of the TsViewer parent
        """
        self.evaluate_view_range()
        self.parent.trigger_data_update()

    def evaluate_view_range(self):
        """
        This function evaluates the current view range and calculates new data padding.
        """
        if (abs(self.view_range.start - self.view_time_axis.view_range.start) > time(0) or
                abs(self.view_range.end - self.view_time_axis.view_range.end) > time(0)):

            # update view point
            view_start = self.view_time_axis.view_range.start
            view_end = self.view_time_axis.view_range.end
            self.view_range = self.view_time_axis.view_range
            if self.padded_view_range.start == min_utctime or self.padded_view_range.end == max_utctime:
                self.padded_view_range = self.view_range  # 1st time, or reset the padded view

            buffer_left = view_start - self.padded_view_range.start
            buffer_right = self.padded_view_range.end - view_end
            # zooming in
            zoom_threshold = self.zoom_threshold_factor*self.pad
            pan_threshold = self.pan_threshold_factor*self.pad

            # estimate new auto dt
            _auto_dt_new = self._calculate_auto_dt()

            # print(f"Auto dt: old {dt_to_str(self.auto_dt)}, new {dt_to_str(_auto_dt_new)}, tests {_auto_dt_new != self.auto_dt} { abs(_auto_dt_new-self.auto_dt) > 1.e-12}")
            # print(buffer_left > zoom_threshold, buffer_right > zoom_threshold, buffer_left < pan_threshold, buffer_right < pan_threshold, _auto_dt_new != self.auto_dt)

            # check if reloading should be done
            if (buffer_left > zoom_threshold or buffer_right > zoom_threshold or
                    buffer_left < pan_threshold or buffer_right < pan_threshold or
                    _auto_dt_new != self.auto_dt):
                # Update data ranges
                # save the new data range
                # padding left and right at least one week\
                self.pad = max(int(round(view_end - view_start)*2.), self.cal.WEEK)
                self.padded_view_range = UtcPeriod(view_start - self.pad, view_end + self.pad)
                # print("updating the data range {} | {} ".format(dt_to_str(self.current_view_end - self.current_view_start), dt_to_str(self.view_end_padded - self.view_start_padded)))

                # historical data
                t_now = utctime_now()
                self.historical_view_range = UtcPeriod(int(min(self.padded_view_range.start, t_now)),
                                                       int(min(t_now, self.padded_view_range.end)))

                self.time_axes_hist = {}

            # update dt and dt options
            if isinstance(self.dt_restriction, list):
                new_dt_options = sorted([dt for dt in self.dt_restriction
                                         if dt >= _auto_dt_new and dt <= view_end - view_start])
            else:
                new_dt_options = [self.auto_dt]
            if abs(self.auto_dt - _auto_dt_new) > time(0) or set(self.dt_options).symmetric_difference(new_dt_options):
                self.auto_dt = _auto_dt_new
                self.dt_options = new_dt_options
                self.send_dt_options(self.dt_options)

    def _calculate_auto_dt(self) -> int:
        """
        This function estimates the auto dt based on the current view and width of the figure(s)

        Returns
        -------
        a_dt: time step for figure(s) in seconds, if restrictions are set it returns the closest value above
              calculated time step
        """
        if self.view_range.valid() and self.view_range.start != min_utctime and self.view_range.end != max_utctime:
            start = int(round(self.view_range.start))
            stop = int(round(self.view_range.end))
            n_auto_dt_multiple = self.cal.diff_units(start, stop, deltahours(1))
            num_periods = self.auto_dt_figure_width
            h_dt = (deltahours(int(round(n_auto_dt_multiple/num_periods)))//self.auto_dt_multiple)*self.auto_dt_multiple
            a_dt = int(round(max(self.auto_dt_multiple, h_dt)))
        else:
            a_dt = int(deltahours(1))  # no valid dt, just assume  hour
        if isinstance(self.dt_restriction, list):
            a_dt = self.calculate_restriction(a_dt)
        return a_dt

    def calculate_restriction(self, dt: int) -> int:
        """
        This function evaluates the dt from the dt_restrictions

        Parameters
        ----------
        dt: time step

        Returns
        -------
        returns the lowest time step from the time step restrictions list or the inputted time step
        """
        idx = min(np.searchsorted(self.dt_restriction, dt, side="left"), len(self.dt_restriction) - 1)
        return int(self.dt_restriction[idx])

    # ---- TIME AXIS REQUEST METHODS
    @property
    def view_time_axis_properties(self)-> ViewTimeAxisProperties:
        """
        :return: parameters that describe the current view-port time-axis
        """
        dt = max([self.auto_dt, self.user_selected_dt])
        if isinstance(self.dt_restriction, list):
            dt = self.calculate_restriction(dt)

        return ViewTimeAxisProperties(dt=dt, cal=self.cal, view_period= self.view_range, padded_view_period=self.padded_view_range,extend_mode=self.full_view)


    # --- EXTERNAL CONTROL/ TOOLS

    def _receive_dt(self, dt: int) -> None:
        """
        This port function receives a user defined dt usually used in connection with the dt selector
        """
        dt = self.auto_dt_multiple*(dt//self.auto_dt_multiple)
        self.user_selected_dt = max(self.auto_dt_multiple, dt)
        # update figure after dt was received
        if self.bound:
            self.parent.trigger_data_update()

    def add_tool(self, tool: ViewTimeAxisTool) -> None:
        """
        This function adds a ViewTimeAxisTool to the axes handler
        """
        if not isinstance(tool, ViewTimeAxisTool):
            raise TimeAxisHandlerError(f"TimeAxisHandler {self}: tool {tool} not of type ViewTimeAxisTool")
        if tool not in self.tools:
            tool.bind(parent=self)
            self.tools.append(tool)

    # --- STATE
    def _receive_state(self, state: States) -> None:
        """
        This function sets the object into the received state
        """
        if state == self._state:
            return
        self._state = state
        if state == States.DEACTIVE:
            self.state_port.send_state(state)
        elif state == States.LOADING or state == States.READY:
            self._state = States.ACTIVE
        elif state == States.ACTIVE:
            # notify all underlying tools etc. that we are active now!
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)
