from typing import List, Optional, Dict, Union

from shyft.dashboard.time_series.view_time_axes import ViewTimeAxisProperties, create_view_time_axis, extend_time_axis
from shyft.time_series import UtcPeriod, min_utctime, max_utctime, TimeAxis, TsVector, utctime_now, time
import logging
from functools import partial
from concurrent.futures import ThreadPoolExecutor

from bokeh.document import Document, without_document_lock
from tornado import gen

from shyft.dashboard.base.ports import States
from shyft.dashboard.time_series.bindable import Bindable
from shyft.dashboard.time_series.view import BaseView
from shyft.dashboard.time_series.sources.ts_adapter import TsAdapter
from shyft.dashboard.base.hashable import Hashable
from shyft.dashboard.time_series.axes_handler import DsViewTimeAxisType
from shyft.dashboard.time_series.state import Unit, Quantity, UnitRegistry


class DataSource(Hashable, Bindable):
    """
    This (not entirely enforced) immutable hashable object contains all data defining a source for requesting data.

    It is typically used related to the view, ref to the class Source below,
    as means of keeping parameters that help getting ts-data in an optimal manner for renderers.


    Attributes
    ----------

    ts_adapter: TsAdapter is the most important feature, its role is to provide the time-series data
                 from the underlying system.

                 It's a callable object of type:

                    fx( time_axis: TimeAxis, unit: Unit) -> Quantity[TsVector]:

                 and as indicated, given a time-axis and a unit, provide a Quantity[TsVector].
                 The TsVector having 1 or more members, depending on the wanted ts-renderer (percentile/fill-between or line/scatter-plots)

                 It is invoked by the view-controller each time it needs (new) data for rendering.


    min_dt: time >=0 the smallest time-step to propagate through requests to the ts_adapter
             the purpose is to let the user instrument this data-source so that it will
             never ask for time-axis of less resolution than this.
             Typically, it's reasonable to set 3600 for ts-expressions where you know that the underlying data
             is sampled at hourly resolution.
             Note that is only for optimizing memory/time usage.

    time_range: UtcPeriod clipping period, default min..max, that is, -> no clip/crop
             the purpose is to let you clip the request,
              and maybe also the returned resulting ts-vector from
             the ts_adapter.

    request_time_axis_type: DsViewTimeAxisType (padded/not padded)
             the purpose is to let user control which of the time-axis provided by the view-controller should be used
             for fetching data through .ts_adapter(....) call.
             The padded time-axis contains surplus ranges at each end of the time-axis to allow for smooth pan-operations.

    tag :str the short-name of the data-source
             the purpose..? have named data-sources.


    """

    def __init__(self, *,
                 ts_adapter: TsAdapter,
                 unit: str,
                 min_dt: Optional['shyft.time_series.time'] = 0,
                 time_range: Optional[UtcPeriod] = None,
                 request_time_axis_type: Optional[DsViewTimeAxisType] = None,
                 tag: Optional[str] = None) -> None:
        """
        Parameters
        ----------
        ts_adapter:
            the TsAdapter which has the data
        unit:
            the unit of the data
        min_dt:
            the smallest time step to use when constructing time-axis used for the .ts_adapter(time_axis..) request.
        time_range:
            the maximum time range for the data, used to clip request, in or outgoing to the ts_adapter(.... ) request.
        request_time_axis_type:
            time axis type (padded/not padded), controls which of the time-axis to use for the .ts_adapter(...) request.
        tag:
            tag(short-name) of data source
        """
        Hashable.__init__(self)
        Bindable.__init__(self)

        self.tag: str = tag or f'ds {self.uid}'
        self.unit: str = unit
        self.min_dt: time = min_dt
        self.time_range: UtcPeriod = time_range or UtcPeriod(min_utctime, max_utctime)
        self.request_time_axis_type: DsViewTimeAxisType = request_time_axis_type or DsViewTimeAxisType.padded_view_time_axis

        if not isinstance(ts_adapter, TsAdapter):
            raise (ValueError(f'Error Source {tag} ts_adapter {ts_adapter} not of type TsAdapter'))
        self.ts_adapter: TsAdapter = ts_adapter


class TsAdapterRequestParameter(Hashable):
    """
    This immutable hashable object contains all information to request data from TimeAxisHandle
    and we use it as message-transport between the front thread and the background worker-thread
    that performs the real work in an async context(strongly recommended)

    Ref. to DataSource for the semantics of the data-members

    """

    def __init__(self, *, request_time_axis_type: DsViewTimeAxisType, unit: Unit, view_time_axis: TimeAxis,
                 padded_view_time_axis: TimeAxis) -> None:
        """
        This object bundles all parameter needed to get data from ts_adapter

        Parameters
        ----------
        request_time_axis_type:
            defines which time axis to use view_time_axis or padded_view_time_axis
        unit:
            unit of the requested data
        view_time_axis:
            view time axis provided from time_axis_handle
        padded_view_time_axis:
            padded view time axis provided from time_axis_handle
        """
        super().__init__()
        self.request_time_axis_type: DsViewTimeAxisType = request_time_axis_type
        self.unit: Unit = unit
        self.view_time_axis: TimeAxis = view_time_axis
        self.padded_view_time_axis: TimeAxis = padded_view_time_axis

    @classmethod
    def create_empty(cls) -> 'TsAdapterRequestParameter':
        return cls(request_time_axis_type=None, unit=None, view_time_axis=None, padded_view_time_axis=None)

    @property
    def is_empty(self):
        return (self.view_time_axis is None or self.unit is None or self.request_time_axis_type is None
                or self.padded_view_time_axis is None)

    def is_equiv(self, other):
        if not isinstance(other, TsAdapterRequestParameter):
            return False
        if not self.request_time_axis_type == other.request_time_axis_type:
            return False
        try:
            rqta = self.request_time_axis
        except RuntimeError:
            return False
        try:
            other_rqta = other.request_time_axis
        except RuntimeError:
            return False
        if not rqta == other_rqta:
            return False
        if not self.unit == other.unit:
            return False
        return True

    @property
    def request_time_axis(self) -> TimeAxis:
        if self.request_time_axis_type == DsViewTimeAxisType.view_time_axis:
            ta = self.view_time_axis
        elif self.request_time_axis_type == DsViewTimeAxisType.padded_view_time_axis:
            ta = self.padded_view_time_axis
        else:
            raise RuntimeError(f"TsAdapterRequestParameter {self.uid} unknown request_time_axis_type={self.request_time_axis_type}")
        return ta

    @property
    def request_parameter(self) -> Dict[str, Union[Unit, TimeAxis]]:
        return {'time_axis': self.request_time_axis, 'unit': self.unit}


class SourceError(RuntimeError):
    pass


class Source(Bindable):
    """
    This object plays the role of binding a DataSource (ref DataSource) to
    a set of Views, based on controls from the .parent (bindable) that need to provide
    TsViewer capabilities.

    It utilizes a *thread-pool* to ensure that time-consuming data-fetching/computations can
    run in the *background thread*, and that when ready, these are *properly dispatched* into the bokeh
    foreground async io-loop.

    Notice that this class plays together (closely) with the TsViewer class that have
    several Sources that is renders.

    The TsViewer is reached through the .parent (from Bindable) member.

    Control flow for an update goes like this:

    From the TsViewer           This class        The background worker(thread-pool)          TsAdapter
    .update_data(vw_parms) ->     |                        |                                    |
                           compute
                          time-axis suitable for the current view,
                           given  source.min_dt,source.time_range(alias clip)
                                  |                        |
                                   post the TsReq  -->     |                                    |
                                  |                  request_data_from_ts_adapter_sync ()      fx(time_axis,unit)->TsVector
                                  |                        |
                               update_view_data(tsv..) <--- TsVector
    .trigger_view_update(views:tsv)


    Attributes
    ----------
    logger:Logger
        provides logging functionality
    data_source: DataSource
        provide means of getting time-series data from the data-layer, with time-axis/delta-t  limitations, does not have any logic.
    views: List[BaseView]
        keeps the list of view that presents this source
    unit_reqistry: UnitRegistry
        keeps the measurement-units and methods for conversions so that we can do simple conversions at
        the visual/presentation layer
    visible: bool
        True if this datasource should be visible
    _state: States
        represent the port/visual state of this object
    bokeh_document: Document
        the document we renter into (we use async, so we need to keep track of it)
    async_on: bool
        True if thread-pool executer is supplied (can be turned off)
    queue: List[TsAdapterRequestParameter]
        Keeps the list of pending request (async) fetching data
    current_request_parameter: TsAdapterRequestParameter
        Keeps the ongoing request (so that other similar request can be skipped)
    loading_data_async: bool
         True while the async-thread worker is executing in background
    async_observer_ts_viewer: TsViewer
        the TsViewer that registers itself as the observer of this Source. This is needed if trigger_view_update()
        should wait for results from all async data updates in its sources.
    """

    def __init__(self, bokeh_document: Document,
                 data_source: DataSource,
                 views: List[BaseView],
                 unit_registry: UnitRegistry,
                 thread_pool_executor: Optional[ThreadPoolExecutor] = None,
                 logger: Optional['logging.Logger'] = None):
        """
        Parameters
        ----------
        bokeh_document:
            bokeh document
        data_source:
            data source
        views:
            views to updated after data was loaded
        unit_registry:
            unit registry use to check units
        thread_pool_executor:
            thread pool executor needed for async data loading, if provided source will use it
        """
        super().__init__()

        self.logger = logger or logging.getLogger()
        self.do_log: bool = self.logger.isEnabledFor(logging.DEBUG)
        self.data_source: DataSource = data_source
        self.views: List[BaseView] = views
        self.unit_registry: UnitRegistry = unit_registry

        self.visible: bool = True
        self._state: States = States.ACTIVE

        self.bokeh_document: Document = bokeh_document

        self.async_on: bool = thread_pool_executor is not None
        self.thread_pool_executor: ThreadPoolExecutor = thread_pool_executor
        self.queue: List[TsAdapterRequestParameter] = []
        self.current_request_parameter: TsAdapterRequestParameter = TsAdapterRequestParameter.create_empty()
        self.loading_data_async: bool = False

        self.async_observer_ts_viewer = None

    def _make_request_parameter(self,view_axis:ViewTimeAxisProperties)->TsAdapterRequestParameter:
        """
        based on the view_axis properties, and self.min_dt and .time_range, compute reasonable time-axis,
        using the create_view_time_axis function.
        :return a ts-adapter-request-parameter that is filled in ready for execution
        """
        dt = max([self.data_source.min_dt, view_axis.dt])
        view_ta = create_view_time_axis(cal=view_axis.cal, view_period=view_axis.view_period, clip_period=self.data_source.time_range, dt=dt)
        padded_ta = create_view_time_axis(cal=view_axis.cal, view_period=view_axis.padded_view_period, clip_period=self.data_source.time_range, dt=dt)
        if view_axis.extend_mode:  # funny that this have to be set on the TsViewer, it could.. be on the view-list..
            view_ta = extend_time_axis(ta=view_ta, p=self.data_source.time_range)
            padded_ta = extend_time_axis(ta=padded_ta, p=self.data_source.time_range)
        return TsAdapterRequestParameter(unit=self.data_source.unit, view_time_axis=view_ta,
                                                  padded_view_time_axis=padded_ta,
                                                  request_time_axis_type=self.data_source.request_time_axis_type)

    def update_data(self, view_axis:ViewTimeAxisProperties) -> None:
        """
        This function triggers the updating of the data using the ts adapter provided in data_source container.
        It is called by the controller(TsViewer):

        It goes through these steps:
          * Create suitable time-axis/parameters to forward to the ts-adapter for getting data
             (try to figure out minimum amount of work to be done)
          * In thread-pool thread, execute the ts-adapter to get the data
          * when done, invoke the update_view_data(..) to update the TsViewer with the results.

        :parameter view_axis Contains the properties of the visual-time-axis, so that this class can
                   adapt and optimize it's request to the TsAdapter class.
        """
        if self._state == States.ACTIVE and self.visible:
            try:
                request_param =  self._make_request_parameter(view_axis)
                #  check if time axes out of view
                if not request_param.request_time_axis:
                    self._empty_time_axis()
                    return
                if self.current_request_parameter.is_equiv(request_param):
                    return
                else:
                    self._update(request_param=request_param)
            except RuntimeError as e:
                self._empty_time_axis()
                self.logger.error(f"Error {self.__class__.__name__} {self.data_source.tag}: {e}", exc_info=True)

    def _update(self,*, request_param:TsAdapterRequestParameter)->None:
        self.queue = [request_param]
        if self.async_on and not self.loading_data_async:
            if self.current_request_parameter.is_empty:
                self.current_request_parameter = request_param
            try:
                if self.async_observer_ts_viewer:
                    self.async_observer_ts_viewer.source_starting_async_data_update(self)
                self.bokeh_document.add_next_tick_callback(self._request_data_from_ts_adapter_async)
                self.loading_data_async = True
            except Exception as e:
                self.logger.error(f"{self.__class__.__name__} {self.data_source.tag}, Exception {e}")
                self._empty_time_axis()
        elif not self.async_on:
            self.current_request_parameter = request_param
            self._request_data_from_ts_adapter_sync(request_param=request_param)

    def _empty_time_axis(self) -> None:
        """
        This function is used when the requested time axis is empty or out of range
        ... AND it fires an update to the observer (parent)
        """
        self.current_request_parameter = TsAdapterRequestParameter.create_empty()
        self.queue = []
        self.update_view_data(ts_vector=self.unit_registry.Quantity(TsVector(), self.data_source.unit))

    def _request_data_from_ts_adapter_sync(self, *, request_param: TsAdapterRequestParameter):
        """
        This function requests the data sync
        """
        if self.do_log:
            self.logger.debug(f"{self.__class__.__name__} {self.data_source.tag} requesting data for {request_param.request_time_axis}")
            timestamp = utctime_now()
        ts_vector = self.data_source.ts_adapter(**request_param.request_parameter)
        for ts in ts_vector:
            if ts.needs_bind():
                raise SourceError(f"TimeSeries {ts} is not bound")

        if self.do_log:
            self.logger.debug(f"{self.__class__.__name__} {self.data_source.tag} received data after {utctime_now() - timestamp}")
        self.update_view_data(ts_vector=ts_vector)

    def request_data_from_ts_adapter_sync(self, *, request_param: TsAdapterRequestParameter):
        if self._state == States.ACTIVE and self.visible:
            self._update(request_param=request_param)

    def update_view_data(self, ts_vector: Quantity[TsVector]) -> None:
        """
        This function triggers the view data update for the ts_vector,
        for each of the views (as a dict), same ts_vector.
        Before return, async_observer_ts_viewer must be notified about completed_async_data_update
        """
        if not self.bound:
            if self.async_observer_ts_viewer:
                self.async_observer_ts_viewer.source_completed_async_data_update(self)
            return
        # check if unit annotated ts vector
        reset_ts_vector = False
        if not isinstance(ts_vector, self.unit_registry.Quantity):
            msg = f"Error {self.__class__.__name__} {self.data_source.tag} ts_vector not annotated with unit" \
                  f" or in viewer unit registry"
            self.logger.error(msg)
            reset_ts_vector = True
        elif not isinstance(ts_vector.magnitude, TsVector):
            self.logger.error(f"Error {self.__class__.__name__} {self.data_source.tag} received magnitude not of type TsVector")
            reset_ts_vector = True
        if reset_ts_vector:
            ts_vector = self.unit_registry.Quantity(TsVector(), self.data_source.unit)
        view_data = {view: ts_vector for view in self.views}
        self.parent.trigger_view_update(view_data)
        if self.async_observer_ts_viewer:
            self.async_observer_ts_viewer.source_completed_async_data_update(self)

    # -- ASYNC

    # @without_document_lock
    # SIH: This one is absolutely unclear, in 2.4 it does not work, in 2.3 it works without
    #  so we need to figure out if we need this. Since this is NOT a doc, there is no requirement
    #  to try to lock it, however, methods called from this(after retrieve data) is
    #  could be docs, but then we must assume they either have, or will take a lock prior to doc change?
    @gen.coroutine
    def _request_data_from_ts_adapter_async(self):
        """
        This function request data from ts_adapter in async way.
        async_observer_ts_viewer must be notified about starting_ and completed_async_data_updates.
        """
        if self.do_log:  # avoid overhead if no debug output
            self.logger.debug(f"{self.__class__.__name__} {self.data_source.tag} requesting data", extra=dict(async_on=True))
            ts = utctime_now()

        if not self.queue:
            self.loading_data_async = False
            if self.async_observer_ts_viewer:
                self.async_observer_ts_viewer.source_completed_async_data_update(self)
            return
        self.loading_data_async = True
        request_param = self.queue.pop(0)
        self.current_request_parameter = request_param
        future_name = self.data_source.uid
        future = self.thread_pool_executor.submit(self.data_source.ts_adapter, **request_param.request_parameter)
        try:
            # use yield fr tornado to not add a blocking wait as #self.future.result(timeout=25) would do
            results = yield future  # we resume execution here, in the bokeh-main-thread, when thread-pool executor is done.
        except (RuntimeError, TypeError, ValueError, AttributeError, ArithmeticError) as e:
            self.logger.error(f"{self.__class__.__name__} {self.data_source.tag} ts_adapter: Exception {e}", exc_info=True, extra=dict(async_on=True))
            # self.bokeh_document.add_next_tick_callback(self.empty_time_axis)  # not wanted, but possible
            results = None
        if self.do_log:
            self.logger.debug(f"{self.__class__.__name__} {self.data_source.tag} received data after {utctime_now() - ts}", extra=dict(async_on=True))
        if self.queue:
            next_request_param = self.queue[0]
            self.current_request_parameter = next_request_param
            if self.async_observer_ts_viewer:
                self.async_observer_ts_viewer.source_starting_async_data_update(self)
            self.bokeh_document.add_next_tick_callback(self._request_data_from_ts_adapter_async)
        else:
            self.loading_data_async = False
        if results and self._state == States.ACTIVE and future_name == self.data_source.uid:
            try:
                self.bokeh_document.add_next_tick_callback(partial(self.update_view_data_async, ts_vector=results))
            except Exception as e:
                self.logger.error(f"{self.__class__.__name__} {self.data_source.tag}, {self.bokeh_document}, Exception {e}", exc_info=True, extra=dict(async_on=True))
                if self.async_observer_ts_viewer:
                    self.async_observer_ts_viewer.source_completed_async_data_update(self)
        elif self.async_observer_ts_viewer:
            self.async_observer_ts_viewer.source_completed_async_data_update(self)

    @gen.coroutine
    def update_view_data_async(self, ts_vector: TsVector) -> None:
        """
        Trigger the view data update, from async function
        """
        self.update_view_data(ts_vector=ts_vector)
