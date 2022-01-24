import itertools
from typing import List,Optional

from shyft.dashboard.base.selector_views import MultiSelect, Select
from shyft.dashboard.time_series.ds_view_handle_registry import DsViewHandleRegistry
from shyft.dashboard.time_series.view_container.figure import Figure
from shyft.dashboard.time_series.view_container.table import Table

from shyft.dashboard.time_series.view_container.view_container_base import BaseViewContainer

from shyft.dashboard.base.ports import Receiver, Sender, connect_ports
import bokeh.models
import bokeh.layouts
from shyft.dashboard.base.app import update_value_factory, LayoutComponents
from shyft.dashboard.apps.dtss_viewer.dtsc_helper_functions import check_dtss_url, find_all_ts_names_and_url, \
    DtssTsAdapter
from shyft.dashboard.base.selector_model import SelectorModelBase, processing_wrapper
from shyft.dashboard.base.selector_presenter import SelectorPresenter
from bokeh.palettes import Category20c as Palette  # @UnresolvedImport
from shyft.dashboard.time_series.sources.source import DataSource
from shyft.dashboard.time_series.view import Line, TableView, DiamondScatter
from shyft.dashboard.time_series.ds_view_handle import DsViewHandle
from shyft.dashboard.widgets.selector_models import LabelDataSelector


class ConsolePrinter:

    def __init__(self, name: str) -> None:
        """
        Small class receiving a string and printing it out on receive
        """
        self.name = name
        # create a receiver port
        self.receive_text = Receiver(parent=self, name='receive text to print', func=self._receive_text,
                                     signal_type=str)

    def _receive_text(self, text: str) -> None:  # create a simple receiving function
        """
        create a simple receiving function to receive and int and print it

        Parameters
        ----------
        text:
            text to print
        """
        print(f" {self.name} received: {text}")


class ContainerPathReceiver:

    def __init__(self,dtss_host: Optional[str]='', dtss_port: Optional[int]=20000) -> None:
        self.dtss_host:str = dtss_host or 'localhost'
        self.dtss_port:int = dtss_port or 20000
        self.send_event_message = Sender(parent=self, name="Container path event messenger", signal_type=str)
        self.send_dtss_url = Sender(parent=self, name="DTSS url sender", signal_type=str)
        self.send_shyft_container = Sender(parent=self, name="shyft container name sender", signal_type=str)
        default_url=f"{self.dtss_host}:{self.dtss_port}"
        self.dtss_url_text_input = bokeh.models.TextInput(title="DTSS url", value=default_url,placeholder=default_url, width=150)
        self.shyft_container_text_input = bokeh.models.TextInput(title="Shyft container name", value="test",placeholder="test", width=150)

        self.dtss_url_text_input.on_change('value', self.changed_value_dtss_url)
        self.shyft_container_text_input.on_change('value', self.changed_value_shyft_container)

        self.set_dtss_text = update_value_factory(self.dtss_url_text_input, 'value')
        self.set_shyft_container_text = update_value_factory(self.shyft_container_text_input, 'value')

        self._layout = bokeh.layouts.column(bokeh.layouts.row(self.dtss_url_text_input),
                                            bokeh.layouts.row(self.shyft_container_text_input),margin=(5,5,5,5))

    @property
    def layout(self) -> bokeh.layouts.column:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.dtss_url_text_input, self.shyft_container_text_input],
                'figures': []}

    def changed_value_dtss_url(self, attr, old, new) -> None:
        if check_dtss_url(new):
            self.send_event_message(f"DTSSR: Received valid url: {new}")
            self.send_dtss_url(new)
            self.send_shyft_container(self.shyft_container_text_input.value)
        else:
            self.send_event_message(f"DTSSR: Invalid url: {new}")

    def changed_value_shyft_container(self, attr, old, new) -> None:
        self.send_event_message(f"SCNR: Received shyft container name: {new}")
        self.send_shyft_container(new)


class TsSelector(SelectorModelBase):

    def __init__(self, presenter: SelectorPresenter) -> None:
        super().__init__(presenter=presenter)

        self.url = None
        self.container = None
        self.ts_list = None

        self.send_event_message = Sender(parent=self, name="TS selector event messenger", signal_type=str)
        self.send_selected_time_series = Sender(parent=self, name="send_selected_time_series", signal_type=List[str])

        self.receive_url = Receiver(parent=self, name='receive url', func=self._receive_url, signal_type=str)
        self.receive_container = Receiver(parent=self, name='receive container', func=self._receive_container, signal_type=str)

    def _receive_url(self, text: str) -> None:
        self.url = text
        if self.container:
            self.update_list()

    def _receive_container(self, text: str) -> None:
        self.container = text
        if self.url:
            self.update_list()

    @processing_wrapper
    def get_options(self):
        try:
            return find_all_ts_names_and_url(self.url, self.container)
        except RuntimeError as e:
            self.send_event_message(f"TSS: could not retrieve data")
            return []

    def update_list(self):
        self.send_event_message(f"TSS: updating TS list")
        self.ts_list = self.get_options()
        self.presenter.set_selector_options(options=self.ts_list, callback=False,
                                            selected_value=["shyft://test/ts-0"],
                                            sort=True)

    def on_change_selected(self, selected_values: List[str]) -> None:
        self.send_event_message(f"TSS: received {len(selected_values)} Time Series")
        self.send_selected_time_series(selected_values)


class TsView:
    def __init__(self, figure: Figure, table: Table) -> None:
        self.figure = figure
        self.table = table
        self.color_line = itertools.cycle(Palette[10])
        self.line_styles = itertools.cycle(['solid', 'dashed', 'dotted', 'dotdash', 'dashdot'])
        self.url_str = ''
        self.send_event_message = Sender(parent=self, name="TsView event messenger", signal_type=str)
        self.receive_dtss_url = Receiver(parent=self, name="send_selected_time_series", func=self._set_url, signal_type=str)
        self.view_handles = []
        self.receive_time_series = Receiver(parent=self, name="send_selected_time_series", func=self._add_time_series, signal_type=List[str])
        self.send_selected = Sender(parent=self, name="ts_selected", signal_type=List[DsViewHandle])

    def _set_url(self, url: str):
        self.url_str = url

    def _add_time_series(self, ts_names: List[str]):
        self.view_handles = []
        self.send_event_message(f"Add time-series {ts_names}")
        for ts_name in ts_names:
            ts_adapter = DtssTsAdapter(self.url_str, ts_name)
            ds = DataSource(ts_adapter=ts_adapter, unit="", tag=ts_name)
            view = Line(view_container=self.figure, color=next(self.color_line), label=ts_name, unit="",index=0, line_width=0.7)

        table_view = TableView(view_container=self.table, columns={0: 'demo'}, label=ts_name.split("/")[-1], unit='')
        view_handle = DsViewHandle(data_source=ds, views=[view, table_view], tag=ts_name)
        self.view_handles.append(view_handle)

        # print(self.view_handles)

        self.send_selected(self.view_handles)


class LineStyleChanger:

    def __init__(self):

        self.line_styles = ['solid', 'dashed', 'dotted', 'dotdash', 'dashdot']
        self.receive_ds_view_handles_to_add = Receiver(parent=self, name="TS to add", signal_type=List[DsViewHandle],
                                                       func=self._receive_ds_view_handles_to_add)
        self.receive_ds_view_handles_to_remove = Receiver(parent=self, name="TS to remove",
                                                          signal_type=List[DsViewHandle],
                                                          func=self._receive_ds_view_handles_to_remove)
        self.receive_line_styles = Receiver(parent=self, name="linestyle to change",
                                            signal_type=List[str],
                                            func=self._receive_line_style)
        self.send_event_message = Sender(parent=self, name="DsView event messenger", signal_type=str)
        self.dsvh_registry = DsViewHandleRegistry()

        self.select_view = Select(title='Select line-style', height=50, width=150)
        select_presenter = SelectorPresenter(name='Line-style', view=self.select_view)
        select_model = LabelDataSelector(presenter=select_presenter)
        select_model.receive_labels(self.line_styles)

        connect_ports(select_model.send_selected_labels, self.receive_line_styles)
        self.layout = self.select_view.layout

    def _receive_ds_view_handles_to_add(self, dsvhs: List[DsViewHandle]):
        self.dsvh_registry.add(dsvhs)

    def _receive_ds_view_handles_to_remove(self, dsvhs: List[DsViewHandle]):
        self.dsvh_registry.remove(dsvhs)

    def _receive_line_style(self, line_style: List[str]):
        self.send_event_message(f"Change line style to {line_style[0]}")
        for dsvh in self.dsvh_registry.ds_view_handles:
            for v in dsvh.views:
                if isinstance(v, Line):
                    v.line_style = line_style[0]


if __name__ == '__main__':
    cp = ConsolePrinter(name='dtss printer')
    cp.receive_text("blub")
