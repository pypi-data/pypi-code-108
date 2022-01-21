from __future__ import annotations
import json
import copy
import itertools
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Tuple, Optional, Union, Dict, Any
from dataclasses import dataclass, field

from e360_charting.common import ColorsNormalExt
from .utils import validate_sunburst_total_values
from .stylers import TableStyler
from .models import (
    ColourStr,
    DictAny,
    ErrorAxisModel,
    GridModel,
    Textpositions,
    Measures,
    LinkModel,
    NodeModel,
    MarkerModel,
    TableFormatModel,
    ChartDataModel,
    ChartModel,
    AnnotationModel,
    LayoutModel,
    ReportModel,
    StratumItemModel,
    StratificationModel,
    VisualisationModel,
    _PlotlyPayloadModel
)

# --- CHART CLASSES -----------------------------------------------------------


@dataclass
class BaseVisualisation(ABC):
    _visualisation: VisualisationModel = field(default_factory=VisualisationModel, init=False)
    _strata_map: dict = field(default_factory=lambda: defaultdict(dict), init=False, repr=False)
    _rendered: bool = field(default=False, init=False, repr=False)
    report_title: str = field(default='<No Report Name>')
    chart_title: str = field(default='<No Chart Name>', repr=False)
    layout_title: str = field(default='<No Layout Name>', repr=False)

    def dump(self) -> dict:
        return self.visualisation.Schema().dump(self.visualisation)

    def json(self, **kwargs) -> str:
        return self.visualisation.Schema().dumps(self.visualisation, **kwargs)

    @property
    def visualisation(self):
        """
        Delayed rendering of the charts data, which allows setting the charts up,
        but not rendering until the ``visualisation`` attribute is called for.
        This allows any pre-requiste works to happen (eg: for grouped charts).
        """
        if not self._rendered:
            self.render()
            self._rendered = True
        return self._visualisation

    @abstractmethod
    def render(self):
        """Runs a series of class methods to build up a chart"""
        raise NotImplementedError  # pragma: no cover

    def as_plotly(self, **kwargs):
        """
        Returns an instance converted with its data for native Plotly lib.
        This class may be overwritten to accomodate visualisations as needed.

        Returns:
            PlotlyConverter:

        Raises:
            NotImplementedError: when not supported by visualisation class.

        """
        return PlotlyConverter(self, **kwargs)

    def copy(self):
        return copy.deepcopy(self)


@dataclass
class PlotlyVisualisation(BaseVisualisation):
    """
    A visualisation instance compatible with VRS schemas, but the source derives from native plotly objects: Figure or JSON.
    To build from Figures, use `.from_figure(figure, **kwargs)` classmethod.

    Args:
        (inherited from BaseVisualisation)
        plotly_json: as dict, json of the plotly figure
        layout_extras: as dict, additional keys/values for the layout model

    Examples:
        ```
        # From a plotly JSON instance
        # assert isinstance(data, dict) is True
        vis = PlotlyVisualisation(plotly_json=data, **kwargs)

        # From a plotly Figure instance
        # assert isinstance(fig, plotly.graph_objects.Figure) is True
        vis = PlotlyVisualisation.from_figure(fig, **kwargs)
        ```
    """
    plotly_json: DictAny = field(default_factory=dict, repr=False)
    layout_extras: DictAny = field(default_factory=dict, repr=False)

    def __post_init__(self):
        self._validate_plotly_json(self.plotly_json)

    def render(self) -> None:
        data = self._convert_plotly_to_visualisation(self.plotly_json.copy())
        self._visualisation = VisualisationModel.Schema().load(data)
        for report in self._visualisation.reports:
            report.name = report.name or self.report_title
            layout_dict = report.layout if isinstance(report.layout, dict) else report.layout.__dict__
            layout_dict.update(self.layout_extras)

    def as_plotly(self, **kwargs):  # pragma: no cover
        import warnings
        warnings.warn('Use `.plotly_json` to retrieve the plotly json object', UserWarning)
        raise NotImplementedError

    @staticmethod
    def _convert_plotly_to_visualisation(plotly_obj: dict) -> dict:
        data = plotly_obj.pop('data')
        layout = plotly_obj.pop('layout', {})
        layout_title = layout.get('title') or ''
        if isinstance(layout_title, dict):
            layout_title = layout.get('title', {}).get('text', '')
        return dict(reports=[
            dict(name=layout_title, layout=layout, charts=[
                dict(type=data[0]['type'], data=data)
            ])
        ])

    @staticmethod
    def _validate_plotly_json(plotly_json: dict):
        if not isinstance(plotly_json, dict):
            raise TypeError(f'plotly_json must be a dict (json); provided: `{type(plotly_json)}`')
        if not plotly_json:
            raise ValueError('plotly_json must not be empty')
        if not plotly_json.get('data'):
            raise ValueError('plotly_json does not have chart data')
        if not plotly_json['data'][0].get('type'):
            raise ValueError('plotly_json chart data does not have a `type` key.')

    @staticmethod
    def _validate_figure(figure: Any) -> None:
        import plotly.graph_objects
        if not isinstance(figure, plotly.graph_objects.Figure):
            raise TypeError(f"`figure` must be an instance of `plotly.graph_objects.Figure`; provided: `{type(figure)}`")

    @staticmethod
    def _convert_figure(figure: 'plotly.graph_objects.Figure') -> dict:  # noqa: F821
        from plotly.utils import PlotlyJSONEncoder
        serialized = json.dumps(figure, cls=PlotlyJSONEncoder)
        return json.loads(serialized)

    @classmethod
    def from_figure(cls, figure: 'plotly.graph_objects.Figure', **kwargs: Any):  # noqa: F821
        cls._validate_figure(figure)
        data = cls._convert_figure(figure)
        return cls(plotly_json=data, **kwargs)


@dataclass
class GroupedVisualisations(BaseVisualisation):
    """
    A visualisation instance capable of grouping multiple visualisations (or groups) together.

    Examples:
        ```
        group = GroupedVisualisations()  # Create a group object
        chart1 = BarVisualisation(...)  # Create a chart
        group += chart1  # Add the chart to the group
        ```
    """

    def add(self, vis_obj: BaseVisualisation):
        """Add a visualisation or list of visualisations to the group."""

        vis_obj_list = vis_obj if isinstance(vis_obj, list) else [vis_obj]

        for vis_obj in vis_obj_list:
            if not isinstance(vis_obj, BaseVisualisation):
                raise ValueError('You can only add BaseVisualisation object types.')
            vis_obj._strata_map.update(self._strata_map)
            self._merge_stratas(vis_obj.visualisation.stratifications)
            self._visualisation.reports.extend(vis_obj.visualisation.reports)
            self._strata_map.update(vis_obj._strata_map)
            self._update_ids()

    def _merge_stratas(self, stratifications):
        existing_strata_dict = {s.name: s for s in self._visualisation.stratifications}
        for new_strata in stratifications:
            if new_strata.name in existing_strata_dict:
                existing_strata = existing_strata_dict[new_strata.name]
                for strata_item in new_strata.items:
                    if strata_item not in existing_strata.items:
                        existing_strata.items.append(strata_item)
            else:
                self._visualisation.stratifications.append(new_strata)

    def _update_ids(self):
        for n, report in enumerate(self._visualisation.reports, start=1):
            report.id = f'report{n}'
            for nn, chart in enumerate(report.charts, start=1):
                chart.id = f'chart{n}-{nn}'

    def render(self):
        pass

    @property
    def count(self):
        return len(self)

    def as_plotly(self, **kwargs):
        raise NotImplementedError('Converting to Plotly is not supported by this Visualisation class.')

    def __add__(self, other):
        if self == other:
            raise ValueError('Object added is the same or has same data as self.')
        self.add(other)
        return self

    def __iadd__(self, other):
        return self + other

    def __len__(self):
        return len(self._visualisation.reports)

    def __bool__(self):
        return bool(self.count)


@dataclass
class BaseBuilder(ABC):
    """
    Builder functions for building Visualisation objects.
    """
    annotations: Optional[List[AnnotationModel]] = field(default_factory=list, repr=False)
    _color_cycler = None

    def setup_layout(self):
        layout_dict = dict(self.layout_dict(), title=self.layout_title)
        annot_dict = self.annotation_dict()
        if self.annotations and annot_dict:
            for annotation in self.annotations:
                annotation.__dict__.update(annot_dict)
        self.layout = LayoutModel(**layout_dict, annotations=self.annotations)
        if hasattr(self, 'axes_titles') and isinstance(self.axes_titles, (list, tuple)):
            self.layout.add_axes_titles(*self.axes_titles)

    def setup_report(self):
        self.report = ReportModel(
            name=self.report_title,
            layout=self.layout)

    def setup_visualisation(self):
        self._visualisation.reports.append(self.report)

    def next_color(self) -> str:
        if self._color_cycler is None:
            self._color_cycler = itertools.cycle(self.COLORS)
        return next(self._color_cycler)

    def reset_colors(self) -> None:
        self._color_cycler = None

    @staticmethod
    def cycle_colors(color_list: list, n: int) -> list:
        cycler = itertools.cycle(color_list)
        return [next(cycler) for _ in range(n)]

    def _validate_list_lengths(self, *lists: list):
        """
        Checks the lengths of the expected datas are valid in all given lists

        Raises:
            ValueError
        """
        if len({*map(len, filter(len, lists))}) > 1:
            raise ValueError('all non-empty list must be same length')

    @abstractmethod
    def setup_chart(self):
        """
        The function processing the dataframe into the chart data.
        Writes a ``self.chart`` object into the class instance.
        """
        raise NotImplementedError  # pragma: no cover


@dataclass
class BaseAxesVisualisation(BaseBuilder, BaseVisualisation):
    """
    Base Visualisation class for serializing/desializing single charts with axes.
    Must be mixed with one of ``BaseMixin`` subclasses to produce a desired chart type.

    Args:
        x_values: a list of values (list of lists) for x-axis
        y_values: a list of values (list of lists) for y-axis
        trace_names: list of trace names
        report_title: title for the Report
        chart_title: title for the Chart
        layout_title: title for the Layout
        axes_titles: optional, a tuple of two strings, eg: ``(<x-axis-title>, <y-axis-title>)``
        hovertext: list of text feields to use for hovertext.
        horizontal: if True only x_values plots will be created.
        vertical: if True only y_values plots will be created.
        * if both vertical and horizontal are True or False it defaults to 2D plots with both x and y values.
        three_dimensional: if True it adds z_values to any of the horizontal and vertical combinations.

    """
    x_values: List[list] = field(default_factory=list, repr=False)
    y_values: List[list] = field(default_factory=list, repr=False)
    z_values: Optional[List[list]] = field(default=None)
    trace_names: List[Any] = field(default_factory=list)
    colors: Optional[List[ColourStr]] = field(default_factory=list, repr=False)
    axes_titles: Optional[Tuple[str, str]] = field(default=None)  # (x, y)
    hovertext: Optional[List[List[str]]] = field(default_factory=list)
    extra_charts = []  # classes for building additional charts per report
    horizontal: Optional[bool] = field(default=None)
    vertical: Optional[bool] = field(default=None)
    three_dimensional: Optional[bool] = field(default=None)
    annotate_by_z: Optional[bool] = field(default=False)
    z_annotation_color: Optional[ColourStr] = field(default=ColorsNormalExt.WHITE)
    is_subplot: Optional[bool] = field(default=None)
    subplot_dimensions: Optional[list] = field(default=None)
    subplot_labels: Optional[List[Tuple]] = field(default=None)
    colorbar_title: Optional[str] = field(default=None)

    def __post_init__(self):
        if not self.colors:
            self.colors = self.cycle_colors(self.COLORS, len(self.trace_names))

        if self.annotate_by_z and self.z_values:
            self.annotations = self._setup_z_annotations(self.z_annotation_color)

        if not self.hovertext and self.x_values:
            self.hovertext = [[] for i in range(len(self.x_values))]
        elif not self.hovertext and self.y_values:
            self.hovertext = [[] for i in range(len(self.y_values))]

    def render(self):
        self.setup_layout()
        self._setup_subplots()
        self.setup_report()
        self.setup_chart()
        if self.extra_charts:
            self.reset_colors()
            self.setup_extra_charts()
        self.setup_visualisation()

    def _validate_input(self):
        """Checks the lengths of the expected datas are valid"""
        self._validate_list_lengths(self.x_values, self.y_values, self.trace_names, self.colors, self.hovertext)
        if not self.trace_names:
            raise ValueError("trace_names is empty.")
        for x, y, t in zip(self.x_values, self.y_values, self.trace_names):
            if any(isinstance(i, list) for i in x):
                sublists_len = map(len, [sublist for sublist in x])
                if any(x != len(y) for x in sublists_len):
                    raise ValueError(f'x-list and y-list lengths for trace `{t}` do not match.')
            elif not self.three_dimensional and len(x) != len(y):
                raise ValueError(f'x-list and y-list lengths for trace `{t}` do not match.')

    def _setup_chart_data(self, style_class, color, **kwargs):
        marker = MarkerModel(**style_class.marker_dict(), color=color)
        data_item = ChartDataModel(**style_class.chartdata_dict(), **kwargs, marker=marker)
        if self.three_dimensional and self.z_values:
            data_item.z = self.z_values
            if data_item.colorbar and self.colorbar_title:
                data_item.colorbar = dict(title=self.colorbar_title)
        if self.is_subplot:
            trace_idx = str(self.colors.index(color) + 1)
            data_item.xaxis = "x" + trace_idx
            data_item.yaxis = "y" + trace_idx
        self.chart.data.append(data_item)

    def setup_chart(self, style_class=None):
        style_class = style_class or self
        self._validate_input()
        self.chart = ChartModel(**style_class.chart_dict(), id=f'chart{len(self.report.charts) + 1}')
        self.setup_typed_chart(style_class)
        self.report.charts.append(self.chart)

    def setup_extra_charts(self):
        for StyleClass in self.extra_charts:
            self.setup_chart(style_class=StyleClass)

    def _setup_subplots(self):
        if self.is_subplot and self.subplot_dimensions and len(self.subplot_dimensions) == 2:
            grid = GridModel(rows=self.subplot_dimensions[0], columns=self.subplot_dimensions[1])
            self.layout.grid = grid

        if self.subplot_labels:
            x_attrs = filter(lambda x: 'xaxis' in x, self.layout.__dict__)
            y_attrs = filter(lambda y: 'yaxis' in y, self.layout.__dict__)
            for label, x_attr, y_attr in zip(self.subplot_labels, x_attrs, y_attrs):
                x, y = label
                x_val = {'zeroline': False, 'visible': True, 'showline': True, 'title': x}
                y_val = {'zeroline': False, 'visible': True, 'showline': True, 'title': y}
                setattr(self.layout, x_attr, x_val)
                setattr(self.layout, y_attr, y_val)

    def _setup_z_annotations(self, annot_color):
        annots: List[AnnotationModel] = []
        x = self.x_values[0]
        y = self.y_values[0]
        z = self.z_values

        if len(self.y_values[0]) != len(self.z_values):
            raise ValueError('Number of z_values rows needs to match y_values elements')

        for y_idx, y_val in enumerate(y):
            for x_idx, x_val in enumerate(x):
                if len(z[y_idx]) != len(x):
                    raise ValueError('Number of z_values columns needs to match x_value number of elements')
                annot = AnnotationModel(x=x_val, y=y_val, text=str(z[y_idx][x_idx]),
                 xref='x1', yref='y1', font={'color': annot_color})
                annots.append(annot)
        return annots

    def setup_typed_chart(self, style_class):
        common_attr = self.trace_names, self.colors, self.hovertext
        if self.horizontal and not self.vertical:
            self.layout.set_data_points(len(self.x_values))
            for x, trace_name, color, hovertext in zip(self.x_values, *common_attr):
                self._setup_chart_data(style_class, color, x=x, name=trace_name, hovertext=hovertext)
        elif self.vertical and not self.horizontal:
            self.layout.set_data_points(len(self.y_values), horizontal=False)
            for y, trace_name, color, hovertext in zip(self.y_values, *common_attr):
                self._setup_chart_data(style_class, color, y=y, name=trace_name, hovertext=hovertext)
        else:
            self.layout.set_data_points(len(self.x_values))
            for x, y, trace_name, color, hovertext in zip(self.x_values, self.y_values, *common_attr):
                self._setup_chart_data(style_class, color, x=x, y=y, name=trace_name, hovertext=hovertext)


@dataclass
class BaseAxesArrayVisualisation(BaseAxesVisualisation):

    array_x: Optional[List[List[Any]]] = field(default_factory=list)
    arrayminus_x: Optional[List[List[Any]]] = field(default_factory=list)
    array_y: Optional[List[List[Any]]] = field(default_factory=list)
    arrayminus_y: Optional[List[List[Any]]] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not self.array_x:
            self.array_x = [[] for _ in range(len(self.x_values))]

        if not self.arrayminus_x:
            self.arrayminus_x = [[] for _ in range(len(self.x_values))]

        if not self.array_y:
            self.array_y = [[] for _ in range(len(self.y_values))]

        if not self.arrayminus_y:
            self.arrayminus_y = [[] for _ in range(len(self.y_values))]

    def setup_typed_chart(self, style_class):
        self.layout.set_data_points(len(self.x_values))
        for x, array_x, arrayminus_x, y, array_y, arrayminus_y, trace_name, color, hovertext in zip(self.x_values, self.array_x, self.arrayminus_x, self.y_values, self.array_y, self.arrayminus_y, self.trace_names, self.colors, self.hovertext):
            marker = MarkerModel(**style_class.marker_dict(), color=color)
            data_item = self.setup_data_item(style_class, marker, x, array_x, arrayminus_x, y, array_y, arrayminus_y, trace_name, color, hovertext)
            self.chart.data.append(data_item)

    def setup_data_item(self, style_class, marker, x, array_x, arrayminus_x, y, array_y, arrayminus_y, trace_name, color, hovertext):
        error_x_model = ErrorAxisModel(array=array_x, arrayminus=arrayminus_x)
        error_y_model = ErrorAxisModel(array=array_y, arrayminus=arrayminus_y)
        return ChartDataModel(**style_class.chartdata_dict(), x=x, error_x=error_x_model, y=y, error_y=error_y_model, name=trace_name, marker=marker, hovertext=hovertext)


@dataclass
class PhewasVisualisation(BaseAxesArrayVisualisation):

    def __post_init__(self):
        super().__post_init__()
        self.is_subplot = True
        self.subplot_dimensions = [2, 2]

    def setup_data_item(self, style_class, marker, x, array_x, arrayminus_x, y, array_y, arrayminus_y, trace_name, color, hovertext):
        if self.trace_names.index(trace_name) == 1:
            data_item = ChartDataModel(**style_class.chartdata_dict(), x=x, y=y, name=trace_name, marker=marker, hovertext=hovertext)
            trace_idx = str(self.colors.index(color) + 1)
            data_item.xaxis = "x" + trace_idx
            data_item.yaxis = "y" + trace_idx
            return data_item
        else:
            return super().setup_data_item(style_class, marker, x, array_x, arrayminus_x, y, array_y, arrayminus_y, trace_name, color, hovertext)


@dataclass
class BaseMeasureVisualisation(BaseBuilder, BaseVisualisation):
    """
    Base for waterfall charts.

    Args:
        x_values: Sets the x coordinates, can be a list of lists.
        y_values: Sets the y coordinates.
        name: Sets the trace name.
        measure: An array containing types of values. By default the values are considered as 'relative'. However; it is possible to use 'total' to compute the sums. Also 'absolute' could be applied to reset the computed total or to declare an initial value where needed.
        text: Sets text elements associated with each (x,y) pair.
        textposition: Specifies the location of the `text`. "inside" positions `text` inside, next to the bar end (rotated and scaled if needed). "outside" positions `text` outside, next to the bar end (scaled if needed), unless there is another bar stacked on this one, then the text gets pushed inside. "auto" tries to position `text` inside the bar, but if the bar is too small and no bar is stacked on this one the text is moved outside.

    """
    x_values: List[Any] = field(default_factory=list, repr=False)
    y_values: List[Any] = field(default_factory=list, repr=False)
    measure: List[str] = field(default_factory=list, repr=False)
    text: List[str] = field(default_factory=list, repr=False)
    textposition: str = field(default=Textpositions.NONE.value)
    name: str = field(default=None)
    base: Optional[int] = field(default=None)

    def render(self):
        self.setup_layout()
        self.setup_report()
        self.setup_chart()
        self.setup_visualisation()

    def _validate_input(self):
        """Validates the inputs are of correct lengths"""
        ilists = [self.y_values, self.measure, self.text]
        if all(isinstance(el, list) for el in self.x_values):
            # x_values may be a list of lists, so checks every inner list
            self._validate_list_lengths(*ilists, *self.x_values)
        else:
            self._validate_list_lengths(*ilists, self.x_values)

    def setup_chart(self):
        self._validate_input()
        self.chart = ChartModel(**self.chart_dict())
        data_item = ChartDataModel(
            **self.chartdata_dict(),
            x=self.x_values,
            y=self.y_values,
            measure=self.measure,
            text=self.text,
            textposition=self.textposition,
            name=self.name,
            base=self.base,
        )
        self.chart.data.append(data_item)
        self.report.charts.append(self.chart)


@dataclass
class BasePropVisualisation(BaseBuilder, BaseVisualisation):
    """
    Base Visualisation class for serializing/desializing single charts with proportional data.
    Must be mixed with one of ``BaseMixin`` subclasses to produce a desired chart type.

    Args:
        labels: a list of labels of categories.
        values: a list of values for the labels.
        report_title: title for the Report
        chart_title: title for the Chart
        layout_title: title for the Layout

    """
    labels: List[str] = field(default_factory=list, repr=False)
    values: List[Union[int, float]] = field(default_factory=list, repr=False)
    colors: Optional[List[ColourStr]] = field(default_factory=list, repr=False)

    def render(self):
        self.setup_layout()
        self.layout.update_axes(visible=False)
        self.setup_report()
        self.setup_chart()
        self.setup_visualisation()

    def setup_chart(self):
        self._validate_list_lengths(self.labels, self.values)
        self.chart = ChartModel(**self.chart_dict())
        if not self.colors:
            self.colors = self.cycle_colors(self.COLORS, len(self.labels))
        marker = MarkerModel(**self.marker_dict(), colors=self.colors)
        data_item = ChartDataModel(
            **self.chartdata_dict(),
            labels=self.labels,
            values_=self.values,
            marker=marker
        )
        self.chart.data.append(data_item)
        self.report.charts.append(self.chart)


@dataclass
class BasePropParentVisualisation(BaseBuilder, BaseVisualisation):
    """
    Base Visualisation class for serializing/desializing single charts with proportional data with parents.
    Must be mixed with one of ``BaseMixin`` subclasses to produce a desired chart type.
    For use with Sunburst charts.

    Args:
        labels: lists the labels of sunburst sectors.
        parents: lists the parent sectors of sunburst sectors. An empty string '' is used for the root node in the hierarchy.
        values: lists the values associated with sunburst sectors, determining their width.
        ids: list of ids for the labels of sunburst sectors. Allows the same label to be used in multiple sectors.
        hovertext: list of text feields to use for hovertext.
        colors: optional, a list of colors for use with the chart.
        use_total: set to True if the values include the sum of children (sets branchvalues='total'); default: False.
    """
    labels: List[str] = field(default_factory=list, repr=False)
    values: List[Union[int, float]] = field(default_factory=list, repr=False)
    parents: List[str] = field(default_factory=list, repr=False)
    ids: List[str] = field(default_factory=list, repr=False)
    hovertext: List[str] = field(default_factory=list, repr=False)
    colors: Optional[List[ColourStr]] = field(default_factory=list, repr=False)
    use_total: bool = field(default=False)

    def render(self):
        self.setup_layout()
        self.layout.update_axes(visible=False)
        self.setup_report()
        self.setup_chart()
        self.setup_visualisation()

    def _validate_totals(self):
        """When branchvalues='total', ensure parents have sufficient values of their children"""
        validate_sunburst_total_values(self.labels, self.parents, self.values)

    def setup_chart(self):
        self._validate_list_lengths(
            self.labels, self.values, self.parents, self.ids, self.hovertext)
        extras = {}
        if self.use_total is True:
            self._validate_totals()
            extras['branchvalues'] = 'total'
        if self.hovertext:
            extras['hovertemplate'] = '<b>%{hovertext}</b>'
        self.chart = ChartModel(**self.chart_dict())
        if not self.colors:
            self.colors = self.cycle_colors(self.COLORS, len(self.labels))
        marker = MarkerModel(**self.marker_dict(), colors=self.colors)
        data_item = ChartDataModel(
            **self.chartdata_dict(),
            labels=self.labels,
            values_=self.values,
            parents=self.parents,
            ids=self.ids,
            hovertext=self.hovertext,
            marker=marker,
            **extras
        )
        self.chart.data.append(data_item)
        self.report.charts.append(self.chart)


@dataclass
class BaseStratifiedVisualisation(BaseBuilder, BaseVisualisation):
    """
    Base Stratification Visualisation class for serializing/desializing chart object datas.
    Must be mixed with one of ``BaseMixin`` subclasses to produce a desired chart type.
    The dataframe must of of a special structure. # TODO: visualise the structure.
    Currently only supported for chart types with x and y axes.

    Args:
        df: Datafame with all the data for the chart to be produced from.
        dataseries_name: column name from the ``df``, subject of reporting.
        strata_label: a string with each stratifyable column name in {column_nam} (in curly braces)
        strata_cols: column name from the ``df``, stratification columns.
        strata_factory: optional, for hierarchy use only; a map for strata columns with values for ``StrataFactory`` instances; takes priority over autogeneration for that column in ``strata_cols``.
        report_title: title for the Report
        chart_title: title for the Chart
        layout_title: title for the Layout
        axes_titles: optional, a tuple of two strings, eg: ``(<x-axis-title>, <y-axis-title>)``
        color_dict: a ditionary mapping of ``dataseries_name`` (dict key) for a colour string (dict value).

    Notes:
        - Apart from ``dataseries_name`` and ``strata_cols``, the ``df`` must contain chart data only.
        - The dataframe layout must have these conditions:
            - One row per trace
            - N-columns for stratifications (list in ``strata_cols``)
            - One column for ``dataseries_name`` with column name = name of the study, column values are the trace names
            - Remaining dataframe column names form the X-asis
            - Values in the row contain values for the Y-axis

    Examples:
        Example of the dataframe:
            - Stratified by column(s) is [Gender]
            - dataseries_name is _Medications
        ```
          Gender    _Medications  2015-12  2016-01  2016-02  2016-03  2016-04  2016-05  2016-06
        0    All         Aspirin     4605     4785     4689     4582     4450     4366     4233
        1    All       Ibuprofen     1281     1273     1269     1267     1235     1200     1196
        2    All  Osteoarthritis     4373     4211     4223     4285     4253     4417     4379
        3    All     Paracetamol      177      171      165      169      157      132      137
        4    All        Tramadol     2158     2168     2107     2131     2092     2110     2086
        0      0         Aspirin     1921     2024     1986     1931     1863     1841     1798
        1      0       Ibuprofen      546      564      549      539      526      526      553
        2      0  Osteoarthritis     1669     1601     1587     1590     1581     1654     1691
        3      0     Paracetamol       58       59       57       63       54       44       48
        4      0        Tramadol      778      803      782      798      760      800      791
        5      1         Aspirin     2684     2761     2703     2651     2587     2525     2435
        6      1       Ibuprofen      735      709      720      728      709      674      643
        7      1  Osteoarthritis     2704     2610     2636     2695     2672     2763     2688
        8      1     Paracetamol      119      112      108      106      103       88       89
        9      1        Tramadol     1380     1365     1325     1333     1332     1310     1295
        ```

    """
    df: 'pandas.DataFrame' = field(repr=False, default=None)  # noqa: F821
    dataseries_name: str = field(default='', metadata=dict(required=True))
    strata_label: str = field(default=None)
    strata_cols: List[Any] = field(default_factory=list)
    strata_factory: Dict[Any, Any] = field(default_factory=dict, repr=False)
    color_dict: Dict[str, ColourStr] = field(default_factory=dict, repr=False)
    axes_titles: Optional[Tuple[str, str]] = field(default=None)  # (x, y)

    def render(self):
        self.setup_layout()
        self.setup_report()
        self.setup_stratas()
        self.setup_chart()
        self.setup_visualisation()

    def setup_report(self):
        super().setup_report()
        strata_label = self.strata_label or f"Stratify by {' '.join(f'{s} {{{s}}}' for s in self.strata_cols)}"
        self.report.strata_label = strata_label

    def setup_stratas(self):
        for strata_col in self.strata_cols:
            stratification = StratificationModel(id=strata_col, name=strata_col)
            if strata_col in self.strata_factory:
                stratification.items.extend(self.strata_factory[strata_col].stratas)
                for strata_item in stratification.items:
                    self._strata_map[strata_col][strata_item.name] = strata_item.id
            else:
                for name in self.df[strata_col].unique():
                    if name not in self._strata_map[strata_col]:
                        id_ = len(self._strata_map[strata_col])
                        strata_item = StratumItemModel(id=id_, name=name)
                        self._strata_map[strata_col][strata_item.name] = strata_item.id
                    else:
                        id_ = self._strata_map[strata_col][name]
                        strata_item = StratumItemModel(id=id_, name=name)
                    stratification.items.append(strata_item)
            self._visualisation.stratifications.append(stratification)

    def _data_strata_from_row(self, row: 'pd.Series', drop_items: list) -> Tuple[dict, dict]:  # noqa: F821
        """
        Returns:
            tuple(data:dict, strata:dict)
        """
        datas = json.loads(row.drop(labels=drop_items).to_json())
        stratas = {col: self._strata_map[col][row[col]] for col in self.strata_cols}
        return (datas, stratas)

    def setup_chart(self):
        self.chart = ChartModel(**self.chart_dict())
        _drop_items = [self.dataseries_name] + self.strata_cols

        _last_strata = None
        for _index, row in self.df.iterrows():
            datas, stratas = self._data_strata_from_row(row, _drop_items)
            if _last_strata != stratas:
                _last_strata = stratas
                self.reset_colors()
            color = self.color_dict.get(row[self.dataseries_name], self.next_color())
            marker = MarkerModel(**self.marker_dict(), color=color)
            data_item = ChartDataModel(
                **self.chartdata_dict(),
                x=list(datas.keys()),
                y=list(datas.values()),
                name=row[self.dataseries_name],
                marker=marker,
                stratification=stratas,
            )
            self.chart.data.append(data_item)
        self.report.charts.append(self.chart)


@dataclass
class TableStyleSetter:
    styles: Optional[List[TableStyler]] = field(default_factory=list, repr=False)

    @staticmethod
    def _is_int(x: Any) -> bool:
        return isinstance(x, int)

    @staticmethod
    def _is_slice(x: Any) -> bool:
        return isinstance(x, slice)

    def _process_col(self, style: TableStyler, row_idx: int, col_idx: int) -> None:
        _val = self.chart.data[row_idx].values_[col_idx]
        if isinstance(_val, dict) and 'style' in _val:
            _val['style'].update(style.get_style())
        else:
            _val = dict(style=style.get_style(), value=_val)
        _val.update(style.get_format())
        self.chart.data[row_idx].values_[col_idx] = _val

    def _apply_format(self, style: TableStyler, format_: Union[TableFormatModel, None]) -> TableFormatModel:
        if isinstance(format_, TableFormatModel):
            format_.style.update(style.get_style())
            format_.__dict__.update(style.get_format())
        else:
            format_ = TableFormatModel(style=style.get_style(), **style.get_format())
        return format_

    def _process_row(self, style: TableStyler, row_idx: int) -> None:
        if not style.columns:
            self.chart.data[row_idx].context = style.context
            self.chart.data[row_idx].format = self._apply_format(
                style, self.chart.data[row_idx].format)
        else:
            for col_idx in filter(self._is_int, style.columns):
                self._process_col(style, row_idx, col_idx)
            for col_slice in filter(self._is_slice, style.columns):
                values_indexes = [*range(len(self.chart.data[row_idx].values_))]
                for col_idx in set(values_indexes[col_slice]):
                    self._process_col(style, row_idx, col_idx)

    def setup_styles(self):
        """Runs setting up of styles"""
        for style in self.styles:
            if style.is_global:
                self.chart.format = self._apply_format(style, self.chart.format)
                continue
            for row_idx in filter(self._is_int, style.rows):
                self._process_row(style, row_idx)
            for row_slice in filter(self._is_slice, style.rows):
                data_indexes = [*range(len(self.chart.data))]
                for row_idx in data_indexes[row_slice]:
                    self._process_row(style, row_idx)


@dataclass
class BaseTableVisualisation(BaseBuilder, BaseVisualisation, TableStyleSetter):
    """
    Base builder for creating stratified data tables.

    Args:
        table: a list of list containing values of the table
        row_headers: optional list of vertical row headers, referenced for a column in your dataframe.
        has_header: boolean meaning the first row contains the header titles (default True)
        axes_titles: optional x and y ases titles
        styles: optional list of styles to apply to the tables

    """
    table: List[List[Any]] = field(default_factory=list, repr=False)
    row_headers: List[Any] = field(default_factory=list)
    has_header: bool = True
    axes_titles: Optional[Tuple[str, str]] = field(default=None)  # (x, y)

    def render(self):
        self.setup_layout()
        self.setup_report()
        self.setup_chart()
        self.setup_styles()
        self.setup_visualisation()

    def _append_data_item(self, values, **kwargs):
        data_item = ChartDataModel(
            **self.chartdata_dict(),
            values_=values,
            **kwargs
        )
        self.chart.data.append(data_item)

    def setup_chart(self):
        self.chart = ChartModel(**self.chart_dict())
        values_iter = iter(self.table)
        if self.has_header is True:
            self._append_data_item(
                next(values_iter),
                headers=self.row_headers,
                is_header_row=True
            )
        for vals in values_iter:
            self._append_data_item(vals, headers=self.row_headers)
        self.report.charts.append(self.chart)

    @classmethod
    def from_df(cls, df: 'pandas.DataFrame', has_header=True, **kwargs):  # noqa: F821
        table = df.values.tolist()
        if has_header is True:
            table.insert(0, df.columns.values.tolist())
        return cls(
            table=table,
            has_header=has_header,
            **kwargs
        )

    def as_plotly(self, **kwargs):
        raise NotImplementedError('Converting to Plotly is not supported by this Visualisation class.')


@dataclass
class BaseStratifiedTableVisualisation(BaseStratifiedVisualisation, BaseTableVisualisation, TableStyleSetter):
    """
    Base builder for creating stratified data tables.

    Args:
        df: Datafame with all the data for the chart to be produced from.
        row_headers: optional list of vertical row headers, referenced for a column in your dataframe.
        strata_label: a string with each stratifyable column name in {column_nam} (in curly braces).
        strata_cols: column name from the ``df``, stratification columns.
        strata_factory: optional, for hierarchy use only; a map for strata columns with values for ``StrataFactory`` instances; takes priority over autogeneration for that column in ``strata_cols``.
        axes_titles: optional, a tuple of two strings, eg: ``(<x-axis-title>, <y-axis-title>)``
        has_header: boolean meaning the first row contains the header titles (default True)
    """

    def setup_chart(self):
        self.chart = ChartModel(**self.chart_dict())
        _drop_items = [*self.row_headers, *self.strata_cols]

        if self.has_header is True:
            row = self.df.iloc[0]
            datas, _ = self._data_strata_from_row(row, _drop_items)
            self._append_data_item(
                list(datas.keys()),
                is_header_row=True,
                headers=self.row_headers
            )
        for _index, row in self.df.iterrows():
            datas, stratas = self._data_strata_from_row(row, _drop_items)
            self._append_data_item(
                list(datas.values()),
                headers=[row[h] for h in self.row_headers],
                stratification=stratas
            )
        self.report.charts.append(self.chart)

    @classmethod
    def from_df(cls, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover


@dataclass
class BaseMeasureStratifiedVisualisation(BaseStratifiedVisualisation, BaseMeasureVisualisation):
    """
    Builder for a stratified measure visualisation.

    ``measures_map`` needs to be created in advance and passed as a parameter.
    Use dataframe header names as keys and ``charting.Measures`` for the values.
    Example:
        ```python
        measures_map = {
            "Add-on": Measures.RELATIVE.value,
            "Switch-Off": Measures.ABSOLUTE.value
        }
        ```

    Dataframe example:
        ```
          Gender  Location     Date  Medications  Opening  Add-on  Switch-Off
        0    All       All  2017-07      Aspirin        7       2           2
        1    All   England  2017-07      Aspirin        5       1           1
        0   Male       All  2017-07      Aspirin        5       2           2
        1   Male   England  2017-07      Aspirin        4       1           1
        0 Female       All  2017-07      Aspirin        3       1           1
        1 Female   England  2017-07      Aspirin        2       0           0
        ```

    Args:
        df: Datafame with all the data for the chart to be produced from.
        dataseries_name: column name from the ``df``, subject of reporting.
        strata_label: a string with each stratifyable column name in {column_nam} (in curly braces)
        strata_cols: column name from the ``df``, stratification columns.
        strata_factory: optional, for hierarchy use only; a map for strata columns with values for ``StrataFactory`` instances; takes priority over autogeneration for that column in ``strata_cols``.
        measures_map: a mapping for _change_ column to ``Measures`` values; default `Measures.RELATIVE`
        base_col: column name with the opening value for the chart
        report_title: title for the Report
        chart_title: title for the Chart
        layout_title: title for the Layout

    """
    measures_map: Dict[str, Measures] = field(default_factory=dict)
    base_col: str = field(default=None)

    def _validate_inputs(self):
        # Check measures_map contains valid values
        if self.measures_map and not all(map(lambda x: isinstance(x, Measures), self.measures_map.values())):
            raise ValueError('All values in `measures_map` must be of a `Measures` enum option.')

    def setup_chart(self):
        self.chart = ChartModel(**self.chart_dict())
        _drop_items = [*filter(lambda x: x is not None, {
            self.dataseries_name, self.base_col, *self.strata_cols
        })]
        self._validate_inputs()

        for _index, row in self.df.iterrows():
            datas, stratas = self._data_strata_from_row(row, _drop_items)
            measures = [str(self.measures_map.get(key, Measures.RELATIVE)) for key in datas.keys()]
            data_item = ChartDataModel(
                **self.chartdata_dict(),
                x=list(datas.keys()),
                y=list(datas.values()),
                measure=measures,
                name=row.get(self.dataseries_name),
                stratification=stratas,
                textposition=self.textposition,
                base=row.get(self.base_col),
            )
            self.chart.data.append(data_item)
        self.report.charts.append(self.chart)


@dataclass
class BaseAxesArrayStratifiedVisualisation(BaseStratifiedVisualisation):

    keys_col: str = field(default=None)
    error_x_cols: List[Any] = field(default_factory=list)
    errorminus_x_cols: List[Any] = field(default_factory=list)
    error_y_cols: List[Any] = field(default_factory=list)
    errorminus_y_cols: List[Any] = field(default_factory=list)
    inverse_axes: bool = field(default=False)

    def _validate_inputs(self):
        if not ((self.error_x_cols and self.errorminus_x_cols) or (self.error_y_cols and self.errorminus_y_cols)):
            raise ValueError('Error bar columns for x or y not present')

    def setup_chart(self):
        self._validate_inputs()
        self.chart = ChartModel(**self.chart_dict())
        _drop_items = [self.dataseries_name] + self.strata_cols + self.error_x_cols + self.errorminus_x_cols + self.error_y_cols + self.errorminus_y_cols

        _last_strata = None
        for _index, row in self.df.iterrows():
            datas, stratas = self._data_strata_from_row(row, _drop_items)
            error_x = ErrorAxisModel()
            error_y = ErrorAxisModel()
            if self.error_x_cols:
                minus_values = row[self.errorminus_x_cols] if (row[self.errorminus_x_cols] > 0).all() else row[self.errorminus_x_cols].multiply(-1)
                error_x = ErrorAxisModel(array=row[self.error_x_cols], arrayminus=minus_values)
            if self.error_y_cols:
                minus_values = row[self.errorminus_y_cols] if (row[self.errorminus_y_cols] > 0).all() else row[self.errorminus_y_cols].multiply(-1)
                error_y = ErrorAxisModel(array=row[self.error_y_cols], arrayminus=minus_values)
            if _last_strata != stratas:
                _last_strata = stratas
                self.reset_colors()
            color = self.color_dict.get(row[self.dataseries_name], self.next_color())
            marker = MarkerModel(**self.marker_dict(), color=color)
            group_label = {row[self.keys_col]: ""}.keys() if self.keys_col else datas.keys()
            data_item = ChartDataModel(
                **self.chartdata_dict(),
                x=list(datas.values() if self.inverse_axes else group_label),
                y=list(group_label if self.inverse_axes else datas.values()),
                error_x=error_x,
                error_y=error_y,
                name=row[self.dataseries_name],
                marker=marker,
                stratification=stratas,
            )
            self.chart.data.append(data_item)
        self.report.charts.append(self.chart)


@dataclass
class BaseLinkVisualisation(BaseBuilder, BaseVisualisation):
    """
    Base class used for Sankey charts.

    Args:
        source: list of positional values (as integers) for sources (from)
        target: list of positional values (as integers) for targets (to)
        values: list of integers for values of the link (value of the source to target)
        link_colors: optional, list of color names/codes for the link
        link_labels: optional, description for each source/target instance
        labels: list of label names, list positions corresponding to positional value for source/target
        link_hoverlabel: optional, dictionary with hover label properties
        node_hoverlabel: optional, dictionary with hover label properties
        node_x: optional, list of float value, x-axes position for where to plot the node labels (position ranges: 0.0-1.0)
        node_y: optional, list of float value, y-axes position for where to plot the node labels (position ranges: 0.0-1.0)
        node_colors: optional, list of colours to match the labels; when not provided, auto-colours are given.
        link_auto_color: boolean, assigns colours to Links from the main colour pallet.

    """
    # Link inputs
    source: List[int] = field(default_factory=list, repr=False)
    target: List[int] = field(default_factory=list, repr=False)
    values: List[int] = field(default_factory=list, repr=False)
    link_colors: Optional[List[ColourStr]] = field(default_factory=list, repr=False)
    link_labels: Optional[List[str]] = field(default_factory=list, repr=False)
    link_customdata: Optional[List[str]] = field(default_factory=list, repr=False)
    link_hoverlabel: Optional[DictAny] = field(default_factory=dict, repr=False)
    link_hovertemplate: str = field(default=None)
    # Node inputs
    labels: List[str] = field(default_factory=list, repr=False)
    node_x: Optional[List[float]] = field(default_factory=list, repr=False)
    node_y: Optional[List[float]] = field(default_factory=list, repr=False)
    node_colors: Optional[List[ColourStr]] = field(default_factory=list, repr=False)
    node_customdata: Optional[List[str]] = field(default_factory=list, repr=False)
    node_hoverlabel: Optional[DictAny] = field(default_factory=dict, repr=False)
    node_hovertemplate: str = field(default=None)
    # Options
    link_auto_color: bool = False

    def render(self):
        self.setup_layout()
        self.setup_report()
        self.setup_chart()

    def setup_chart(self):
        self._validate_list_lengths(self.source, self.target, self.values, self.link_labels, self.link_colors, self.link_customdata)  # Link object input validation
        self._validate_list_lengths(self.labels, self.node_x, self.node_y, self.node_colors, self.node_customdata)  # Node object input validation
        self.chart = ChartModel(**self.chart_dict())
        if (not self.link_colors) and self.link_auto_color is True:
            self.link_colors = self.cycle_colors(self.COLORS_LINK, len(self.source))
        if not self.node_colors:
            self.node_colors = self.cycle_colors(self.COLORS_NODE, len(self.labels))

        link = LinkModel(
            source=self.source,
            target=self.target,
            value=self.values,
            label=self.link_labels,
            color=self.link_colors,
            customdata=self.link_customdata,
            hoverlabel=self.link_hoverlabel,
            hovertemplate=self.link_hovertemplate,
        )
        node = NodeModel(
            **self.node_dict(),
            label=self.labels,
            color=self.node_colors,
            customdata=self.node_customdata,
            hoverlabel=self.node_hoverlabel,
            hovertemplate=self.node_hovertemplate,
            x=self.node_x,
            y=self.node_y,
        )

        chart_data = ChartDataModel(**self.chartdata_dict(), link=link, node=node)
        self.chart.data.append(chart_data)

        self.report.charts.append(self.chart)
        self._visualisation.reports.append(self.report)

    @classmethod
    def from_df(cls, df: 'pandas.DataFrame', source_col: str, target_col: str, value_col: str, **kwargs):  # noqa: F821
        """
        Args:
            df: the dataframe
            source_col: column name of the source (from) column
            target_col: column name of the target (to) colums
            value_col: column name with the values
            labels: list of label names
            **kwargs: passed to the main class
        """
        vals = df[[source_col, target_col]].values.ravel()
        maps = {name: n for (n, name) in enumerate(set(vals))}
        return cls(
            source=df[source_col].map(maps).to_list(),
            target=df[target_col].map(maps).to_list(),
            values=df[value_col].to_list(),
            labels=list(maps.keys()),
            **kwargs
        )


# --- CONVERTERS --------------------------------------------------------------

@dataclass
class PlotlyConverter:
    """
    Converts VRS visualisation objects to plain plotly.
    Use class methods ``dump`` or ``json`` to get the dict or json objects.
    """
    _vis: BaseVisualisation
    report_idx: int = 0
    chart_idx: int = 0
    data_limit: int = 100
    height: int = 900
    width: int = 1200

    def __post_init__(self):
        self.vis = self._vis.copy()
        _report = self.vis.visualisation.reports[self.report_idx]
        _chart = _report.charts[self.chart_idx]
        _layout = _report.layout.convert_for_plotly(
            height=self.height, width=self.width, title=_report.name)
        _datas = _chart.data[:self.data_limit].copy()
        _datas = [_data.convert_for_plotly(type=_chart.type) for _data in _datas]

        self.plotly_payload = _PlotlyPayloadModel(data=_datas, layout=_layout)

    def dump(self) -> dict:
        return self.plotly_payload.Schema().dump(self.plotly_payload)

    def json(self, **kwargs) -> str:
        return self.plotly_payload.Schema().dumps(self.plotly_payload, **kwargs)
