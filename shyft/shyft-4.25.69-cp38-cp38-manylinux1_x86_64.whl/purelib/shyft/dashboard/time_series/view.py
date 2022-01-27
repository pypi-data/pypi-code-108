from typing import Dict, List, Optional, Tuple, Type, Union

from shyft.dashboard.time_series.state import Unit
from shyft.dashboard.base.hashable import Hashable
from shyft.dashboard.time_series.bindable import Bindable
from shyft.dashboard.time_series.renderer import (BaseFigureRenderer, FillInBetweenRenderer, LineRenderer,
                                                  CircleScatterRenderer, SquareScatterRenderer, TriangleScatterRenderer,
                                                  VALID_LINE_STYLES, DiamondScatterRenderer, BackgroundDataRenderer,
                                                  MultiLineRenderer)
from shyft.dashboard.time_series.attr_callback_manager import AttributeCallbackManager
from shyft.dashboard.time_series.axes import YAxis

base_view_container = 'shyft.dashboard.time_series.view_container.view_container_base.BaseViewContainer'
figure_container = 'shyft.dashboard.time_series.view_container.figure.Figure'
legend_container = 'shyft.dashboard.time_series.view_container.legend.Legend'
table_container = 'shyft.dashboard.time_series.view_container.table.Table'


class ViewError(RuntimeError):
    pass


class BaseView(Hashable, Bindable, AttributeCallbackManager):
    """
    This object represents the immutable, hashable view base which can be used as dict keys
    """

    def __init__(self, *, view_container: base_view_container, label: str, visible: bool = True,
                 tooltips: Optional[List[Tuple[str, str]]] = None) -> None:
        """
        Base class of all views, makes no sense to use it on its own.

        Parameters
        ----------
        view_container: view_container
        label: label of the view
        visible: visibility of the view
        """
        AttributeCallbackManager.__init__(self)
        Hashable.__init__(self)
        Bindable.__init__(self)

        self.__view_container = view_container
        self.label = label
        self.visible = visible
        self.tooltips = tooltips

    @property
    def view_container(self) -> base_view_container:
        return self.__view_container


class LegendItem(BaseView):
    """
    This object defines the data legend view
    """

    def __init__(self, *, view_container: legend_container, label: str, views: List[BaseView], expanded: Optional[bool] = None) -> None:
        """
        Legend Item to show in the given legend: view_container

        Parameters
        ----------
        view_container: Legend instance where to add this legend item
        label: label in the legend
        views: all views which are represented by this legend item (will be used to trigger visibility)

        Notes
        -----
        One view can be in several LegendItem s but this might lead to strange behaviour
        """
        if not label:
            label = ', '.join([v.label for v in views])
        super().__init__(view_container=view_container, label=label, visible=True)
        self.views = views
        self.expanded = expanded


class TableView(BaseView):
    """
    This object defines the data for table view
    """

    def __init__(self, *, view_container: table_container, label: str, unit: Unit, columns: Dict[int, str] = None,
                 visible: bool = True) -> None:
        """
        View defining one or more colums in the provided table, view_container,

        Parameters
        ----------
         view_container:
            Figure view container where to plot the renderer of the view
        label:
            main label of the view
        unit:
            unit of the data in the columns
        visible:
            controls the visibility of all columns
        columns:
            Dict[index:int, column_label:str] defines all columns a la:
            index of the time series in the ts_vector to add
            column_label of the specific column


        Notes
        -----
        The following values can be changed from the outside during runtime:
            visible, unit
        Final column labels are combined from label + column_label.
        """
        super().__init__(view_container=view_container, label=label, visible=visible)
        self.columns = columns or {}
        self.unit = unit


class FigureView(BaseView):
    """
    This is the base class of all figure views
    """

    def __init__(self, *, view_container: figure_container, color: str, label: str,
                 renderer_class: Type[BaseFigureRenderer],
                 unit: Unit, no_y_rescaling: Optional[bool] = False, visible: bool = True,
                 y_axis: Optional[YAxis] = None, tooltips: List[Tuple[str, str]] = None):
        """
        Base class for figure views, makes no sens to initialize this class by it self

        Parameters
        ----------
        view_container: Figure view container where to plot the renderer of the view
        color: Color of the filling
        label: label of the view
        unit: unit of the data in the renderer
        no_y_rescaling: If data should be used for y axis rescaling
        visible: controls the visiblity of the renderer
        y_axis: defines on which YAxis the renderer should be plotted

        Notes
        -----
        The following values can be changed from the outside during runtime:
            color, label, unit, visible
        """
        super().__init__(view_container=view_container, label=label, visible=visible, tooltips=tooltips)
        # immutable attrs
        self.__renderer_class = renderer_class
        self.__y_axis = y_axis

        # mutable attrs
        self.color = color
        self.no_y_rescaling = no_y_rescaling
        self.unit = unit

    @property
    def renderer_class(self) -> Type[BaseFigureRenderer]:
        return self.__renderer_class

    @property
    def y_axis(self) -> YAxis:
        return self.__y_axis


class Line(FigureView):
    """
    This object contains all data for line view
    """

    def __init__(self, *, view_container: figure_container, color: str, label: str, unit: Unit,
                 index: int, no_y_rescaling: Optional[bool] = False, visible: bool = True,
                 y_axis: Optional[YAxis] = None, line_style: str = 'solid',
                 line_width: float = 2., tooltips: List[Tuple[str, str]] = None):
        """
        Plots a line for a time series with the index in the ts-vector from the data source

        Parameters
        ----------
        view_container: Figure view container where to plot the renderer of the view
        color: color of the line
        label: label of the view
        unit: unit of the data in the renderer
        index: index defining the time series in the ts-vector
        no_y_rescaling: If data should be used for y axis rescaling
        visible: controls the visiblity of the renderer
        y_axis: defines on which YAxis the renderer should be plotted
        line_width: line width of the line

        Notes
        -----
        The following values can be changed from the outside during runtime:
            color, label, unit, indices, visible
        """
        tooltips = tooltips or [("label", "@label")]
        super().__init__(view_container=view_container, color=color, label=label, unit=unit,
                         no_y_rescaling=no_y_rescaling, visible=visible, renderer_class=LineRenderer,
                         y_axis=y_axis, tooltips=tooltips)
        self.index = index
        if line_style not in VALID_LINE_STYLES:
            raise ViewError(f'view {label} in {view_container}: line_style {line_style} not in {VALID_LINE_STYLES}')
        self.line_style = line_style
        self.line_width = line_width


class Scatter(FigureView):
    """
        This object contains all data for a scatter view
        """

    def __init__(self, *, view_container: figure_container, color: str, label: str, unit: Unit,
                 index: int, renderer_class: Union[Type[DiamondScatterRenderer],
                                                   Type[CircleScatterRenderer],
                                                   Type[SquareScatterRenderer],
                                                   Type[TriangleScatterRenderer]],
                 no_y_rescaling: Optional[bool] = False, visible: bool = True, size: int = 4,
                 fill_color: str = None, fill_alpha: float = 1., line_alpha: float = 1.,
                 y_axis: Optional[YAxis] = None, tooltips: List[Tuple[str, str]] = None):
        """
        Plots a line for a time series with the index in the ts-vector from the data source

        Parameters
        ----------
        view_container:
            Figure view container where to plot the renderer of the view
        color:
            color of the line
        renderer_class:
            defines which scatter it is going to be
        fill_color:
            fill_color of the scatter
        fill_alpha:
            alpha transparency of the scatter fill_color
        line_alpha:
            alpha transparency of the scatter line
        label:
            label of the view
        unit:
            unit of the data in the renderer
        index:
            index defining the time series in the ts-vector
        no_y_rescaling:
            If data should be used for y axis rescaling
        visible:
            controls the visibility of the renderer
        y_axis:
            defines on which YAxis the renderer should be plotted
        size:
            defines the size of the scatter

        Notes
        -----
        The following values can be changed from the outside during runtime:
            color, label, unit, indices, visible, size, fill_color, fill_alpha, line_alpha
        """
        expected_renderer_class = [DiamondScatterRenderer, CircleScatterRenderer, SquareScatterRenderer,
                                   TriangleScatterRenderer]
        if renderer_class not in expected_renderer_class:
            raise ValueError(f"Scatter: expected renderer class should be one of {expected_renderer_class}, "
                             f"got {renderer_class}")
        super().__init__(view_container=view_container, color=color, label=label, unit=unit,
                         no_y_rescaling=no_y_rescaling, visible=visible, renderer_class=renderer_class,
                         y_axis=y_axis, tooltips=tooltips)
        self.index = index
        self.line_style = ""
        self.size = size
        self.fill_color = fill_color
        self.fill_alpha = fill_alpha
        self.line_alpha = line_alpha


class DiamondScatter(Scatter):
    """
    This object contains all data for diamond view
    """

    def __init__(self, *, view_container: figure_container, color: str, label: str, unit: Unit,
                 index: int, no_y_rescaling: Optional[bool] = False, visible: bool = True, size: int = 4,
                 fill_color: str = None, fill_alpha: float = 1., line_alpha: float = 1.,
                 y_axis: Optional[YAxis] = None, tooltips: List[Tuple[str, str]] = None):
        """
        Plots a line for a time series with the index in the ts-vector from the data source

        Parameters
        ----------
        view_container:
            Figure view container where to plot the renderer of the view
        color:
            color of the line
        fill_color:
            fill_color of the scatter
        fill_alpha:
            alpha transparency of the scatter fill_color
        line_alpha:
            alpha transparency of the scatter line
        label:
            label of the view
        unit:
            unit of the data in the renderer
        index:
            index defining the time series in the ts-vector
        no_y_rescaling:
            If data should be used for y axis rescaling
        visible:
            controls the visibility of the renderer
        y_axis:
            defines on which YAxis the renderer should be plotted
        size:
            defines the size of the scatter

        Notes
        -----
        The following values can be changed from the outside during runtime:
            color, label, unit, indices, visible, size, fill_color, fill_alpha, line_alpha
        """
        super().__init__(view_container=view_container, color=color, label=label, unit=unit,
                         index=index, size=size, fill_color=fill_color, fill_alpha=fill_alpha, line_alpha=line_alpha,
                         no_y_rescaling=no_y_rescaling, visible=visible, renderer_class=DiamondScatterRenderer,
                         y_axis=y_axis, tooltips=tooltips)


class CircleScatter(Scatter):
    """
    This object contains all data for diamond view
    """

    def __init__(self, *, view_container: figure_container, color: str, label: str, unit: Unit,
                 index: int, no_y_rescaling: Optional[bool] = False, visible: bool = True, size: int = 4,
                 fill_color: str = None, fill_alpha: float = 1., line_alpha: float = 1.,
                 y_axis: Optional[YAxis] = None, tooltips: List[Tuple[str, str]] = None):
        """
        Plots a line for a time series with the index in the ts-vector from the data source

        Parameters
        ----------
        view_container:
            Figure view container where to plot the renderer of the view
        color:
            color of the line
        fill_color:
            fill_color of the scatter
        fill_alpha:
            alpha transparency of the scatter fill_color
        line_alpha:
            alpha transparency of the scatter line
        label:
            label of the view
        unit:
            unit of the data in the renderer
        index:
            index defining the time series in the ts-vector
        no_y_rescaling:
            If data should be used for y axis rescaling
        visible:
            controls the visibility of the renderer
        y_axis:
            defines on which YAxis the renderer should be plotted
        size:
            defines the size of the scatter

        Notes
        -----
        The following values can be changed from the outside during runtime:
            color, label, unit, indices, visible, size, fill_color, fill_alpha, line_alpha
        """
        super().__init__(view_container=view_container, color=color, label=label, unit=unit,
                         index=index, size=size, fill_color=fill_color, fill_alpha=fill_alpha, line_alpha=line_alpha,
                         no_y_rescaling=no_y_rescaling, visible=visible, renderer_class=CircleScatterRenderer,
                         y_axis=y_axis, tooltips=tooltips)


class SquareScatter(Scatter):
    """
    This object contains all data for diamond view
    """

    def __init__(self, *, view_container: figure_container, color: str, label: str, unit: Unit,
                 index: int, no_y_rescaling: Optional[bool] = False, visible: bool = True, size: int = 4,
                 fill_color: str = None, fill_alpha: float = 1., line_alpha: float = 1.,
                 y_axis: Optional[YAxis] = None, tooltips: List[Tuple[str, str]] = None):
        """
        Plots a line for a time series with the index in the ts-vector from the data source

        Parameters
        ----------
        view_container:
            Figure view container where to plot the renderer of the view
        color:
            color of the line
        fill_color:
            fill_color of the scatter
        fill_alpha:
            alpha transparency of the scatter fill_color
        line_alpha:
            alpha transparency of the scatter line
        label:
            label of the view
        unit:
            unit of the data in the renderer
        index:
            index defining the time series in the ts-vector
        no_y_rescaling:
            If data should be used for y axis rescaling
        visible:
            controls the visibility of the renderer
        y_axis:
            defines on which YAxis the renderer should be plotted
        size:
            defines the size of the scatter

        Notes
        -----
        The following values can be changed from the outside during runtime:
            color, label, unit, indices, visible, size, fill_color, fill_alpha, line_alpha
        """
        super().__init__(view_container=view_container, color=color, label=label, unit=unit,
                         index=index, size=size, fill_color=fill_color, fill_alpha=fill_alpha, line_alpha=line_alpha,
                         no_y_rescaling=no_y_rescaling, visible=visible, renderer_class=SquareScatterRenderer,
                         y_axis=y_axis, tooltips=tooltips)


class TriangleScatter(Scatter):
    """
    This object contains all data for diamond view
    """

    def __init__(self, *, view_container: figure_container, color: str, label: str, unit: Unit,
                 index: int, no_y_rescaling: Optional[bool] = False, visible: bool = True, size: int = 4,
                 fill_color: str = None, fill_alpha: float = 1., line_alpha: float = 1.,
                 y_axis: Optional[YAxis] = None, tooltips: List[Tuple[str, str]] = None):
        """
        Plots a line for a time series with the index in the ts-vector from the data source

        Parameters
        ----------
        view_container:
            Figure view container where to plot the renderer of the view
        color:
            color of the line
        fill_color:
            fill_color of the scatter
        fill_alpha:
            alpha transparency of the scatter fill_color
        line_alpha:
            alpha transparency of the scatter line
        label:
            label of the view
        unit:
            unit of the data in the renderer
        index:
            index defining the time series in the ts-vector
        no_y_rescaling:
            If data should be used for y axis rescaling
        visible:
            controls the visibility of the renderer
        y_axis:
            defines on which YAxis the renderer should be plotted
        size:
            defines the size of the scatter

        Notes
        -----
        The following values can be changed from the outside during runtime:
            color, label, unit, indices, visible, size, fill_color, fill_alpha, line_alpha
        """
        super().__init__(view_container=view_container, color=color, label=label, unit=unit,
                         index=index, size=size, fill_color=fill_color, fill_alpha=fill_alpha, line_alpha=line_alpha,
                         no_y_rescaling=no_y_rescaling, visible=visible, renderer_class=TriangleScatterRenderer,
                         y_axis=y_axis, tooltips=tooltips)


class FillInBetween(FigureView):
    """
    This object contains all data for fill in between view
    """

    def __init__(self, *, view_container: figure_container, color: str, label: str, unit: Unit,
                 indices: Tuple[int, int], no_y_rescaling: Optional[bool] = False, visible: bool = True,
                 y_axis: Optional[YAxis] = None, fill_alpha: float = 0.5,
                 tooltips: List[Tuple[str, str]] = [("label", "@label")]):
        """
        Plots a filled patch between the data of two time series in the ts-vector from the data source

        Parameters
        ----------
        view_container: Figure view container where to plot the renderer of the view
        color: Color of the filling
        fill_alpha: defines the alpha value of the filling default is 0.5
        label: label of the view
        unit: unit of the data in the renderer
        indices: tuple with 2 indices defining the 2 time series in the ts-vector
        no_y_rescaling: If data should be used for y axis rescaling
        visible: controls the visiblity of the renderer
        y_axis: defines on which YAxis the renderer should be plotted

        Notes
        -----
        The following values can be changed from the outside during runtime:
            color, fill_alpha, label, unit, indices, visible
        """
        super().__init__(view_container=view_container, color=color, label=label, unit=unit,
                         no_y_rescaling=no_y_rescaling, visible=visible, renderer_class=FillInBetweenRenderer,
                         y_axis=y_axis, tooltips=tooltips)
        self.indices = indices
        self.fill_alpha = fill_alpha
        # self.tooltip = [("Name", "@label"), ("temperatures", ToolTipFunction.average), ("pos", "12312,332, 1232.333")]


class MultiLine(FigureView):
    """
    This object contains all data for a multiple-line view.
    """

    def __init__(self, *, view_container: figure_container, colors: List[str], labels: List[str], unit: Unit,
                 indices: List[int] = [], no_y_rescaling: Optional[bool] = False, visible: bool = True,
                 y_axis: Optional[YAxis] = None, line_styles: List[str] = ['solid'], line_widths: List[float] = [2.0],
                 expandable: Optional[bool] = False,
                 tooltips: List[Tuple[str, str]] = [("label", "@label")]):
        """
        Plots multiple lines for a time series with selected scenarios in the ts-vector from the data source

        Parameters
        ----------
        view_container: Figure view container where to plot the renderer of the view
        colors: color of the line
        labels: label of the view
        unit: unit of the data in the renderer
        indices: a list of indices defining the time series in the ts-vector
        no_y_rescaling: If data should be used for y axis rescaling
        visible: controls the visibility of the renderer
        y_axis: defines on which YAxis the renderer should be plotted
        expandable:

        Notes
        -----
        The following values can be changed from the outside during runtime:
            color, label, unit, indices, visible
        """
        super().__init__(view_container=view_container, color=colors, label=labels, unit=unit,
                         no_y_rescaling=no_y_rescaling, visible=visible, renderer_class=MultiLineRenderer,
                         y_axis=y_axis, tooltips=tooltips)
        self.indices = indices
        self.labels = labels
        self.expanded = True
        self.expandable = expandable

        for line_style in line_styles:
            if line_style not in VALID_LINE_STYLES:
                raise ViewError(
                    f'view {labels} in {view_container}: line_style {line_style} not in {VALID_LINE_STYLES}')
        self.line_styles = line_styles
        self.line_widths = line_widths


class BackgroundData(FigureView):
    """
    This object contains all data for background data patches
    """

    def __init__(self, *, view_container: figure_container,
                 label: str,
                 unit: Unit,
                 values_color_map=Dict[int, str],
                 default_color: str = 'white',
                 index: int, visible: bool = True,
                 y_axis: Optional[YAxis] = None,
                 fill_alpha: float = 0.5,
                 y_max: int = 1000,
                 y_min: int = -1000,
                 show_not_defined: bool = False):
        """

        Plots the data of a time series in the ts-vector from the data source as filled background patches.
        Values of the time series are mapped to colors using the values_color_map.

        For now only a single value to color are supported. See also example.

        Parameters
        ----------
        view_container:
            Figure view container where to plot the renderer of the view
        fill_alpha:
            defines the alpha value of the filling default is 0.5
        label:
            label of the view
        unit:
            unit of the data in the renderer
        index:
            index defining the time series in the ts-vector from data source to plot
        default_color:
            The color everything not defined in color map should have, has only an effect if show_not_defined=True
        show_not_defined:
            Show values not defined in the value_color_map with default_color
        values_color_map:
            Defines the mapping from value to color to use
        visible:
            controls the visibility of the renderer
        y_axis:
            defines on which YAxis the renderer should be plotted
        y_max:
            value to use as max value for the y axis
        y_min:
            value to use as min value for the y axis
        color, label, unit, index, visible, y_max, y_min, values_color_map, fill_alpha, show_not_defined
        """
        super().__init__(view_container=view_container, color=default_color, label=label, unit=unit,
                         no_y_rescaling=True, visible=visible, renderer_class=BackgroundDataRenderer,
                         y_axis=y_axis)
        # validate value_color_map:
        for k, v in values_color_map.items():
            if not isinstance(v, dict):
                raise ValueError(
                    f"BackgroundData in values_color_map: expect values in "
                    f"form of Dict[str, str] with keys `label` and `color` got {v}")
            for label in ['color', 'label']:
                if label not in v:
                    raise KeyError(f"BackgroundData in values_color_map: `{label}` not in dict of {k}: got {v}")
                if not isinstance(v[label], str):
                    raise ValueError(f"BackgroundData in values_color_map: `{label}` not of type str: got {v[label]} {type(v[label])}")

        self.index = index
        self.fill_alpha = fill_alpha
        self.values_color_map = values_color_map
        self.y_max = y_max
        self.y_min = y_min
        self.show_not_defined = show_not_defined
