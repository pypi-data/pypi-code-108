from typing import List, Optional, Dict, Union, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import bokeh
from bokeh.layouts import row, column
from pint import UnitRegistry, UndefinedUnitError

from shyft.time_series import UtcPeriod, TimeAxis, min_utctime, max_utctime, TsVector

from shyft.dashboard.base import constants
from shyft.dashboard.base.ports import (Receiver, StatePorts, States, connect_state_ports, connect_ports)

from shyft.dashboard.time_series.ds_view_handle import DsViewHandle
from shyft.dashboard.time_series.view import BaseView
from shyft.dashboard.time_series.state import State
from shyft.dashboard.time_series.sources.source import DataSource, Source
from shyft.dashboard.time_series.state import Quantity
from shyft.dashboard.time_series.axes_handler import TimeAxisHandler, BokehViewTimeAxis
from shyft.dashboard.time_series.view_container.view_container_base import BaseViewContainer
from shyft.dashboard.time_series.view_container.figure import Figure
from shyft.dashboard.time_series.bindable import BindableError
from shyft.dashboard.time_series.tools.ts_viewer_tools import TsViewerTool
from shyft.dashboard.time_series.tools.view_time_axis_tools import ViewTimeAxisTool


class TsViewerError(RuntimeError):
    pass


class TsViewer:
    """
    TsViewer class is the main class combining all components to
    view time series in bokeh.

    Different ViewContainer (As figures, tables) can be added to
    the viewer.

    Examples
    --------
    |     # create our viewer app
    |     viewer = TsViewer()
    |
    |     # create view container
    |     table1 = Table(viewer=viewer)
    |     fig1 = Figure(viewer=viewer)

    All view container will be bound to the same time axis, controlled
    by a TimeAxisHandler. (i.e. linked x axis of all figures)


    To view time series data one need to define the data or how it
    can be retrieved with a DataSource.
    In addition one need to define the View(s), i.e. how the data should
    be visualised in the different ViewContainer.
    For convenience, book-keeping and easy messaging between apps is the
    combination of a DataSource and a List[Views] defined as an ds_view_handle.

    Examples (continued)
    --------------------

    |     # define data source
    |     data_source = DataSource(ts_adapter="TsAdapter", unit='MW')
    |     # define views
    |     percentile_view = PercentileView(view_container_uid=fig1.uid)
    |     table_view = TableView(view_container_uid=table1.uid)
    |
    |     # add it to the viewer
    |     ds_view_handle = viewer.create_ds_view_handle(data_source=data_source,
    |                                 views=[percentile_view, table_view])
    |     # OR create an ds_view_handle and add it to the viewer
    |     dsviehandle = DsViewHandle(data_source=data_source,
    |                   views=[percentile_view, table_view])
    |     viewer.add_ds_view_handle(ds_view_handle)
    |     # OR send it using the port function (takes a List[DsViewHandles])
    |     viewer.receive_ds_view_handles_to_add([ds_view_handle])
    |
    |     # the ds_view_handle can be removed by
    |
    |     viewer.remove_ds_view_handle(ds_view_handle)
    |     # OR using the port function (takes a List[DsViewHandles])
    |     viewer.receive_ds_view_handles_to_remove([ds_view_handle])
    """

    def __init__(self, *,
                 bokeh_document: 'bokeh.document.Document',
                 title: Optional[str] = '',
                 state: Optional[States] = States.ACTIVE,
                 width: Optional[int] = 150,
                 height: Optional[int] = None,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 time_step_restrictions: Optional[Union[List[Union[int, float]], np.ndarray]] = None,
                 zoom_in_interval: Optional[Union[int, float]] = None,
                 zoom_out_interval: Optional[Union[int, float]] = None,
                 init_view_range: UtcPeriod = None,
                 auto_dt_multiple: Optional[int] = None,
                 thread_pool_executor: Optional[ThreadPoolExecutor] = None,
                 add_dt_selector: bool = True,
                 logger: Optional['logging.Logger'] = None,
                 unit_registry: Optional[UnitRegistry] = None,
                 tools: List[TsViewerTool] = None,
                 time_zone: Optional[str] = None,
                 reset_time_axis: bool = True,
                 full_view: bool = True,
                 should_wait_async_view_data: bool = False) -> None:
        """
        Parameters
        ----------
        bokeh_document:
            the bokeh document it belongs to
        title:
            title of the app
        time_step_restrictions:
            list of time step restrictions
        zoom_in_interval:
            the minimum visible interval
        zoom_out_interval:
            the maximum visible interval
        init_view_range:
            the period which should be the default period
        auto_dt_multiple:
            sets the lowest resolution of the time series
        thread_pool_executor:
            the thread pool executor used for async requests
        add_dt_selector:
            switch to add a time step selector tool
        logger:
            python logger
        unit_registry:
            the unit registry used in the app
        tools:
            list of tools to be part of the TsViewer
        state:
            the initial state
        full_view:
            if set to true, the time-series are *not* clipped to t_now (should be the default!)
        """

        self.width: int = width

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        self.logger = logger or logging.getLogger()
        self.time_zone: str = time_zone or 'UTC'

        self.unit_registry: UnitRegistry = unit_registry or State.unit_registry
        self.thread_pool_executor: ThreadPoolExecutor = thread_pool_executor

        self.view_container: List[BaseViewContainer] = []
        self.ds_view_handles: List[DsViewHandle] = []

        self.sources: Dict[DataSource, Source] = {}
        self.bokeh_document = bokeh_document

        self.view_time_axis: BokehViewTimeAxis = BokehViewTimeAxis(bokeh_document=bokeh_document, init_view_range=init_view_range,
                                                zoom_in_interval=zoom_in_interval,
                                                zoom_out_interval=zoom_out_interval,
                                                time_zone=self.time_zone,
                                                logger=logger)
        self.estimate_default_view_range: UtcPeriod = init_view_range is None
        self.reset_time_axis:bool = reset_time_axis
        time_axis_tools = []
        self.tools: List[ViewTimeAxisTool] = []
        if tools:
            for tool in tools:
                if isinstance(tool, ViewTimeAxisTool):
                    time_axis_tools.append(tool)
                else:
                    self.add_tool(tool)

        self.time_axis_handler:TimeAxisHandler = TimeAxisHandler(view_time_axis=self.view_time_axis,
                                                 estimate_default_view=self.estimate_default_view_range,
                                                 time_step_restrictions=time_step_restrictions,
                                                 auto_dt_multiple=auto_dt_multiple,
                                                 add_dt_selector=add_dt_selector,
                                                 title=title,
                                                 width=width,
                                                 height=height,
                                                 padding=padding,
                                                 sizing_mode=sizing_mode,
                                                 tools=time_axis_tools,
                                                 logger=logger,
												 time_zone=self.time_zone,
                                                 full_view=full_view)
        self.time_axis_handler.bind(parent=self)

        self.receive_ds_view_handles_to_add: Receiver = Receiver(parent=self, name="Receive List[DsViewHandles] to add",
                                                       signal_type=List[DsViewHandle],
                                                       func=self.add_ds_view_handles)
        self.receive_ds_view_handles_to_remove: Receiver = Receiver(parent=self, name="Receive List[DsViewHandles] to remove",
                                                          signal_type=List[DsViewHandle],
                                                          func=self.remove_ds_view_handles)

        self.state_port: StatePorts = StatePorts(parent=self, _receive_state=self._receive_state)
        self._state: States = state

        self.dt_view = self.time_axis_handler.dt_view

        # connect ports
        connect_state_ports(self.state_port, self.view_time_axis.state_port)
        connect_state_ports(self.state_port, self.time_axis_handler.state_port)

        self.generated_layout = None

        # deactivate all states after init
        self.state_port.receive_state(state)

        # True if view updates are to be made once per container, after all sources update their data asynchronously
        self.should_wait_async_view_data = should_wait_async_view_data
        self.sources_async_data_update_running: list[Source] = []
        self.collected_async_view_data: Dict[BaseView, Quantity[TsVector]] = {}

    @property
    def layout(self) -> Optional[bokeh.layouts.column]:
        return self.dt_view.layout

    # --- MAIN METHODS
    def init_view_range(self, intersection: bool = False) -> None:
        """
        This function intializes the view range
        """
        if self.estimate_default_view_range:
            min_func = min
            max_func = max
            total_data_range = UtcPeriod(max_utctime, min_utctime)

            if intersection:
                min_func = max
                max_func = min
                total_data_range = UtcPeriod(min_utctime, max_utctime)

            for ds_view_handle in self.ds_view_handles:
                tr = ds_view_handle.data_source.time_range
                if tr.start != min_utctime:
                    total_data_range.start = min_func(total_data_range.start, tr.start)
                if tr.end != max_utctime:
                    total_data_range.end = max_func(total_data_range.end, tr.end)

            if total_data_range.valid():
                self.time_axis_handler.set_default_view_period(total_data_range, reset_view=self.reset_time_axis)
            else:
                self._state = States.DEACTIVE
                self.state_port.send_state(self._state)

    def plot(self, reset_time_axis: bool = True) -> None:
        """
        This function triggers the plotting of views
        """
        if self._state == States.DEACTIVE:
            return
        if reset_time_axis:
            self.time_axis_handler.initialize(reset_view=reset_time_axis)

        for view_container in self.view_container:
            if isinstance(view_container, Figure):
                # update y range now
                view_container.update_y_range()
                # update y range next time data is coming
                view_container.next_new_data_update_y_range()
        self.trigger_data_update()

    def clear(self) -> None:
        """
        This function clears all views, view contianer etc.
        """
        if self._state == States.ACTIVE:
            self.state_port.send_state(States.DEACTIVE)
            self._state = States.DEACTIVE
        # TODO implement

    def trigger_data_update(self) -> None:
        """
        This function triggers the reloading of the sources with data,
        each source is requested for data
        currently that will result in a call to the function above,
         request_time_axis(min_dt, data_time_range) to get back
         a time-axis that is fitted to the current view-range and auto/dt selection
                                    .. and the particular data-source limitations min_dt, and data_time_range.
        (possibly in background thread)
        and when done they will eventually call
        the trigger_view_update(...) with the new data.

        TODO: consider passing the current view_range, cal,delta-t .. that is: the view-timeaxis(padded or not)
              *down* to the source so that it can make it's own choices.
              That helps a lot..

        """
        vp = self.time_axis_handler.view_time_axis_properties
        for source in self.sources.values():
            if self.should_wait_async_view_data:
                source.async_observer_ts_viewer = self
            source.update_data(view_axis=vp)

    def source_starting_async_data_update(self, source: Source):
        """
        This function must be called by the source before starting an asynchronous data update operation.
        """
        if self.should_wait_async_view_data:
            self.sources_async_data_update_running.append(source)

    def source_completed_async_data_update(self, source: Source):
        """
        This function must be called by the source after its asynchronous data update.
        """
        if source in self.sources_async_data_update_running:
            self.sources_async_data_update_running.remove(source)
        if self.should_wait_async_view_data and len(self.sources_async_data_update_running) == 0:
            for container_i, view_data_i in self.collected_async_view_data.items():
                if view_data_i:
                    container_i.update_view_data(view_data=view_data_i)
                    self.collected_async_view_data[container_i] = {}

    def trigger_view_update(self, view_data: Dict[BaseView, Quantity[TsVector]]) -> None:
        """
        This function triggers the updating of the views, with given data,
        it's usually called by the data-sources when they are finished
        extracting data from the TsAdapters.

        This function merely dispatches the received values
        to the view-containers that performs the presentation.

        """
        container = {c: {} for c in self.view_container}
        for view, data in view_data.items():
            view_container = view.view_container
            if view_container not in self.view_container:
                continue
            container[view_container][view] = data
            if self.should_wait_async_view_data and view_container in self.collected_async_view_data:
                self.collected_async_view_data[view_container][view] = data

        if not self.should_wait_async_view_data:
            for container_i, view_data_i in container.items():
                if view_data_i:
                    container_i.update_view_data(view_data=view_data_i)

    # --- VIEW CONTAINERS

    def add_view_container(self, view_container: BaseViewContainer) -> None:
        """
        This functions adds a view container to the TsViewer and assignes an uid to
        the view container

        Raises
        ------
        BindableError if view container is already bound to a TsViewer
        """
        # check if view container is unbound
        if view_container.bound:
            raise BindableError(f"View container {view_container} is already bound to a ts viewer")
        view_container.bind(parent=self)
        view_container.set_unit_registry(unit_registry=self.unit_registry)
        self.view_container.append(view_container)
        if self.should_wait_async_view_data:
            self.collected_async_view_data[view_container] = {}
        if isinstance(view_container, Figure):
            if self.time_axis_handler.auto_dt_figure_width == self.time_axis_handler.default_auto_dt_width:
                self.time_axis_handler.auto_dt_figure_width = view_container.figure_width
            else:
                self.time_axis_handler.auto_dt_figure_width = min([self.time_axis_handler.auto_dt_figure_width,
                                                                   view_container.figure_width])
        # connect state ports
        connect_state_ports(self.state_port, view_container.state_port)

    def remove_view_container(self, view_container: BaseViewContainer) -> None:
        """
        This functions removes a view container from the TsViewer.

        Raises
        ------
        BindableError if view container is is not bound to the TsViewer
        """
        if view_container.parent != self:
            raise BindableError(f"View container {view_container} is not bound to this ts viewer")
        view_container.unbind()
        if view_container in self.view_container:
            self.view_container.remove(view_container)
        else:
            raise BindableError(f"View container {view_container} is not found in the ts viewer")
        if view_container in self.collected_async_view_data:
            self.collected_async_view_data.pop(view_container)

    def connect_to_dt_selector(self, receive_dt: Receiver) -> None:
        """
        This function connects the a receiver port to receive the current dt to the
        dt selector box if available.
        """
        if self.time_axis_handler.dt_selector:
            connect_ports(self.time_axis_handler.dt_selector.dt_select.send_dt, receive_dt)

    # --- ACTORS

    def add_ds_view_handles(self, ds_view_handles: List[DsViewHandle]) -> None:
        """
        This function add new ds_view_handles to the TsViewer

        Parameters
        ----------
        ds_view_handles:
            ds_view_handles defining data source and views of the data
        """
        for ds_view_handle in ds_view_handles:
            if ds_view_handle in self.ds_view_handles:
                raise TsViewerError(f"Error DsViewHandle {ds_view_handle} already added in TsViewer")
            # 0. Check if unit compatible with unit registry
            try:
                self.unit_registry.Unit(ds_view_handle.data_source.unit)
            except UndefinedUnitError as u:
                raise TsViewerError(f"{ds_view_handle}: Incompatible units!: {u}")

            # 1. add all views of the ds_view_handle to view container
            for view in ds_view_handle.views:
                if view.view_container not in self.view_container:
                    raise TsViewerError(f"Error Cannot add ds_view_handle {ds_view_handle}:" +
                                        f"Unknown view container uid {view.uid} of view {view}")
                view.view_container.add_view(view=view)

            # 2. add source of ds_view_handle
            if ds_view_handle.data_source not in self.sources:
                s = Source(bokeh_document=self.bokeh_document, data_source=ds_view_handle.data_source,
                           views=ds_view_handle.views, thread_pool_executor=self.thread_pool_executor,
                           unit_registry=self.unit_registry, logger=self.logger)
                s.bind(parent=self)
                self.sources[ds_view_handle.data_source] = s
            else:
                # TODO: decide what to do here
                raise TsViewerError(f"Error Cannot add ds_view_handle {ds_view_handle}: Source already registered")
                # self.sources[actor.data_source].extend_views(views=actor.views)
            # 3. #add ds_view_handle
            self.ds_view_handles.append(ds_view_handle)

        # 4. refresh plots
        self.init_view_range()
        self.plot(reset_time_axis=self.reset_time_axis)

    def remove_ds_view_handles(self, ds_view_handles: List[DsViewHandle]) -> None:
        """
        This function remove ds_view_handles from the TsViewer

        Parameters
        ----------
        ds_view_handles:
            ds_view_handles defining data source and views of the data
        """

        container_view_map = {}
        for ds_view_handle in ds_view_handles:
            if ds_view_handle not in self.ds_view_handles:
                self.logger.debug(f"WARNING: Cannot remove unknown DsViewHandle {ds_view_handle.tag}{ds_view_handle}")
                continue
            # 1. find all views per container to remove
            for view in ds_view_handle.views:
                vc = view.view_container
                if vc not in container_view_map:
                    container_view_map[vc] = [view]
                else:
                    container_view_map[vc].append(view)
            # 2. remove  source of ds_view_handle
            source = self.sources.pop(ds_view_handle.data_source)
            source.unbind()
            # 3. remove ds_view_handle
            self.ds_view_handles.remove(ds_view_handle)
        # 4. clear all view container
        for view_container, views in container_view_map.items():
            view_container.clear_views(specific_views=views)
            if self.should_wait_async_view_data and view_container in self.collected_async_view_data:
                for view in views:
                    if view in self.collected_async_view_data[view_container]:
                        self.collected_async_view_data[view_container].pop(view)

        # 5. refresh plots
        self.init_view_range()
        self.plot(reset_time_axis=self.reset_time_axis)

    # --- EXTERNAL CONTROL/ TOOLS

    def add_tool(self, tool: TsViewerTool) -> None:
        if not isinstance(tool, TsViewerTool):
            raise TsViewerError(f"TsViewer {self}: tool {tool} not of type TsViewerTool")
        if tool not in self.tools:
            tool.bind(parent=self)
            self.tools.append(tool)

    # --- LAYOUT

    def set_layout(self, layout: Union[List[BaseViewContainer], List[List[BaseViewContainer]], Dict[str, BaseViewContainer]]) -> None:
        """
        Function to quickly define a layout

        Use List[ViewContainer] -> columns
        Use List[List[ViewContainer]] -

        Parameters
        ----------
        layout

        Returns
        -------
        """
        # TODO Implement set_layout function

        pass

    @property
    def layout_components(self):
        """
        This property returns all layout components of the all sub components
        """
        widgets = self.dt_view.layout if self.dt_view is not None else []
        return {"widgets": widgets, "figures": [], "tables": []}

    # --- STATES

    def _receive_state(self, state: States) -> None:
        """
        Receives States of the ts viewer app.

        Behaviour:
            States.ACTIVE:  - all plots, tools adding, remeoving of dsvh will work
                            - if it was DEACTIVE, self.plot() is called and the time_axis reset to default
            States.DEACTIVE:
                            - propagates state to all view_containers and tools,
                            - no dsvh is removed from the ts viewer
                            - the blank out of figures is achieved by setting bokeh_view_time_axis to (0,0)
                            - dsvh can be added and removed, it will show the results first when States.Active was send
                            - table, figure and legend will blank out
                            - tools if proper implemented will not work

        Parameters
        ----------
        state:
            States Enum
        """
        if state == self._state:
            return
        self._state = state
        if state == States.DEACTIVE:
            self.state_port.send_state(state)
        elif state == States.LOADING:
            self._state = States.ACTIVE
            self.state_port.send_state(state)
            # self._set_loading_state(state)
        elif state == States.READY:
            self._state = States.ACTIVE
            # self._set_loading_state(state)
        elif state == States.ACTIVE:
            self.state_port.send_state(state)
            self.plot(reset_time_axis=self.reset_time_axis)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)

    def _set_loading_state(self, state: States) -> None:
        """
        Send state only loading states to canvas

        Parameters
        ----------
        state:
            States Enum
        """
        # for canvas in self.canvases.values():
        #     canvas.state_port.receive_state(state)
        # TODO implement _set_loading_state
        pass
