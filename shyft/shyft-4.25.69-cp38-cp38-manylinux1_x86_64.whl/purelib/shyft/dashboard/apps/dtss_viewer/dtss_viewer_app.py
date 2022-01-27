from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from shyft.dashboard.time_series.ds_view_handle_registry import DsViewHandleRegistryApp
from shyft.dashboard.time_series.renderer import LineRenderer, DiamondScatterRenderer
from shyft.dashboard.time_series.view_container.figure import Figure

from shyft.dashboard.time_series.ts_viewer import TsViewer

from shyft.dashboard.base.selector_presenter import SelectorPresenter
from shyft.dashboard.base.selector_views import FilterMultiSelect

from shyft.dashboard.base.app import AppBase
from shyft.dashboard.apps.dtss_viewer.widgets import (ContainerPathReceiver,
                                                      TsSelector, TsView, LineStyleChanger)


import bokeh
import bokeh.layouts
import bokeh.models

from shyft.dashboard.base.ports import connect_ports, Receiver
from shyft.dashboard.time_series.view_container.table import Table
from shyft.dashboard.widgets.logger_box import LoggerBox
from shyft.dashboard.widgets.message_viewer import MessageViewer

import shyft.time_series as sa


class DtssViewerApp(AppBase):

    def __init__(self, thread_pool: Optional[ThreadPoolExecutor]=None,
                 app_kwargs: Optional[Dict[str, Any]]=None) -> None:
        super().__init__(thread_pool=thread_pool)
        a= app_kwargs or {}
        self.default_host:str = a.get('dtss_host','localhost')
        self.default_port:int = a.get('dtss_port',20000)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "DTSS Viewer App"

    def get_layout(self, doc: 'bokeh.document.Document', logger: Optional[LoggerBox]=None) -> bokeh.models.LayoutDOM:
        """
        This function returns the full page layout for the app
        """
        doc.title= self.name
        event_messenger = MessageViewer(title='Log:', rows=10, width=2000, height=200, title_hight=55,
                                        sizing_mode=None, show_time=True, time_zone='Europe/Oslo')

        container_path_input = ContainerPathReceiver(dtss_host=self.default_host,dtss_port=self.default_port)
        multi_select_view = FilterMultiSelect(title='Time Series in DTSS', height=600, width=400, size=40,padding=20)
        multi_select_presenter = SelectorPresenter(name='Ts', view=multi_select_view)
        ts_selector = TsSelector(multi_select_presenter)
        utc=sa.Calendar()
        time_range = sa.UtcPeriod(utc.time(2020,1,1), utc.time(2021,1,1))

        time_step_restrictions = [sa.Calendar.HOUR, sa.Calendar.HOUR*3, sa.Calendar.DAY, sa.Calendar.WEEK,
                                  sa.Calendar.MONTH, sa.Calendar.QUARTER, sa.Calendar.YEAR]
        ts_viewer = TsViewer(bokeh_document=doc, title="Ts Viewer", padding=10,height=50,thread_pool_executor=self.thread_pool,
                             init_view_range=time_range, time_step_restrictions=time_step_restrictions)
        fig = Figure(viewer=ts_viewer, width=1500, height=600, init_renderers={LineRenderer: 6})
        table1 = Table(viewer=ts_viewer, width=1500, height=600)

        view_handle = TsView(figure=fig, table=table1)

        dsviewhandle_registry = DsViewHandleRegistryApp()

        line_style_changer = LineStyleChanger()

        connect_ports(container_path_input.send_event_message, event_messenger.receive_message)
        connect_ports(ts_selector.send_event_message, event_messenger.receive_message)
        connect_ports(view_handle.send_event_message, event_messenger.receive_message)
        connect_ports(line_style_changer.send_event_message, event_messenger.receive_message)

        connect_ports(container_path_input.send_dtss_url, ts_selector.receive_url)
        connect_ports(container_path_input.send_shyft_container, ts_selector.receive_container)
        connect_ports(container_path_input.send_dtss_url, view_handle.receive_dtss_url)
        connect_ports(ts_selector.send_selected_time_series, view_handle.receive_time_series)

        connect_ports(view_handle.send_selected, line_style_changer.receive_ds_view_handles_to_add)
        # connect_ports(view_handle.send_selected, ts_viewer.receive_ds_view_handles_to_add)

        connect_ports(view_handle.send_selected, dsviewhandle_registry.receive_ds_view_handles_to_register)
        connect_ports(dsviewhandle_registry.send_ds_view_handles_to_add, ts_viewer.receive_ds_view_handles_to_add)
        connect_ports(dsviewhandle_registry.send_ds_view_handles_to_remove,
                      ts_viewer.receive_ds_view_handles_to_remove)

        connect_ports(dsviewhandle_registry.send_ds_view_handles_to_add, line_style_changer.receive_ds_view_handles_to_add)
        connect_ports(dsviewhandle_registry.send_ds_view_handles_to_remove,
                      line_style_changer.receive_ds_view_handles_to_remove)
        # ensure we get a flying start sending suitable start values to the container
        container_path_input.send_dtss_url(f'{self.default_host}:{self.default_port}')
        container_path_input.send_shyft_container('test')

        return bokeh.layouts.column(bokeh.layouts.row(event_messenger.layout),
                                    bokeh.layouts.row(
                                        bokeh.layouts.column(
                                            bokeh.layouts.row(container_path_input.layout_components["widgets"][0],
                                                              container_path_input.layout_components["widgets"][1]),
                                            # multi_select_view.layout_components['widgets'][0],
                                            multi_select_view.layout_components['widgets'][1],
                                            bokeh.layouts.row(dsviewhandle_registry.layout_components['widgets'][1],
                                                              dsviewhandle_registry.layout_components['widgets'][0]),
                                            line_style_changer.layout
                                        ),
                                        bokeh.layouts.column(bokeh.layouts.row(ts_viewer.layout_components['widgets']),
                                                             fig.layout,
                                                             table1.layout)
                                         )
                                    )

