import datetime
import marshmallow_dataclass
from typing import List, Dict, Any, Optional, Union, NewType
from dataclasses import field
from marshmallow import Schema, post_dump, validate, INCLUDE
from .common import BaseEnum, ColorsNormalExt

ColourStr = NewType('ColourStr', str)
DictAny = NewType('DictAny', Dict[str, Any])

# --- SERIALIZERS -------------------------------------------------------------


class BaseSchema(Schema):
    SKIP_VALUES = [None, [], {}]

    class Meta:
        ordered = True
        unknown = INCLUDE

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return self._remove_skip_values(data)

    @classmethod
    def _remove_skip_values(cls, obj):
        if isinstance(obj, list):
            return [*map(cls._remove_skip_values, obj)]
        elif isinstance(obj, dict):
            return {k: cls._remove_skip_values(v) for k, v in obj.items() if v not in cls.SKIP_VALUES}
        return obj


class Measures(BaseEnum):
    """Used with waterfall"""
    RELATIVE = 'relative'
    ABSOLUTE = 'absolute'
    TOTAL = 'total'


class Textpositions(BaseEnum):
    """Used with waterfall"""
    INSIDE = "inside"
    OUTSIDE = "outside"
    AUTO = "auto"
    NONE = "none"


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class LinkModel:
    source: List[Any] = field(default_factory=list)  # indices correspond to NodeModel.label
    target: List[Any] = field(default_factory=list)
    value: List[Any] = field(default_factory=list)
    label: List[str] = field(default_factory=list)
    color: List[ColourStr] = field(default_factory=list)
    customdata: Optional[List[str]] = field(default_factory=list)
    hoverlabel: DictAny = field(default_factory=dict)
    hovertemplate: str = field(default=None)


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class NodeModel:
    x: List[float] = field(default_factory=list)
    y: List[float] = field(default_factory=list)
    label: List[str] = field(default_factory=list)
    color: Optional[Union[List[str], str]] = field(default=None)
    customdata: Optional[List[str]] = field(default_factory=list)
    pad: Optional[int] = field(default=None)
    thickness: Optional[int] = field(default=None)
    line: Optional[DictAny] = field(default=None)
    hoverlabel: DictAny = field(default_factory=dict)
    hovertemplate: str = field(default=None)


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class MarkerModel:
    opacity: Optional[float] = field(default=None)
    symbol: Optional[List[int]] = field(default=None)
    color: Optional[ColourStr] = field(default=None)
    colors: Optional[List[ColourStr]] = field(default_factory=list)


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class TableFormatModel:
    style: Optional[DictAny] = field(default_factory=dict)
    type: Optional[str] = field(default=None)
    format: Optional[str] = field(default=None)


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class ErrorAxisModel:
    type: Optional[str] = field(default='data')
    visible: Optional[bool] = field(default=True)
    symmetric: Optional[bool] = field(default=False)
    array: Optional[List[Any]] = field(default_factory=list)
    arrayminus: Optional[List[Any]] = field(default_factory=list)


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class ChartDataModel:
    x: List[Any] = field(default_factory=list)
    y: List[Any] = field(default_factory=list)
    z: Optional[List[Any]] = field(default=None)
    error_x: Optional[ErrorAxisModel] = field(default=None)
    error_y: Optional[ErrorAxisModel] = field(default=None)
    xaxis: Optional[str] = field(default=None)
    yaxis: Optional[str] = field(default=None)
    labels: List[Any] = field(default_factory=list)
    values_: List[Any] = field(default_factory=list, metadata=dict(data_key='values'))
    parents: List[Any] = field(default_factory=list)
    hovertext: List[Any] = field(default_factory=list)
    ids: List[Any] = field(default_factory=list)
    measure: List[str] = field(default_factory=list, metadata=dict(validate=validate.ContainsOnly(Measures.to_list())))
    text: List[str] = field(default_factory=list)
    name: str = field(default=None)
    branchvalues: Optional[str] = field(default=None)
    link: Optional[LinkModel] = field(default=None)
    node: Optional[NodeModel] = field(default=None)
    hoverinfo: Optional[str] = field(default=None)
    hovertemplate: Optional[str] = field(default=None)
    textinfo: Optional[str] = field(default=None)
    hole: Optional[float] = field(default=None)
    line: Optional[DictAny] = field(default=None)
    totals: Optional[DictAny] = field(default=None)
    increasing: Optional[DictAny] = field(default=None)
    decreasing: Optional[DictAny] = field(default=None)
    marker: Optional[MarkerModel] = field(default=None)
    fill: Optional[str] = field(default=None)
    mode: Optional[str] = field(default=None)
    orientation: Optional[str] = field(default=None)
    arrangement: Optional[str] = field(default=None)
    valueformat: Optional[str] = field(default=None)
    textposition: Optional[str] = field(default=None, metadata=dict(validate=validate.OneOf(Textpositions.to_list())))
    base: Optional[int] = field(default=None)
    showlegend: Optional[bool] = field(default=None)
    type: Optional[str] = field(default=None)  # only for use of backwards plotly regeneration
    headers: Optional[List[str]] = field(default_factory=list)
    is_header_row: Optional[bool] = field(default=None, metadata=dict(data_key='isHeaderRow'))
    format: Optional[TableFormatModel] = field(default=None)
    context: Optional[str] = field(default=None)
    stratification: DictAny = field(default_factory=dict, metadata=dict(plotly_exclude=True))
    domain: Optional[DictAny] = field(default=None)
    textfont: Optional[DictAny] = field(default=None)
    box: Optional[DictAny] = field(default=None)
    boxpoints: Optional[bool] = field(default=None)
    meanline: Optional[DictAny] = field(default=None)
    colorscale: Optional[List[list]] = field(default=None)
    colorbar: Optional[DictAny] = field(default=None)

    def convert_for_plotly(self, **kwargs: Any):
        for key, value in kwargs.items():
            if key in self.__dict__:
                self.__dict__[key] = value
        for field_key, field_value in self.__dataclass_fields__.items():
            if field_value.metadata.get('plotly_exclude'):
                setattr(self, field_key, None)
        return self


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class ChartModel:
    type: str = field(init=True, metadata=dict(required=True))  # Define the plotly chart type, such as bar, pie, etc.
    id: str = field(default='chart1')  # Optional?
    data: List[Union[ChartDataModel, DictAny]] = field(default_factory=list, repr=False, metadata=dict(validate=validate.Length(min=1)))
    mode: Optional[str] = field(default=None)
    data_count: Optional[int] = field(default=None, metadata=dict(data_key='dataCount'))
    format: Optional[TableFormatModel] = field(default=None)


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class AnnotationModel:
    """
    Most common used annotations types.
    For extending this model, refer to: https://plotly.com/python/reference/layout/annotations/
    """
    text: str = field(default='')
    x: Any = field(default=None)
    y: Any = field(default=None)
    width: int = field(default=None)
    height: int = field(default=None)
    xref: str = field(default='paper')  # ( "paper" | "/^x([2-9]|[1-9][0-9]+)?( domain)?$/" )
    yref: str = field(default='paper')  # ( "paper" | "/^y([2-9]|[1-9][0-9]+)?( domain)?$/" )
    xanchor: str = field(default=None)  # ( "auto" | "left" | "center" | "right" )
    yanchor: str = field(default=None)  # ( "auto" | "top" | "middle" | "bottom" )
    xshift: int = field(default=None)
    yshift: int = field(default=None)
    optacity: float = field(default=None)  # ( 0.0 .. 1.0 )
    bgcolor: ColourStr = field(default=None)
    bordercolor: ColourStr = field(default=None)
    borderpad: int = field(default=None)
    borderwidth: int = field(default=None)
    align: str = field(default=None)  # ( "left" | "center" | "right" )
    valign: str = field(default=None)  # ( "top" | "middle" | "bottom" )
    font: DictAny = field(default_factory=dict)
    textangle: int = field(default=None)  # ( 0 .. 360 )
    showarrow: bool = field(default=False)
    arrowcolor: ColourStr = field(default=None)
    visible: bool = field(default=True)


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class GridModel:
    pattern: str = field(default='independent')
    rows: int = field(default=1)
    columns: int = field(default=2)


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class LayoutModel:
    title: Union[str, DictAny] = field(default='', metadata=dict(required=False))
    xaxis: DictAny = field(default_factory=lambda: dict(visible=True, showline=True))
    yaxis: DictAny = field(default_factory=lambda: dict(visible=True, showline=True))
    xaxis2: Optional[DictAny] = field(default=None)
    yaxis2: Optional[DictAny] = field(default=None)
    xaxis3: Optional[DictAny] = field(default=None)
    yaxis3: Optional[DictAny] = field(default=None)
    xaxis4: Optional[DictAny] = field(default=None)
    yaxis4: Optional[DictAny] = field(default=None)
    grid: Optional[GridModel] = field(default=None)
    font: Optional[DictAny] = field(default_factory=dict)
    titlefont: Optional[DictAny] = field(default_factory=lambda:
        dict(color=ColorsNormalExt.BLUE, size=20))
    plot_bgcolor: ColourStr = field(default=ColorsNormalExt.WHITE)
    annotations: Optional[List[AnnotationModel]] = field(default_factory=list)
    height: int = field(default=700)
    width: int = field(default=1200)
    autosize: bool = field(default=True)
    barmode: Optional[str] = field(default=None)
    margin: Optional[DictAny] = field(default_factory=dict)
    shapes: Optional[List[DictAny]] = field(default_factory=list)
    updatemenus: Optional[List[DictAny]] = field(default_factory=list)
    waterfallgroupgap: Optional[float] = field(default=None)

    def convert_for_plotly(self, **kwargs: Any):
        for key, value in kwargs.items():
            if key in self.__dict__:
                self.__dict__[key] = value
        self.autosize = False
        return self

    def update_axes(self, **kwargs: dict):
        self.xaxis.update(kwargs)
        self.yaxis.update(kwargs)

    def add_axes_titles(self, xaxis_title: str, yaxis_title: str):
        self.xaxis['title'], self.yaxis['title'] = xaxis_title, yaxis_title

    def set_data_points(self, data_len: int, horizontal=True):
        if horizontal:
            if data_len > 500:
                self.xaxis['dtick'] = 100
            elif data_len > 50:
                self.xaxis['dtick'] = 10
        else:
            if data_len > 500:
                self.yaxis['dtick'] = 100
            elif data_len > 50:
                self.yaxis['dtick'] = 10


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class ReportModel:
    id: str = field(default='report1')
    name: str = field(default='')
    layout: Union[LayoutModel, DictAny] = field(default_factory=dict, metadata=dict(required=False))
    charts: List[ChartModel] = field(default_factory=list, metadata=dict(validate=validate.Length(min=1)))
    strata_label: str = field(default=None, metadata=dict(data_key='stratificationLabel'))


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class StratumItemModel:
    id: int = field(default=0)
    name: str = field(default='')
    parent_id: int = field(default=None, metadata=dict(data_key='parentId'))


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class StratificationModel:
    id: str = field(default='')
    name: str = field(default='')
    items: List[StratumItemModel] = field(default_factory=list, repr=False)


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class VisualisationModel:
    reports: List[ReportModel] = field(default_factory=list, metadata=dict(validate=validate.Length(min=1)))
    stratifications: List[StratificationModel] = field(default_factory=list)
    id: str = field(default=None, metadata=dict(load_only=True))
    status: Any = field(default=None, metadata=dict(load_only=True))
    message: str = field(default=None, metadata=dict(load_only=True))
    version: int = field(default=None, metadata=dict(load_only=True))
    created: datetime.datetime = field(default=None, metadata=dict(load_only=True))
    updated: datetime.datetime = field(default=None, metadata=dict(load_only=True))


@marshmallow_dataclass.dataclass(base_schema=BaseSchema)
class _PlotlyPayloadModel:
    """
    Private model for mapping to plain Plotly objects
    """
    data: List[ChartDataModel]
    layout: LayoutModel
