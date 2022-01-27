import logging
from typing import List, Dict, Any, Optional, Callable, Union, Iterable
import numpy as np
from shyft.time_series import TsVector
from enum import Enum

from bokeh.models import ColumnDataSource, DataTable, TableColumn, Div
from bokeh.layouts import column, row
from shyft.dashboard.time_series.dt_selector import dt_to_str

from shyft.dashboard.time_series.axes_handler import BaseViewTimeAxis

from shyft.dashboard.base.ports import States, StatePorts, Sender, connect_state_ports
from shyft.dashboard.time_series.tools.table_tools import TableTool
from shyft.dashboard.time_series.view import TableView
from shyft.dashboard.time_series.data_utility import find_nearest, merge_convert_ts_vectors_to_numpy
from shyft.dashboard.time_series.view_container.view_container_base import BaseViewContainer
from shyft.dashboard.time_series.state import Quantity
from shyft.dashboard.time_series.formatter import basic_time_formatter


class TableError(RuntimeError):
    pass


class BoundaryValuePolicy(Enum):
    inside = 0
    outside = 1


class Table(BaseViewContainer):
    """
    Table class is the view container for a table

    Examples
    --------
    | # create the viewer app
    | viewer = TsViewer(bokeh_document=doc, title='Test Ts Viewer')
    |
    | # create view container
    | table1 = Table(viewer=viewer, tools=[])
    |
    | # create a data source
    | data_source = DataSource(ts_adapter=A_time_series_adapter(unit_to_decorate='MW'), unit='MW',
    |                          request_time_axis_type=DsViewTimeAxisType.padded_view_time_axis,
    |                          time_range=UtcPeriod(start_time, end_time))
    |
    | # create a view in where we put the view container
    | table_view = TableView(view_container_uid=table1.uid, columns={0: 'column 1', 1: 'column 2'},
    |                        label='Generic Label')
    |
    | # create a handle for the data source and list of views connected to the data source
    | ds_view_handle = DsViewHandle(data_source=data_source, views=[table_view, line_view, fill_in_between_view])
    |
    | # add views and data source to the viewer
    | viewer.add_ds_view_handles(ds_view_handles=[ds_view_handle])
    """

    def __init__(self, *,
                 viewer: 'shyft.dashboard.time_series.ts_viewer.TsViewer',
                 width: int = 600,
                 height: int = 600,
                 title: str = '',
                 max_column_width: Optional[int] = None,
                 min_column_width: int = 120,
                 visible: bool = True,
                 time_formatter: Callable[[Iterable, str], List[str]] = basic_time_formatter,
                 tools: Union[List['TableTool'], 'TableTool'] = None,
                 boundary_value_policy: BoundaryValuePolicy = BoundaryValuePolicy.inside,
                 logger: Optional['logging.Logger'] = None,
                 alternative_view_time_axis: BaseViewTimeAxis = None) -> None:
        """
        Parameters
        ----------
        viewer:
            which TsViewer it is connected to
        width:
            pixel width of the table
        height:
            pixel height of the table
        title:
            title of the table
        max_column_width:
            sets an upper limit of the size of the columns, if None upper = infinite
        min_column_width:
            sets a lower limit of the size of the columns
        visible:
            switch for visibility
        time_formatter:
            the time format of the time column
        tools:
            optional table tools see table tools/table_tools.py
        boundary_value_policy:
            boundary value policy, show value inside or outside of boundaries
        """
        super().__init__(viewer=viewer)
        self.logger = logger or logging.getLogger(f"Table {title}")
        self.tools = []
        self.time_formatter = time_formatter
        self.bokeh_data_source = ColumnDataSource({k: [] for k in ["Time"]})
        self.bokeh_data_table = DataTable(source=self.bokeh_data_source,
                                          columns=[TableColumn(field=f"{self.uid}", title="Time", width=85)],
                                          editable=False, sortable=False, index_position=None, fit_columns=False,
                                          width=width, height=height, scroll_to_selection=True)
        self.data = {}
        self.table_columns = {}
        self.unit_row = {}
        self.title = title
        self.bokeh_title_div = Div(text=f'<b>{title}</b>', height=20, width=width)
        self.active_views = []
        self.views = []
        self.view_range_indices = []
        self.aligned_time = None

        self.y_axis_label = ''
        self.time_column_width = 145
        self.max_column_width = max_column_width
        self.min_column_width = min_column_width
        self.ts_dict = {}

        self.boundary_value_policy = boundary_value_policy

        if alternative_view_time_axis and isinstance(alternative_view_time_axis, BaseViewTimeAxis):
            self.view_time_axis = alternative_view_time_axis

        self.view_time_axis.on_change_view_range(obj=self, callback=self.view_range_callback)
        self._visible = visible
        self._visible_state = visible  # remember visibility when set Deactive and Active again
        self.visible_callback_enabled = True

        self._layout = column(row(self.bokeh_title_div, height=20, width=width, sizing_mode='fixed'),
                              row(self.bokeh_data_table))

        if tools:
            if not isinstance(tools, list):
                tools = [tools]
            for tool in tools:
                self.add_tool(tool=tool)

    @property
    def layout(self) -> Any:
        """
        This property returns the preferred layout of the view_container
        """
        return self._layout

    @property
    def layout_components(self) -> Dict[str, List[Any]]:
        """
        This property returns all layout components of the view_container
        """
        return {"widgets": [self.bokeh_title_div],
                "figures": [self.bokeh_data_table]}

    @property
    def visible(self) -> bool:
        """
        This property returns the visibility of the table
        """
        return self._visible

    @visible.setter
    def visible(self, visible: bool) -> None:
        """
        This functions will turn off the visibility of the table, i.e. the table in the browser will not be updated,
        Setter of visibility.
        """
        if visible == self._visible or not isinstance(visible, bool):
            return
        self._visible = visible
        if not visible:
            self.reset_columns()
        if visible:
            self.update_stored_view_data()

    def add_view(self, *, view: TableView) -> None:
        """
        This function adds a new view to the view_container
        """
        if view in self.views:
            self.logger.debug(f"Table {self.uid}: not adding view {view} since it is already registered")
            return
        # save view
        self.views.append(view)
        view.on_change(obj=self, attr='visible', callback=self.visible_callback)

    def update_stored_view_data(self):
        """
        This function only updates the time series who are stored within the view container
        """
        if self.visible:
            self.prepare_data_and_update_data_source()
        else:
            self.reset_data_source()

    def update_view_data(self, *, view_data: Dict[TableView, Quantity[TsVector]]) -> None:
        """
        This function updates the table with new data as sent in by view_data
        """
        if sum(v not in self.views for v in view_data):
            raise TableError(f'TableView {view_data.keys()} not in registered views')

        visible_view_changed = False
        for view, ts in view_data.items():
            view_data[view] = ts.to(self.unit_registry.Unit(view.unit))
            if view.visible:
                visible_view_changed = True
        self.ts_dict.update(view_data)
        if self.visible:
            self.prepare_data_and_update_data_source(needs_data_source_update=visible_view_changed)
        else:
            self.reset_data_source()

    def prepare_data_and_update_data_source(self, needs_data_source_update: bool = True):
        """
        This function prepares all the view data and creates the bokeh data and table columns that should be updated
        and updates the data source
        """
        if not self.ts_dict:
            return

        views_visible = {view: tsv for view, tsv in self.ts_dict.items() if view.visible}
        self.aligned_time, aligned_data = merge_convert_ts_vectors_to_numpy(ts_vectors=list(views_visible.values()))
        self.table_columns = {"Time": TableColumn(field='Time', title='Time', width=self.time_column_width)}
        self.data = {"Time": []}
        self.unit_row = {"Time": ['Unit']}

        if len(aligned_data) != 0:
            self.data["Time"] = self.time_formatter(self.aligned_time, self.parent.time_zone or None)

            for ts_number, view in enumerate(views_visible.keys()):
                for column_index, column_name in view.columns.items():
                    if view.label in column_name:
                        title = f"{column_name}"
                    else:
                        title = f"{view.label} - {column_name}" if column_name.strip() else f"{view.label}"
                    field_name = f"{view.uid}.{column_index}"
                    column_width = max(int(len(title)*7), self.min_column_width)
                    if self.max_column_width is not None:
                        column_width = min(column_width, self.max_column_width)
                    self.table_columns[field_name] = TableColumn(field=field_name, title=title, width=column_width)
                    if not aligned_data:
                        self.unit_row[field_name] = []
                        self.data[field_name] = []
                    elif not aligned_data[ts_number]:
                        self.unit_row[field_name] = [str(view.unit)]
                        self.data[field_name] = np.ones(len(self.aligned_time))*np.nan
                    else:
                        self.unit_row[field_name] = [str(view.unit)]
                        self.data[field_name] = aligned_data[ts_number][column_index]
            if needs_data_source_update:
                self.update_data_source()

    def update_data_source(self):
        """
        This function updates the data that is to be shown
        """
        self.estimate_view_range_indices()
        if not self.view_range_indices:
            self.reset_data_source()
            return
        data = {}
        for (k, d), u in zip(self.data.items(), self.unit_row.values()):
            if len(d) == 0:
                formatter = "{}"
            elif isinstance(d[0], float) or isinstance(d[0], int):
                formatter = "{:4.2f}"
            elif isinstance(d[0], str):
                formatter = "{:s}"
            else:
                raise TableError(f"{self}: data type {d[0]} in table column {k} is not string or int/float")

            # Add one to the end index since slicing needs one extra value
            data[k] = list(u) + list(map(formatter.format, d[self.view_range_indices[0]: self.view_range_indices[1] + 1]))
        self.bokeh_data_table.columns = list(self.table_columns.values())
        self.bokeh_data_source.data = data

    def reset_columns(self):
        """
        This function uses the stored time series and sets all columns but the time column to nothing
        """
        if len(self.ts_dict):
            aligned_time, aligned_data = merge_convert_ts_vectors_to_numpy(ts_vectors=list(self.ts_dict.values()))
            self.table_columns = {"Time": TableColumn(field='Time', title='Time', width=self.time_column_width)}
            self.data = {"Time": [self.time_formatter(aligned_time, self.parent.time_zone or None)]}
            self.view_range_callback()

    def reset_data_source(self):
        """
        This function clears the data that bokeh should handle
        """
        self.bokeh_data_source.data = {k: [] for k in [f"Time"]}

    def view_range_callback(self) -> None:
        """
        This callback is triggered whenever the view range changes
        view_range = self.view_time_axis.view_range
        """
        self.estimate_view_range_indices()
        #sih: self.data.keys()
        if len(self.data) > 1:
            self.update_data_source()

    def estimate_view_range_indices(self) -> None:
        """
        This function evaluates the view range indices, using
        self.aligned_time and self.view_time_axis.view_range
        and self.boundary_value_policy
        """
        if self.aligned_time is None:
            return
        elif len(self.aligned_time) == 0:
            self.view_range_indices = []
        else:
            start = self.view_time_axis.view_range.start
            end = self.view_time_axis.view_range.end
            if self.boundary_value_policy == BoundaryValuePolicy.inside:
                start_index = find_nearest(self.aligned_time, start, smaller_equal=False)
                end_index = find_nearest(self.aligned_time, end, smaller_equal=True)
            elif self.boundary_value_policy == BoundaryValuePolicy.outside:
                start_index = find_nearest(self.aligned_time, start, smaller_equal=True)
                end_index = find_nearest(self.aligned_time, end, smaller_equal=False)
            if end_index > start_index:  # note that this is possible since view-range could be 0,
                self.view_range_indices = [start_index, end_index]
            else:
                self.view_range_indices =[]

    def clear(self) -> None:
        """
        This function removes all views from the view_container and resets the meta data
        """
        self.clear_views()
        self.aligned_time = {}
        self.data = {}
        self.view_range_indices = []

    def clear_views(self, *, specific_views: Optional[List[TableView]] = None) -> None:
        """
        This function removes all or specific views from the view container
        """
        if specific_views:
            for v in specific_views:
                v.remove_all_callbacks(obj=self)
                if v in self.ts_dict:
                    self.ts_dict.pop(v)
            self.views = [v for v in self.views if v not in specific_views]
        else:
            for v in self.views:
                v.remove_all_callbacks(obj=self)
            self.ts_dict = {}
            self.views = []
        if len(self.ts_dict):
            self.update_stored_view_data()
        else:
            self.reset_columns()

    def update_title(self, title: str) -> None:
        """
        This function sets the title in the correct <div> format
        """
        if self.title:
            self.bokeh_title_div.text = ': '.join([self.title, title])
        else:
            self.bokeh_title_div.text = title

    def _receive_state(self, state: States) -> None:
        """
        This function checks the state of self
        """
        if state == self._state:
            return
        self._state = state
        if state == States.LOADING:
            if self._state == state:
                return
            self.update_title('Loading table ...')
        elif state == States.DEACTIVE:
            if self.visible:
                self.reset_data_source()
            self._visible_state = self.visible
            self.visible = False
            self.state_port.send_state(state)
        elif state in [States.ACTIVE, States.READY]:
            self.visible = self._visible_state
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)

    def visible_callback(self, obj, attr, old_value, new_value):
        """
        This function is the callback for when the visibility for table view changes
        """
        if self._state == States.DEACTIVE or not self.visible_callback_enabled:
            return
        if obj not in self.views:
            obj.remove_all_callbacks(self)
            return
        self.update_stored_view_data()

    def add_tool(self, tool: TableTool) -> None:
        """
        This function adds a FigureTool to the figure
        """
        if not isinstance(tool, TableTool):
            raise TableError(f'Table {self.title}: tool {tool} not of type TableTool')
        if tool not in self.tools:
            tool.bind(parent=self)
            self.tools.append(tool)
            connect_state_ports(self.state_port, tool.state_port)


class StatisticsTable(Table):

    def __init__(self, *,
                 viewer: 'shyft.dashboard.time_series.ts_viewer.TsViewer',
                 width: int = 600,
                 height: int = 600,
                 title: str = '',
                 name_column_width: int = 300,
                 max_column_width: Optional[int] = None,
                 min_column_width: int = 120,
                 visible: bool = True,
                 time_formatter: Callable[[np.ndarray, str], List[str]] = basic_time_formatter,
                 tools: Union[List['TableTool'], 'TableTool'] = None,
                 boundary_value_policy: BoundaryValuePolicy = BoundaryValuePolicy.inside,
                 logger: Optional['logging.Logger'] = None,
                 alternative_view_time_axis: BaseViewTimeAxis = None) -> None:
        super().__init__(viewer=viewer,
                         width=width,
                         height=height,
                         title=title,
                         max_column_width=max_column_width,
                         min_column_width=min_column_width,
                         visible=visible,
                         time_formatter=time_formatter,
                         tools=tools,
                         boundary_value_policy=boundary_value_policy,
                         logger=logger,
                         alternative_view_time_axis=alternative_view_time_axis)

        def calc_column_width(title):
            column_width = max(int(len(title)*7), self.min_column_width)
            if self.max_column_width is not None:
                column_width = min(column_width, self.max_column_width)
            return column_width

        self.name_column_width = name_column_width

        self.table_columns = {"Name": TableColumn(field='Name', title='Name', width=self.name_column_width),
                              "Unit": TableColumn(field='Unit', title='Unit', width=calc_column_width('Unit')),
                              'Mean': TableColumn(field='Mean', title='Mean', width=calc_column_width('Mean')),
                              'Min': TableColumn(field='Min', title='Min', width=calc_column_width('Min')),
                              'Max': TableColumn(field='Max', title='Max', width=calc_column_width('Max')),
                              'Std': TableColumn(field='Std', title='Std', width=calc_column_width('Std')),
                              'Net Change': TableColumn(field='Net Change', title='Net Change',
                                                        width=calc_column_width('Net Change'))
                              }

    def prepare_data_and_update_data_source(self, needs_data_source_update: bool = True):
        """
        This function prepares all the view data and creates the bokeh data and table columns that should be updated
        and updates the data source
        """
        if not self.ts_dict:
            return

        views_visible = {view: tsv for view, tsv in self.ts_dict.items() if view.visible}
        self.aligned_time, aligned_data = merge_convert_ts_vectors_to_numpy(ts_vectors=list(views_visible.values()))
        self.data = {}
        self.unit_row = {}

        if len(aligned_data) != 0:

            for ts_number, view in enumerate(views_visible.keys()):
                for column_index, column_name in view.columns.items():
                    if view.label in column_name:
                        title = f"{column_name}"
                    else:
                        title = f"{view.label} - {column_name}" if column_name.strip() else f"{view.label}"
                    if not aligned_data:
                        self.unit_row[title] = []
                        self.data[title] = []
                    elif not aligned_data[ts_number]:
                        self.unit_row[title] = [str(view.unit)]
                        self.data[title] = np.ones(len(self.aligned_time))*np.nan
                    else:
                        self.unit_row[title] = [str(view.unit)]
                        self.data[title] = aligned_data[ts_number][column_index]
        if needs_data_source_update:
            self.update_data_source()

    def update_data_source(self):
        """
        This function updates the data that is to be shown
        """
        self.estimate_view_range_indices()
        if not self.view_range_indices:
            self.reset_data_source()
            return

        data = {k: [] for k in self.table_columns.keys()}

        # just return if the same value is shown
        if self.view_range_indices[0] == self.view_range_indices[1]:
            self.bokeh_data_table.columns = list(self.table_columns.values())
            self.bokeh_data_source.data = data
            return

        t = self.aligned_time[self.view_range_indices[0]: self.view_range_indices[1] + 1]

        data["Name"].append('Time Range')
        data["Unit"].append('-')
        data['Min'].append(basic_time_formatter([t[0]], self.parent.time_zone or None)[0])
        data['Max'].append(basic_time_formatter([t[-1]], self.parent.time_zone or None)[0])
        data['Mean'].append('-')
        data['Std'].append('-')
        data['Net Change'].append(dt_to_str(int(t[-1] - t[0])))
        for (k, d), u in zip(self.data.items(), self.unit_row.values()):
            d = d[self.view_range_indices[0]: self.view_range_indices[1] + 1]

            if len(d) == 0 or np.isnan(d).all():
                min_v = '-'
                max_v = '-'
                mean_v = '-'
                std_v = '-'
                change = '-'
            elif isinstance(d[0], float) or isinstance(d[0], int):
                min_v = f"{np.nanmin(d):4.2f}"
                max_v = f"{np.nanmax(d):4.2f}"
                mean_v = f"{np.nanmean(d):4.2f}"
                std_v = f"{np.nanstd(d):4.2f}"
                try:
                    nans = np.where(~np.isnan(d))
                    if np.shape(nans)[1] > 1:
                        s = np.polyfit(x=t[nans], y=d[nans], deg=1)
                        s = s[0]
                        change = f"{s*(t[-1] - t[0]):4.2f}"
                    else:
                        change = '-'
                except Exception as e:
                    self.logger.error(f"error: {e}")
                    change = '-'
            elif isinstance(d[0], str):
                min_v = '-'
                max_v = '-'
                mean_v = '-'
                std_v = '-'
                change = '-'
            else:
                raise TableError(f"{self}: data type {d[0]} in table column {k} is not string or int/float")

            data["Name"].append(k)
            data["Unit"].append(u)
            data['Min'].append(min_v)
            data['Max'].append(max_v)
            data['Mean'].append(mean_v)
            data['Std'].append(std_v)
            data['Net Change'].append(change)
        self.bokeh_data_table.columns = list(self.table_columns.values())
        self.bokeh_data_source.data = data

    def reset_columns(self):
        """
        This function uses the stored time series and sets all columns but the time column to nothing
        """
        if len(self.ts_dict):
            self.data = {}
            self.view_range_callback()

    def view_range_callback(self) -> None:
        """
        This callback is triggered whenever the view range changes
        view_range = self.view_time_axis.view_range
        """
        self.estimate_view_range_indices()
        self.data.keys()
        if len(self.data) > 0:
            self.update_data_source()

#
# class TableEditable(Table):
#     """
#     This object represents an editable table, it is not yet fully implemented
#     """
#     def __init__(self, *, viewer: 'statkraft.bokeh.time_series.ts_viewer.TsViewer', axis_unit: str,
#                  width: int=600, height: int=600, tools=List[str], title: Optional[str]=''):
#         """
#         Parameters
#         ----------
#         viewer: which TsViewer it is connected to
#         width: pixel width of the table
#         height: pixel height of the table
#         title: title of the table
#         tools: not in use
#         """
#         raise NotImplementedError("Editable table is not yet implemented completely")
#         super().__init__(viewer=viewer, axis_unit=axis_unit, width=width, height=height, tools=tools,
#                          title=title)
#         self.bokeh_data_table.editable = True
#         self.bokeh_data_source.on_change('data', self.changed_data_values)
#         self.send_table_edits = Sender(parent=self, name='send table edits', signal_type=Dict)
#
#     def changed_data_values(self, attr: str, old: Dict, new: Dict) -> None:
#         """
#         Is called on change in an editable table.
#         Sorts edited data and sends via Sender as a dictionary.
#
#         Parameters
#         ----------
#         attr str
#         old Dict
#         new Dict
#         """
#         if new:
#             if new.keys() == old.keys():
#                 table_keys = list(new.keys())
#                 if 'Time' in table_keys:
#                     table_keys.remove('Time')
#                 for name in table_keys:
#                     check = np.array_equal(np.array(new[name]), np.array(old[name]))
#                     if not check:
#                         if len(old[name]) == len(new[name]):
#                             diff_mask = np.equal(old[name], new[name])
#                             changed_value = np.ma.masked_array(new[name], mask=diff_mask)
#                             ch_value_date = np.ma.masked_array(new['Time'], mask=diff_mask)
#                             changes = {name: {'data': changed_value[~changed_value.mask].data,
#                                               'time': ch_value_date[~ch_value_date.mask].data}}
#
#                             # Send values onward to be processed
#                             # self.send_table_edits(changes) # f.eks.
