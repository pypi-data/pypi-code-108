import itertools
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Union, Any, Tuple
from pint import UnitRegistry, UndefinedUnitError, DimensionalityError

from shyft.dashboard.time_series.sources.ts_adapter import BasicTsAdapter

from shyft.time_series import statistics_property, TimeSeries, TsVector, UtcPeriod, min_utctime, max_utctime

from shyft.dashboard.time_series.axes import YAxis

from shyft.dashboard.time_series.state import State, Unit, Quantity

from shyft.dashboard.time_series.view_container.table import Table

from shyft.dashboard.time_series.view_container.legend import Legend

from shyft.dashboard.time_series.view_container.figure import Figure

from shyft.dashboard.base.ports import Sender, Receiver

from shyft.dashboard.time_series.sources.source import DataSource
from shyft.dashboard.time_series.view import BaseView, FillInBetween, Line, TableView, LegendItem
from shyft.dashboard.base.hashable import Hashable

from bokeh.palettes import Category20 as DefaultPalette


class DsViewHandleError(RuntimeError):
    pass


class DsViewHandle(Hashable):
    """
    This Object combines the data_source with views. It is used to show data in ts_viewer
    """
    def __init__(self, *,
                 data_source: DataSource,
                 views: List[BaseView],
                 tag: Optional[str]=None,
                 unit_registry: Optional[UnitRegistry]=None):
        """
        Initializes an immutable, hashable ds_view_handle.

        Parameters
        ----------
        data_source: unbound data source to combine with views
        views: list of unbound views to view the data
        tag: optional uid to identify the ds view handle later
        unit_registry: optional unit_registry, is used to verify if units in data_source and views are compatible,
                       should be used provided if custom defined units are used
        """
        super().__init__()
        # check data_source is unbound
        if data_source.bound:
            raise DsViewHandleError(f'{tag}: data_source {data_source.tag} already bound!')
        data_source.bind(parent=self)

        # check views
        for view in views:
            if view.bound:
                raise DsViewHandleError(f'{tag}: data_source {view.label} already bound!')
            view.bind(parent=self)

        # check units
        try:
            temp_ureg = unit_registry or UnitRegistry()
            ds_unit_dimensionality = temp_ureg.Unit(data_source.unit).dimensionality
            for v in views:
                if not hasattr(v, 'unit'):
                    continue
                v_unit_dimensionality = temp_ureg.Unit(v.unit).dimensionality
                if not ds_unit_dimensionality == v_unit_dimensionality:
                    raise DsViewHandleError(f"{tag}: Incompatible units {data_source.unit}!!{v.unit} of {data_source} and {v}!")
        except UndefinedUnitError as u:
            raise DsViewHandleError(f"{tag}: Incompatible unit registry! Please provide one!: {u}")

        self.__data_source = data_source
        self.__views = views
        self.tag = tag or str(self.uid)

    @property
    def data_source(self):
        """
        This property returns the data source
        """
        return self.__data_source

    @property
    def views(self):
        """
        This property returns the list with all defiend views
        """
        return self.__views


class DsViewHandleCreator(ABC):
    """
    This abstract class should be implemented in applications that need automated creation of DsViewHandles.
    This class should receive a data structure and create DsViewHandles to all TimeSeries contained in it.
    These DsViewHamndles are then sent forward, i.e. to a TsViewer or DsViewHandleRegistry.
    """
    def __init__(self,
                 unit_registry: Optional[UnitRegistry] = None,
                 figure_container: Optional[Union[List[Figure], Figure]] = None,
                 legend_container: Optional[Union[List[Legend], Legend]] = None,
                 table_container: Optional[Union[List[Table], Table]] = None,
                 logger: Optional[logging.Logger] = None) -> None:

        self.logger = logger or logging.getLogger()

        self.unit_registry = unit_registry or State.unit_registry

        self.figure_container = (figure_container if isinstance(figure_container, list) else [figure_container]
                                 ) if figure_container else []
        self.legend_container = (legend_container if isinstance(legend_container, list) else [legend_container]
                                 ) if legend_container else []
        self.table_container = (table_container if isinstance(table_container, list) else [table_container]
                                ) if table_container else []

        self.y_axes = [x.axis_view for lst in [figure.y_axes.values() for figure in self.figure_container] for x in lst]

        self.iter_color = itertools.cycle(DefaultPalette[20])

        self.default_line_style = "solid"
        self.default_line_width = 2.0

        self.tooltips = [("label", "@label"),
                         ("f", "$y"),
                         ("t", "$x{%d-%m-%Y %H:%M}")]

        #  Every DsViewHandleCreator should have a Receiver with the signal type of the data structure it supports.
        #  This attribute is implementation dependent since the signal type must match the associated Sender
        self.receive_data: Receiver

        self.send_ds_view_handles = Sender(parent=self,
                                           name='send ds view handles',
                                           signal_type=List[DsViewHandle])

    def _receive_data(self, data: Any):
        """
        This function receives a data structure containing TimeSeries, creates DsViewHandles to each one of them and
        sends the resulting List[DsViewHandles] forward, i.e. to a TsViewer or DsViewHandleRegistry
        """
        ds_view_handles = self.create_ds_view_handles(data)
        self.send_ds_view_handles(ds_view_handles)

    @abstractmethod
    def create_ds_view_handles(self, data: Any) -> List[DsViewHandle]:
        pass

    def get_views(self,
                  unit: str,
                  label: str,
                  visible=True,
                  y_axis_label: Optional[str] = None,
                  line_width: Optional[float] = None,
                  line_style: Optional[str] = None,
                  percentiles: Optional[List[Union[float, statistics_property]]] = None,
                  table_label: Optional[str] = None,
                  color: Optional[str] = None) -> List[BaseView]:
        """
        Auxiliary function for the creation of BaseViews for the DsViewHandles
        """
        line_width = line_width or self.default_line_width
        line_style = line_style or self.default_line_style
        percentiles = percentiles or []
        table_label = table_label or label
        color = color or next(self.iter_color)
        views = []

        if self.figure_container:
            if y_axis_label:
                y_axis = self.get_y_axis_by_label(label=y_axis_label)
            elif self.y_axes:
                y_axis = self.get_y_axis_by_unit(unit=unit)
            else:
                y_axis = None

            for figure in self.figure_container:
                if y_axis in figure.y_axes:
                    line_view = Line(color=color,
                                     unit=unit,
                                     label=label,
                                     view_container=figure,
                                     index=len(percentiles)//2,
                                     visible=visible,
                                     y_axis=y_axis,
                                     line_style=line_style,
                                     line_width=line_width,
                                     tooltips=self.tooltips)
                    views.append(line_view)
                    if len(percentiles) > 1:
                        fill_in_betweens = self.get_percentiles_views(percentiles=percentiles,
                                                                      view_container=figure,
                                                                      visible=visible,
                                                                      color=color,
                                                                      label=label,
                                                                      unit=unit,
                                                                      y_axis=y_axis)
                        views.extend(fill_in_betweens)
        if self.table_container:
            for table in self.table_container:
                table_view = TableView(view_container=table,
                                       unit=unit,
                                       columns={0: ' '},
                                       label=table_label,
                                       visible=visible)
                views.append(table_view)
        if self.legend_container:
            for legend in self.legend_container:
                legend_item = LegendItem(view_container=legend, label=label, views=[v for v in views])
                views.append(legend_item)

        return views

    def get_y_axis_by_label(self, label: str):
        """
                Auxiliary function for the management of YAxis by label.
        """
        for y_axis in self.y_axes:
            if y_axis.label == label:
                return y_axis
        else:
            raise RuntimeError(f"No y-axis found for {label}")

    def get_y_axis_by_unit(self, unit: Union[str, Unit]) -> Optional[YAxis]:
        """
        Auxiliary function for the management of YAxis by unit.
        """
        for y_axis in self.y_axes:
            if self.unit_registry(str(unit)) == self.unit_registry(str(y_axis.unit)):
                return y_axis
        else:
            for y_axis in self.y_axes:
                try:
                    self.unit_registry(str(unit)).to(self.unit_registry(str(y_axis.unit)))
                    return y_axis
                except DimensionalityError:
                    continue
            else:
                raise RuntimeError(f"No y-axis found for {unit}")

    @staticmethod
    def get_percentiles_views(percentiles: List[Union[float, statistics_property]],
                              view_container: Figure,
                              color: str,
                              label: str,
                              unit: Union[str, Unit],
                              visible: bool = True,
                              y_axis: Optional[YAxis] = None) -> List[FillInBetween]:
        """
        Auxiliary function for the creation of FillInBetweens
        """
        fill_in_betweens = []
        for i in range(len(percentiles) // 2):
            fill_label = f'{label} p{percentiles[i]}-{percentiles[-(i + 1)]}'
            fill_in_betweens.append(FillInBetween(view_container=view_container,
                                                  color=color,
                                                  label=fill_label,
                                                  visible=visible,
                                                  unit=unit,
                                                  indices=(i, -(i + 1)),
                                                  y_axis=y_axis))

        return fill_in_betweens

    @staticmethod
    def get_time_range(tso: Union[Quantity, TsVector, TimeSeries]):
        def get_ts_time_range(ts):
            if len(ts) > 0:
                return int(ts.time_axis.time_points.min()), int(ts.time_axis.time_points.max())
            else:
                return min_utctime, max_utctime

        if isinstance(tso, TimeSeries):
            t_min, t_max = get_ts_time_range(ts=tso)
        elif isinstance(tso, TsVector) and len(tso) > 0:
            ranges = [get_ts_time_range(ts=ts) for ts in tso]
            t_min, t_max = min(v[0] for v in ranges), max(v[1] for v in ranges)
        else:
            t_min, t_max = min_utctime, max_utctime

        return UtcPeriod(t_min, t_max)


class BasicDsViewHandleCreator(DsViewHandleCreator):
    """
    A basic implementation of a DsViewHandleCreator which uses BasicTsAdapters and supports labels and units.
    """
    def __init__(self,
                 unit_registry: Optional[UnitRegistry] = None,
                 figure_container: Optional[Union[List[Figure], Figure]] = None,
                 legend_container: Optional[Union[List[Legend], Legend]] = None,
                 table_container: Optional[Union[List[Table], Table]] = None,
                 logger: Optional[logging.Logger] = None) -> None:
        super().__init__(unit_registry=unit_registry,
                         figure_container=figure_container,
                         legend_container=legend_container,
                         table_container=table_container,
                         logger=logger)
        self.receive_data = Receiver(parent=self,
                                     name="Receive data",
                                     func=self._receive_data,
                                     signal_type=List[Union[Quantity, TsVector, TimeSeries,
                                                      Tuple[Union[Quantity, TsVector, TimeSeries], str]]])

    def create_ds_view_handles(self,
                               data_container: List[Union[Quantity, TsVector, TimeSeries,
                                                          Tuple[Union[Quantity, TsVector, TimeSeries], str]]]
                               ) -> List[DsViewHandle]:
        """
        :param data_container: A list of TimeSeries, TsVector, or tuples containing data and label
        :return: A list of DsViewHandles for the data
        """
        dsvhs = []
        for element in data_container:
            data, label = element if isinstance(element, Tuple) else (element, "")
            tso, unit = (data.magnitude, data.units) if isinstance(data, self.unit_registry.Quantity) else (data, "")
            tsa = BasicTsAdapter(data=tso, unit_registry=self.unit_registry, unit=unit)
            time_range = self.get_time_range(tso=tso)
            data_source = DataSource(ts_adapter=tsa, unit=unit, tag=label, time_range=time_range)
            views = self.get_views(unit=unit, label=label)
            dsvh = DsViewHandle(data_source=data_source, views=views, tag=label, unit_registry=self.unit_registry)
            dsvhs.append(dsvh)
        return dsvhs

