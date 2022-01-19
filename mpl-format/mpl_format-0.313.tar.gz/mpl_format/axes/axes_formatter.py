from math import pi, atan2
from typing import Optional, Union, List, Tuple, Iterable, TYPE_CHECKING

import matplotlib.pyplot as plt
from compound_types.arrays import ArrayLike
from compound_types.built_ins import FloatOrFloatIterable, StrOrStrIterable, \
    DictOrDictIterable, BoolOrBoolIterable, FloatIterable, Scalar, \
    IntOrIntIterable, NdArrayIterable
from compound_types.type_checks import all_are_none, one_is_not_none
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.font_manager import FontProperties
from matplotlib.patches import \
    Arc, Arrow, BoxStyle, Circle, Ellipse, \
    FancyArrow, FancyArrowPatch, FancyBboxPatch, \
    Patch, Polygon, Rectangle, RegularPolygon, Wedge
from matplotlib.path import Path
from numpy import ndarray, linspace
from numpy.ma import cos, sin
from pandas import DataFrame, Series
from scipy.interpolate import interp1d

from mpl_format.axes.axis_formatter import AxisFormatter
from mpl_format.axes.axis_utils import new_axes
from mpl_format.axes.ticks_formatter import TicksFormatter
from mpl_format.compound_types import FontSize, Color, LegendLocation, \
    StringMapper, ColorOrColorIterable, FontStretch, FontWeight, \
    FontSizeIterable, FontStretchIterable, FontStyle, FontStyleIterable, \
    FontVariant, FontVariantIterable, CapStyle, CapStyleIterable, \
    JoinStyleIterable, JoinStyle, LineStyleIterable, LineStyle, \
    ArrowStyleIterable, ArrowStyle, ConnectionStyleIterable, ConnectionStyle, \
    PathIterable, PatchIterable, BoxStyleTypeIterable
from mpl_format.enums.box_style import BOX_STYLE, BoxStyleType
from mpl_format.enums.cap_style import CAP_STYLE
from mpl_format.enums.connection_style import CONNECTION_STYLE
from mpl_format.enums.draw_style import DRAW_STYLE
from mpl_format.enums.font_weight import FONT_WEIGHT
from mpl_format.enums.line_style import LINE_STYLE
from mpl_format.enums.mappings import kwarg_mappings
from mpl_format.enums.marker_style import MARKER_STYLE
from mpl_format.legend.legend_formatter import LegendFormatter
from mpl_format.literals import H_ALIGN, V_ALIGN, ROTATION_MODE, WHICH_TICKS, \
    FIGURE_UNITS, WHICH_AXIS, LINE_STYLE_STR
from mpl_format.patches.patch_list_formatter import PatchListFormatter
from mpl_format.text.text_formatter import TextFormatter
from mpl_format.text.text_utils import wrap_text
from mpl_format.utils.arg_checks import check_h_align, check_v_align
from mpl_format.utils.arg_transforms import smart_zip_kwargs, \
    drop_none_values, apply_mappings
from mpl_format.utils.color_utils import cross_fade
from mpl_format.utils.io_utils import save_plot

if TYPE_CHECKING:
    from mpl_format.figures.figure_formatter import FigureFormatter


class AxesFormatter(object):

    def __init__(self, axes: Optional[Axes] = None,
                 width: Optional[Scalar] = None,
                 height: Optional[Scalar] = None,
                 constrained_layout: bool = False):
        """
        Create a new AxesFormatter

        :param axes: The matplotlib Axes instance to wrap.
        :param width: Width of new Axes, if none are given.
        :param height: Height of new Axes, if none are given.
        :param constrained_layout: Option for constrained_layout of new Axes.
        """
        if axes is None:
            self._axes: Axes = new_axes(
                width=width, height=height,
                constrained_layout=constrained_layout
            )
        else:
            self._axes: Axes = axes
        self._x_axis: AxisFormatter = AxisFormatter(
            axis=self._axes.xaxis, direction='x', axes=self._axes
        )
        self._y_axis: AxisFormatter = AxisFormatter(
            axis=self._axes.yaxis, direction='y', axes=self._axes
        )
        self._title: TextFormatter = TextFormatter(self._axes.title)
        legend = self._axes.get_legend()
        if legend is None:
            self._legend = None
        else:
            self._legend = LegendFormatter(legend)
        self._ticks: TicksFormatter = TicksFormatter(
            axis='both', which='both', axes=self._axes)
        self._major_ticks: TicksFormatter = TicksFormatter(
            axis='both', which='major', axes=self._axes)
        self._minor_ticks: TicksFormatter = TicksFormatter(
            axis='both', which='minor', axes=self._axes)
        self._x_ticks: TicksFormatter = TicksFormatter(
            axis='x', which='both', axes=self._axes)
        self._x_major_ticks: TicksFormatter = TicksFormatter(
            axis='x', which='major', axes=self._axes)
        self._x_minor_ticks: TicksFormatter = TicksFormatter(
            axis='x', which='minor', axes=self._axes)
        self._y_ticks: TicksFormatter = TicksFormatter(
            axis='y', which='both', axes=self._axes)
        self._y_major_ticks: TicksFormatter = TicksFormatter(
            axis='y', which='major', axes=self._axes)
        self._y_minor_ticks = TicksFormatter(
            axis='y', which='minor', axes=self._axes)

    @staticmethod
    def gca() -> 'AxesFormatter':

        return AxesFormatter(axes=plt.gca())

    # region properties

    @property
    def axes(self) -> Axes:
        """
        Return the wrapped Axes instance.
        """
        return self._axes

    @property
    def x_axis(self) -> AxisFormatter:
        """
        Return an AxisFormatter for the x-axis of the wrapped Axes.
        """
        return self._x_axis

    @property
    def y_axis(self) -> AxisFormatter:
        """
        Return an AxisFormatter for the y-axis of the wrapped Axes.
        """
        return self._y_axis

    @property
    def legend(self) -> LegendFormatter:
        """
        Return a LegendFormatter for the legend of the wrapped Axes,
        if there is one.
        """
        return self._legend

    @property
    def title(self) -> TextFormatter:
        return self._title

    @property
    def figure(self) -> 'FigureFormatter':

        from mpl_format.figures.figure_formatter import FigureFormatter
        return FigureFormatter(self._axes)

    @property
    def ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the ticks on both axes.
        """
        return self._ticks
    
    @property
    def x_ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the ticks on the x-axis.
        """
        return self._x_ticks

    @property
    def y_ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the ticks on the y-axis.
        """
        return self._y_ticks

    @property
    def major_ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the major ticks on both axes.
        """
        return self._major_ticks

    @property
    def x_major_ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the major ticks on the x-axis.
        """
        return self._x_major_ticks

    @property
    def y_major_ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the major ticks on the y-axis.
        """
        return self._y_major_ticks

    @property
    def minor_ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the minor ticks on both axes.
        """
        return self._minor_ticks

    @property
    def x_minor_ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the minor ticks on the x-axis.
        """
        return self._x_minor_ticks

    @property
    def y_minor_ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the minor ticks on the y-axis.
        """
        return self._y_minor_ticks
    
    # endregion

    # region set text

    def set_title_text(self, text: str) -> 'AxesFormatter':
        """
        Set the text of the Axes title.

        :param text: The text to use for the Axes title.
        """
        self.title.set_text(text)
        return self

    def map_title_text(
            self, mapping: StringMapper
    ) -> 'AxesFormatter':
        """
        Map the label text for the title using a dictionary or function.

        :param mapping: Dictionary or a function mapping old text to new text.
        """
        self.title.map(mapping=mapping)
        return self

    def set_x_label_text(self, text: str) -> 'AxesFormatter':
        """
        Set the text for the x-axis label.

        :param text: The text to use for the Axis label.
        """
        self.x_axis.set_label_text(text)
        return self

    def set_y_label_text(self, text: str) -> 'AxesFormatter':
        """
        Set the text for the y-axis label.

        :param text: The text to use for the Axis label.
        """
        self.y_axis.set_label_text(text)
        return self

    def set_text(self, title: Optional[str] = None,
                 x_label: Optional[str] = None,
                 y_label: Optional[str] = None) -> 'AxesFormatter':
        """
        Set text properties for elements of the Axes.

        :param title: Text for the title.
        :param x_label: Text for the x-axis label.
        :param y_label: Text for the y-axis label.
        """
        if title is not None:
            self.set_title_text(title)
        if x_label is not None:
            self.x_axis.set_label_text(x_label)
        if y_label is not None:
            self.y_axis.set_label_text(y_label)
        return self

    # endregion

    # region wrap text

    def wrap_title(self, max_width: int) -> 'AxesFormatter':
        """
        Wrap the text for the title if it exceeds a given width of characters.

        :param max_width: The maximum character width per line.
        """
        self.set_title_text(wrap_text(self.title.text, max_width=max_width))
        return self

    def wrap_x_label(self, max_width: int) -> 'AxesFormatter':
        """
        Wrap the text for the x-axis label if it exceeds a given width of
        characters.

        :param max_width: The maximum character width per line.
        """
        self.x_axis.wrap_label(max_width=max_width)
        return self

    def wrap_y_label(self, max_width: int) -> 'AxesFormatter':
        """
        Wrap the text for the y-axis label if it exceeds a given width of
        characters.

        :param max_width: The maximum character width per line.
        """
        self.y_axis.wrap_label(max_width=max_width)
        return self

    def wrap_axis_labels(self, max_width: int) -> 'AxesFormatter':
        """
        Wrap the texts for the x and y-axis labels if they exceeds a given width
        of characters.

        :param max_width: The maximum character width per line.
        """
        self.wrap_x_label(max_width=max_width)
        self.wrap_y_label(max_width=max_width)
        return self

    # endregion

    # region set font sizes

    def set_title_size(self, font_size: FontSize) -> 'AxesFormatter':
        """
        Set the font size for the title of the wrapped Axes.

        :param font_size: Size of the font in points, or size name.
        """
        self.title.set_size(font_size)
        return self

    def set_x_label_size(self, font_size: FontSize) -> 'AxesFormatter':
        """
        Set the font size for the x-axis label.

        :param font_size: Size of the font in points, or size name.
        """
        self.x_axis.set_label_size(font_size)
        return self

    def set_y_label_size(self, font_size: FontSize) -> 'AxesFormatter':
        """
        Set the font size for the x-axis label.

        :param font_size: Size of the font in points, or size name.
        """
        self.y_axis.set_label_size(font_size)
        return self

    def set_axis_label_sizes(self, font_size: FontSize) -> 'AxesFormatter':
        """
        Set the font size for the axis labels.

        :param font_size: Size of the font in points, or size name.
        """
        self.set_x_label_size(font_size)
        self.set_y_label_size(font_size)
        return self

    def set_font_sizes(
            self,
            title: Optional[FontSize] = None,
            axis_labels: Optional[FontSize] = None,
            x_axis_label: Optional[FontSize] = None,
            y_axis_label: Optional[FontSize] = None,
            tick_labels: Optional[FontSize] = None,
            major_tick_labels: Optional[FontSize] = None,
            minor_tick_labels: Optional[FontSize] = None,
            x_tick_labels: Optional[FontSize] = None,
            x_major_tick_labels: Optional[FontSize] = None,
            x_minor_tick_labels: Optional[FontSize] = None,
            y_tick_labels: Optional[FontSize] = None,
            y_major_tick_labels: Optional[FontSize] = None,
            y_minor_tick_labels: Optional[FontSize] = None,
            legend: Optional[FontSize] = None,
            figure_title: Optional[FontSize] = None
    ) -> 'AxesFormatter':
        """
        Set font sizes for different axes elements.
        """
        ax = self._axes
        # title
        if title is not None:
            self.set_title_size(title)
        # axis labels
        if axis_labels is not None:
            self.set_axis_label_sizes(axis_labels)
        if x_axis_label is not None:
            self.set_x_label_size(x_axis_label)
        if y_axis_label is not None:
            self.set_y_label_size(y_axis_label)
        # tick labels
        if tick_labels is not None:
            self.ticks.set_label_size(tick_labels)
        if major_tick_labels is not None:
            self.major_ticks.set_label_size(major_tick_labels)
        if minor_tick_labels is not None:
            self.minor_ticks.set_label_size(minor_tick_labels)
        if x_tick_labels is not None:
            self.x_ticks.set_label_size(tick_labels)
        if x_major_tick_labels is not None:
            self.x_major_ticks.set_label_size(x_major_tick_labels)
        if x_minor_tick_labels is not None:
            self.x_minor_ticks.set_label_size(x_minor_tick_labels)
        if y_tick_labels is not None:
            self.y_ticks.set_label_size(tick_labels)
        if y_major_tick_labels is not None:
            self.y_major_ticks.set_label_size(y_major_tick_labels)
        if y_minor_tick_labels is not None:
            self.y_minor_ticks.set_label_size(y_major_tick_labels)
        if legend is not None:
            ax.legend(fontsize=legend)
        if figure_title is not None:
            ax.figure.suptitle(ax.get_title(), fontsize=figure_title)

        return self

    # endregion

    # region map labels

    def map_x_axis_label(
            self, mapping: StringMapper
    ) -> 'AxesFormatter':
        """
        Map the label text for the x-axis using a dictionary or function.

        :param mapping: Dictionary or a function mapping old text to new text.
        """
        self.x_axis.map_label_text(mapping)
        return self

    def map_y_axis_label(
            self, mapping: StringMapper
    ) -> 'AxesFormatter':
        """
        Map the label text for the y-axis using a dictionary or function.

        :param mapping: Dictionary or a function mapping old text to new text.
        """
        self.y_axis.map_label_text(mapping)
        return self

    def map_axis_labels(
            self, mapping: StringMapper
    ) -> 'AxesFormatter':
        """
        Map the label text for the x and y axes using a dictionary or function.

        :param mapping: Dictionary or a function mapping old text to new text.
        """
        self.map_x_axis_label(mapping)
        self.map_y_axis_label(mapping)
        return self

    # endregion

    # region remove

    def remove_title(self) -> 'AxesFormatter':
        """
        Remove the title from the Axes.
        """
        self.set_title_text('')
        return self

    def remove_legend(self) -> 'AxesFormatter':
        """
        Remove the legend from the Axes.
        """
        legend = self._axes.get_legend()
        if legend is not None:
            legend.remove()
            self._legend = None
        return self

    def remove_x_ticks(self) -> 'AxesFormatter':
        """
        Remove x-ticks from the Axes.
        """
        self._axes.set_xticks([])
        return self

    def remove_y_ticks(self) -> 'AxesFormatter':
        """
        Remove y-ticks from the Axes.
        """
        self._axes.set_yticks([])
        return self

    def remove_axes_ticks(self) -> 'AxesFormatter':
        """
        Remove x- and y- ticks from the Axes.
        """
        self.remove_x_ticks()
        self.remove_y_ticks()
        return self

    def remove_x_label(self) -> 'AxesFormatter':
        """
        Remove the label from the x-axis.
        """
        self.x_axis.remove_label()
        return self

    def remove_y_label(self) -> 'AxesFormatter':
        """
        Remove the label from the y-axis.
        """
        self.y_axis.remove_label()
        return self

    def remove_axes_labels(self) -> 'AxesFormatter':
        """
        Remove the labels from the x- and y- axes.
        """
        self.remove_x_label()
        self.remove_y_label()
        return self

    # endregion

    # region rotation

    def rotate_x_label(self,
                       rotation: int,
                       how: ROTATION_MODE = 'absolute') -> 'AxesFormatter':
        """
        Set the rotation of the x-axis label.

        :param rotation: The rotation value to set in degrees.
        :param how: 'absolute' or 'relative'
        """
        self.x_axis.rotate_label(rotation, how)
        return self

    def rotate_y_label(self,
                       rotation: int,
                       how: ROTATION_MODE = 'absolute') -> 'AxesFormatter':
        """
        Set the rotation of the x-axis label.

        :param rotation: The rotation value to set in degrees.
        :param how: 'absolute' or 'relative'
        """
        self.y_axis.rotate_label(rotation, how)
        return self

    # endregion

    # region spans

    def add_h_line(self, y: Union[float, str] = 0,
                   x_min: Union[float, str] = 0,
                   x_max: Union[float, str] = 1,
                   color: Optional[Color] = None,
                   alpha: Optional[float] = None,
                   line_style: Optional[LineStyle] = None,
                   line_width: Optional[float] = None,
                   label: Optional[str] = None,
                   marker_edge_color: Optional[Color] = None,
                   marker_edge_width: Optional[Color] = None,
                   marker_face_color: Optional[Color] = None,
                   marker_size: Optional[float] = None) -> 'AxesFormatter':
        """
        Add a horizontal line to the plot.

        :param y: y position in data coordinates of the horizontal line
        :param x_min: Between 0 and 1, 0 being the far left of the plot,
                      1 the far right of the plot
        :param x_max: Between 0 and 1, 0 being the far left of the plot,
                      1 the far right of the plot
        :param color: Color of the line
        :param alpha: Opacity of the line
        :param line_style: One of {'-', '--', '-.', ':', ''}
        :param line_width: Width of the line
        :param label: Text for the label
        :param marker_edge_color: Color for the edges of the line markers
        :param marker_edge_width: Width for the edges of the line markers
        :param marker_face_color: Color for the markers
        :param marker_size: Size of the markers.
        """
        line_style = LINE_STYLE.get_line_style(line_style)
        kwargs = {}
        for arg, mpl_arg in zip(
            [color, line_style, line_width,
             marker_edge_color, marker_edge_width,
             marker_face_color, marker_size,
             alpha, label],
            ['c', 'ls', 'lw', 'mec', 'mew', 'mfc', 'ms', 'alpha', 'label']
        ):
            if arg is not None:
                kwargs[mpl_arg] = arg

        self._axes.axhline(
            y=y, xmin=x_min, xmax=x_max,
            **kwargs
        )
        return self

    def add_v_line(self, x: Union[float, str] = 0,
                   y_min: Union[float, str] = 0,
                   y_max: Union[float, str] = 1,
                   color: Optional[Color] = None, alpha: Optional[float] = None,
                   line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
                   line_width: Optional[float] = None,
                   label: Optional[str] = None,
                   marker_edge_color: Optional[Color] = None,
                   marker_edge_width: Optional[Color] = None,
                   marker_face_color: Optional[Color] = None,
                   marker_size: Optional[float] = None) -> 'AxesFormatter':
        """
        Add a vertical line to the plot.

        :param x: x position in data coordinates of the vertical line
        :param y_min: Should be between 0 and 1, with 0 being the bottom of the
                      plot, and 1 the top of the plot
        :param y_max: Should be between 0 and 1, with 0 being the bottom of the
                      plot, and 1 the top of the plot
        :param color: Color of the line
        :param alpha: Opacity of the line
        :param line_style: One of {'-', '--', '-.', ':', ''}
        :param line_width: Width of the line
        :param label: Text for the label
        :param marker_edge_color: Color for the edges of the line markers
        :param marker_edge_width: Width for the edges of the line markers
        :param marker_face_color: Color for the markers
        :param marker_size: Size of the markers.
        """
        line_style = LINE_STYLE.get_line_style(line_style)
        kwargs = {}
        for arg, mpl_arg in zip(
            [color, line_style, line_width, marker_edge_color,
             marker_edge_width, marker_face_color, marker_size,
             alpha, label],
            ['c', 'ls', 'lw', 'mec',
             'mew', 'mfc', 'ms',
             'alpha', 'label']
        ):
            if arg is not None:
                kwargs[mpl_arg] = arg

        self._axes.axvline(
            x=x, ymin=y_min, ymax=y_max,
            **kwargs
        )
        return self

    def add_h_lines(self, y: FloatOrFloatIterable,
                    x_min: FloatOrFloatIterable,
                    x_max: FloatOrFloatIterable,
                    colors='k',
                    line_styles: LINE_STYLE_STR = 'solid',
                    label: Optional[str] = '') -> 'AxesFormatter':
        """
        Plot horizontal lines at each y from x_min to x_max.

        :param y: x-indexes where to plot the lines.
        :param x_min: Beginning of each or all lines.
        :param x_max: End of each or all lines.
        :param colors: Line colors.
        :param line_styles: One of {'solid', 'dashed', 'dashdot', 'dotted'}
        :param label: Label.
        """
        self._axes.hlines(y=y, xmin=x_min, xmax=x_max,
                          colors=colors, linestyles=line_styles,
                          label=label)
        return self

    def add_v_lines(self, x: FloatOrFloatIterable,
                    y_min: FloatOrFloatIterable,
                    y_max: FloatOrFloatIterable,
                    colors='k',
                    line_styles: LINE_STYLE_STR = 'solid',
                    label: Optional[str] = '') -> 'AxesFormatter':
        """
        Plot vertical lines at each x from y_min to y_max.

        :param x: x-indexes where to plot the lines.
        :param y_min: Beginning of each or all lines.
        :param y_max: End of each or all lines.
        :param colors: Line colors.
        :param line_styles: One of {'solid', 'dashed', 'dashdot', 'dotted'}
        :param label: Label.
        """
        self._axes.vlines(x=x, ymin=y_min, ymax=y_max,
                          colors=colors, linestyles=line_styles,
                          label=label)
        return self

    def fill_between(self, x: Union[ArrayLike, str],
                     y1: Union[float, ArrayLike, str],
                     y2: Union[float, ArrayLike, str],
                     data: Optional[DataFrame] = None,
                     where: Optional[ArrayLike] = None,
                     interpolate: bool = False,
                     step: Optional[str] = None,
                     color: Optional[Color] = None,
                     alpha: Optional[float] = None,
                     line_style: Optional[LineStyle] = None,
                     line_width: Optional[float] = None,
                     edge_color: Optional[Color] = None,
                     face_color: Optional[Color] = None) -> 'AxesFormatter':
        """
        Make filled polygons between two curves.

        :param x: N-length array of, or name of column with the x data.
        :param y1: N-length array, scalar, or name of column with the y1 data.
        :param y2: N-length array, scalar, or name of column with the y2 data.
        :param data: Optional DataFrame with x, y1 and y2 columns.
        :param where: If None, default to fill between everywhere. If not None,
                      it is an N-length numpy boolean array and the fill will
                      only happen over the regions where where==True.
        :param interpolate: If True, interpolate between the two lines to find
                            the precise point of intersection. Otherwise, the
                            start and end points of the filled region will only
                            occur on explicit values in the x array.
        :param step: One of {‘pre’, ‘post’, ‘mid’}. If not None, fill with step
                     logic.
        :param color: matplotlib color arg or sequence of rgba tuples
        :param alpha: Opacity.
        :param line_style: One of {'-', '--', '-.', ':', ''}
        :param line_width: float or sequence of floats
        :param edge_color: matplotlib color spec or sequence of specs
        :param face_color: matplotlib color spec or sequence of specs
        """
        line_style = LINE_STYLE.get_line_style(line_style)
        # get arrays from DataFrame
        if data is not None:
            if isinstance(x, str):
                x = data[x]
            if isinstance(y1, str):
                y1 = data[y1]
            if isinstance(y2, str):
                y2 = data[y2]
        # convert args to matplotlib names
        kwargs = {}
        for arg, mpl_arg in zip(
            [color, alpha, line_style, line_width, edge_color, face_color],
            ['color', 'alpha', 'line_style',
             'line_width', 'edge_color', 'face_color']
        ):
            if arg is not None:
                kwargs[mpl_arg] = arg
        # call matplotlib method
        self._axes.fill_between(
            x=x, y1=y1, y2=y2,
            where=where, interpolate=interpolate,
            step=step,
            **kwargs
        )
        return self

    # endregion

    # region colors

    def set_face_color(self, color: Color) -> 'AxesFormatter':

        self._axes.set_facecolor(color)
        return self

    def get_frame_color(self) -> Union[Color, List[Color]]:
        """
        Return the color of the frame if all edges are the same color,
        otherwise a list of the top, bottom, left and right colors.
        """
        colors = self.get_frame_colors()
        if len(set(colors)) == 1:
            return colors[0]
        else:
            return self.get_frame_colors()

    def set_frame_color(self, color: Color) -> 'AxesFormatter':

        for pos in ['top', 'bottom', 'left', 'right']:
            self._axes.spines[pos].set_edgecolor(color)
        return self

    def get_frame_colors(self) -> List[Color]:
        """
        Return the colors of the top, bottom, left and right edges of the Axes.
        """
        return [
            self._axes.spines[pos].get_edgecolor()
            for pos in ['top', 'bottom', 'left', 'right']
        ]

    # endregion

    # region shapes

    # region patches

    def add_text(
            self,
            x: FloatOrFloatIterable,
            y: FloatOrFloatIterable,
            text: StrOrStrIterable,
            max_width: Optional[IntOrIntIterable] = None,
            font_dict: Optional[DictOrDictIterable] = None,
            alpha: Optional[FloatOrFloatIterable] = None,
            color: Optional[ColorOrColorIterable] = None,
            h_align: Optional[StrOrStrIterable] = None,
            v_align: Optional[StrOrStrIterable] = None,
            m_align: Optional[StrOrStrIterable] = None,
            rotation: Optional[
                Union[IntOrIntIterable, StrOrStrIterable]] = None,
            rotation_mode: Optional[StrOrStrIterable] = None,
            line_spacing: Optional[FloatOrFloatIterable] = None,
            font_family: Optional[StrOrStrIterable] = None,
            font_size: Optional[Union[FontSize, FontSizeIterable]] = None,
            font_stretch: Optional[
                Union[FontStretch, FontStretchIterable]] = None,
            font_style: Optional[Union[FontStyle, FontStyleIterable]] = None,
            font_variant: Optional[
                Union[FontVariant, FontVariantIterable]] = None,
            font_weight: Optional[Union[FontWeight, FONT_WEIGHT]] = None,
            wrap: Optional[BoolOrBoolIterable] = None,
            bbox_style: Optional[StrOrStrIterable] = None,
            bbox_alpha: Optional[FloatOrFloatIterable] = None,
            bbox_cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            bbox_color: Optional[ColorOrColorIterable] = None,
            bbox_edge_color: Optional[ColorOrColorIterable] = None,
            bbox_face_color: Optional[ColorOrColorIterable] = None,
            bbox_fill: Optional[BoolOrBoolIterable] = None,
            bbox_join_style: Optional[
                Union[JoinStyle, JoinStyleIterable]] = None,
            bbox_line_style: Optional[
                Union[LineStyle, LineStyleIterable]] = None,
            bbox_line_width: Optional[FloatOrFloatIterable] = None,
            z_order: Optional[IntOrIntIterable] = None
    ) -> 'AxesFormatter':
        """
        Add a single or multiple text blocks to the plot.

        :param x: x-coordinate(s) of the text.
        :param y: y-coordinate(s) of the text.
        :param text: String or iterable of text strings to add.
        :param max_width: Max number of characters to wrap lines at.
        :param font_dict: A dictionary to override the default text properties.
                          If font_dict is None, the defaults are determined by
                          your rc parameters.
        :param alpha: Text opacity.
        :param color: Text color.
        :param h_align: Horizontal alignment.
        :param v_align: Vertical alignment.
        :param m_align: Multi-line alignment.
        :param rotation: float or {'vertical', 'horizontal'}
        :param rotation_mode: {None, 'default', 'anchor'}
        :param line_spacing:
        :param font_family:
        :param font_size: float or {'xx-small', 'x-small', 'small', 'medium',
                                    'large', 'x-large', 'xx-large'}
        :param font_stretch: {a numeric value in range 0-1000,
                             'ultra-condensed', 'extra-condensed', 'condensed',
                             'semi-condensed', 'normal', 'semi-expanded',
                             'expanded', 'extra-expanded', 'ultra-expanded'}
        :param font_style: {'normal', 'italic', 'oblique'}
        :param font_variant: {'normal', 'small-caps'}
        :param font_weight: {a numeric value in range 0-1000, 'ultralight',
                             'light', 'normal', 'regular', 'book', 'medium',
                             'roman', 'semibold', 'demibold', 'demi', 'bold',
                             'heavy', 'extra bold', 'black'}
        :param wrap: Set whether the text can be wrapped.
        :param bbox_alpha: Opacity.
        :param bbox_style: Box style.
        :param bbox_cap_style: Cap style.
        :param bbox_color: Use to set both the edge-color and the face-color.
        :param bbox_edge_color: Edge color.
        :param bbox_face_color: Face color.
        :param bbox_fill: Whether to fill the rectangle.
        :param bbox_join_style: Join style.
        :param bbox_line_style: Line style for edge.
        :param bbox_line_width: Line width for edge.
        :param z_order: z-order for the text.
        """
        for kwargs in smart_zip_kwargs(
                x=x, y=y, s=text,
                fontdict=font_dict, max_width=max_width,
                alpha=alpha, color=color,
                ha=h_align, va=v_align, ma=m_align,
                rotation=rotation, rotation_mode=rotation_mode,
                linespacing=line_spacing,
                fontfamily=font_family, fontsize=font_size,
                fontstretch=font_stretch, fontstyle=font_style,
                fontvariant=font_variant, fontweight=font_weight,
                wrap=wrap, zorder=z_order,
                bbox__boxstyle=bbox_style, bbox__alpha=bbox_alpha,
                bbox__capstyle=bbox_cap_style, bbox__color=bbox_color,
                bbox__edgecolor=bbox_edge_color,
                bbox__facecolor=bbox_face_color,
                bbox__fill=bbox_fill, bbox__joinstyle=bbox_join_style,
                bbox__linestyle=bbox_line_style, bbox__linewidth=bbox_line_width
        ):
            # main kwargs
            kwargs = drop_none_values(kwargs)
            kwargs = apply_mappings(kwargs, kwarg_mappings)
            # bbox kwargs
            bbox_kwargs = {}
            for kw, arg in kwargs.items():
                if kw.startswith('bbox__'):
                    bbox_kwargs[kw[6:]] = arg
            kwargs = {kw: arg for kw, arg in kwargs.items()
                      if not kw.startswith('bbox__')}
            if bbox_kwargs:
                bbox_kwargs = apply_mappings(bbox_kwargs, kwarg_mappings)
                kwargs['bbox'] = bbox_kwargs
            # max width
            mw = kwargs.pop('max_width', None)
            if mw is not None:
                kwargs['s'] = wrap_text(text=kwargs['s'], max_width=mw)
            # add text
            self._axes.text(**drop_none_values(kwargs))

        return self

    def add_arc(
            self,
            x_center: FloatOrFloatIterable,
            y_center: FloatOrFloatIterable,
            width: FloatOrFloatIterable,
            height: FloatOrFloatIterable,
            angle: FloatOrFloatIterable = 0.0,
            theta_start: FloatOrFloatIterable = 0.0,
            theta_end: FloatOrFloatIterable = 360.0,
            alpha: Optional[FloatOrFloatIterable] = None,
            cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            join_style: Optional[Union[JoinStyle, JoinStyleIterable]] = None,
            label: Optional[StrOrStrIterable] = None,
            line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
            line_width: Optional[FloatOrFloatIterable] = None,
            z_order: Optional[IntOrIntIterable] = None
    ):
        """
        Add an elliptical arc, i.e. a segment of an ellipse.

        :param x_center: The x-coordinate of the center of the ellipse.
        :param y_center: The y-coordinate of the center of the ellipse.
        :param width: The length of the horizontal axis.
        :param height: The length of the vertical axis.
        :param angle: Rotation of the ellipse in degrees (counterclockwise).
        :param theta_start: Starting angle of the arc in degrees.
                            Relative to angle, e.g. if angle = 45 and
                            theta_start = 90 the absolute starting angle is 135.
        :param theta_end: Ending angle of the arc in degrees.
        :param alpha: Opacity.
        :param cap_style: Cap style.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        :param z_order: z-order for the arc.
        """
        for kwargs in smart_zip_kwargs(
            x_center=x_center, y_center=y_center,
            width=width, height=height, angle=angle,
            theta1=theta_start, theta2=theta_end,
            alpha=alpha, capstyle=cap_style, color=color, edgecolor=edge_color,
            joinstyle=join_style, label=label,
            linestyle=line_style, linewidth=line_width, zorder=z_order
        ):
            kwargs = drop_none_values(kwargs)
            kwargs['xy'] = kwargs.pop('x_center'), kwargs.pop('y_center')
            arc = Arc(**kwargs)
            self._axes.add_artist(arc)

        return self

    def add_arrow(
            self,
            x_tail: FloatOrFloatIterable,
            y_tail: FloatOrFloatIterable,
            x_head: Optional[FloatOrFloatIterable] = None,
            y_head: Optional[FloatOrFloatIterable] = None,
            dx: Optional[FloatOrFloatIterable] = None,
            dy: Optional[FloatOrFloatIterable] = None,
            width: Optional[FloatOrFloatIterable] = None,
            alpha: Optional[FloatOrFloatIterable] = None,
            cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            join_style: Optional[Union[JoinStyle, JoinStyleIterable]] = None,
            label: StrOrStrIterable = None,
            line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
            line_width: Optional[FloatOrFloatIterable] = None,
            z_order: Optional[IntOrIntIterable] = None
    ):
        """
        Add an an arrow patch.

        :param x_tail: The x-coordinate of the arrow tail.
        :param y_tail: The y-coordinate of the arrow tail.
        :param x_head: The x-coordinate of the arrow head.
        :param y_head: The y-coordinate of the arrow head.
        :param dx: Arrow length in the x direction. Only used if x_head is None.
        :param dy: Arrow length in the y direction. Only used if y_head is None.
        :param width: Width of full arrow tail. default: 0.001
        :param alpha: Opacity.
        :param cap_style: Cap style.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param face_color: Face color.
        :param fill: Whether to fill the rectangle.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        :param z_order: z-order for the arrow.
        """
        if not one_is_not_none(dx, x_head):
            raise ValueError('Must give dx or x_head')
        if not one_is_not_none(dy, y_head):
            raise ValueError('Must give dy or y_head')
        for kwargs in smart_zip_kwargs(
                x=x_tail, y=y_tail, x_head=x_head, y_head=y_head,
                dx=dx, dy=dy, width=width,
                alpha=alpha, capstyle=cap_style,
                color=color, edgecolor=edge_color, facecolor=face_color,
                fill=fill, joinstyle=join_style, label=label,
                linestyle=line_style, linewidth=line_width,
                zorder=z_order
        ):
            kwargs = drop_none_values(kwargs)
            kwargs = apply_mappings(kwargs, kwarg_mappings)
            if kwargs['x_head'] is not None:
                kwargs['dx'] = kwargs['x_head'] - kwargs['x']
                kwargs.pop('x_head')
            if kwargs['y_head'] is not None:
                kwargs['dy'] = kwargs['y_head'] - kwargs['y']
                kwargs.pop('y_head')
            arrow = Arrow(**kwargs)
            self._axes.add_artist(arrow)

        return self

    def add_circle(
            self,
            x_center: FloatOrFloatIterable,
            y_center: FloatOrFloatIterable,
            radius: FloatOrFloatIterable,
            alpha: Optional[FloatOrFloatIterable] = None,
            cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            label: Optional[StrOrStrIterable] = None,
            line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
            line_width: Optional[FloatOrFloatIterable] = None,
            join_style: Optional[Union[JoinStyle, JoinStyleIterable]] = None,
            z_order: Optional[IntOrIntIterable] = None
    ) -> 'AxesFormatter':
        """
        Add a rectangle to the Axes.

        :param x_center: The left rectangle coordinate.
        :param y_center: The bottom rectangle coordinate.
        :param radius: The radius of the circle.
        :param alpha: Opacity.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param face_color: Face color.
        :param fill: Whether to fill the rectangle.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        :param cap_style: Cap style.
        :param z_order: z-order for the circle.
        """
        for kwargs in smart_zip_kwargs(
                x_center=x_center, y_center=y_center, radius=radius,
                alpha=alpha, capstyle=cap_style,
                color=color, edgecolor=edge_color, facecolor=face_color,
                fill=fill, joinstyle=join_style, label=label,
                linestyle=line_style, linewidth=line_width,
                zorder=z_order
        ):
            kwargs = drop_none_values(kwargs)
            kwargs = apply_mappings(kwargs, kwarg_mappings)
            kwargs['xy'] = kwargs.pop('x_center'), kwargs.pop('y_center')
            circle = Circle(**kwargs)
            self._axes.add_artist(circle)

        return self

    def add_ellipse(
            self,
            x_center: FloatOrFloatIterable,
            y_center: FloatOrFloatIterable,
            width: FloatOrFloatIterable,
            height: FloatOrFloatIterable,
            angle: FloatOrFloatIterable = 0.0,
            alpha: Optional[FloatOrFloatIterable] = None,
            cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            join_style: Optional[Union[JoinStyle, JoinStyleIterable]] = None,
            label: Optional[StrOrStrIterable] = None,
            line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
            line_width: Optional[FloatOrFloatIterable] = None,
            z_order: Optional[IntOrIntIterable] = None
    ):
        """
        Add an elliptical arc, i.e. a segment of an ellipse.

        :param x_center: The x-coordinate of the center of the ellipse.
        :param y_center: The y-coordinate of the center of the ellipse.
        :param width: The length (diameter) of the horizontal axis.
        :param height: The length (diameter) of the vertical axis.
        :param angle: Rotation of the ellipse in degrees (counter-clockwise).
        :param alpha: Opacity.
        :param cap_style: Cap style.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param face_color: Face color.
        :param fill: Whether to fill the rectangle.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        :param z_order: z-order for the ellipse.
        """
        for kwargs in smart_zip_kwargs(
            x_center=x_center, y_center=y_center,
            width=width, height=height, angle=angle,
            alpha=alpha, capstyle=cap_style,
            color=color, edgecolor=edge_color, facecolor=face_color,
            fill=fill, joinstyle=join_style, label=label,
            linestyle=line_style, linewidth=line_width, zorder=z_order
        ):
            kwargs = drop_none_values(kwargs)
            kwargs = apply_mappings(kwargs, kwarg_mappings)
            kwargs['xy'] = kwargs.pop('x_center'), kwargs.pop('y_center')
            ellipse = Ellipse(**kwargs)
            self._axes.add_artist(ellipse)

        return self

    def add_fancy_arrow(
            self,
            x_tail: FloatOrFloatIterable,
            y_tail: FloatOrFloatIterable,
            x_head: Optional[FloatOrFloatIterable] = None,
            y_head: Optional[FloatOrFloatIterable] = None,
            dx: Optional[FloatOrFloatIterable] = None,
            dy: Optional[FloatOrFloatIterable] = None,
            tail_width: FloatOrFloatIterable = 0.001,
            length_includes_head: BoolOrBoolIterable = False,
            head_width: Optional[FloatOrFloatIterable] = None,
            head_length: Optional[FloatOrFloatIterable] = None,
            shape: StrOrStrIterable = 'full',
            overhang: FloatOrFloatIterable = 0.0,
            head_starts_at_zero: BoolOrBoolIterable = False,
            alpha: Optional[FloatOrFloatIterable] = None,
            cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            join_style: Optional[Union[JoinStyle, JoinStyleIterable]] = None,
            label: Optional[StrOrStrIterable] = None,
            line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
            line_width: Optional[FloatOrFloatIterable] = None,
            z_order: Optional[IntOrIntIterable] = None
    ):
        """
        Like Arrow, but lets you set head width and head height independently.

        :param x_tail: The x-coordinate of the arrow tail.
        :param y_tail: The y-coordinate of the arrow tail.
        :param x_head: The x-coordinate of the arrow head.
        :param y_head: The y-coordinate of the arrow head.
        :param dx: Arrow length in the x direction. Only used if x_head is None.
        :param dy: Arrow length in the y direction. Only used if y_head is None.
        :param tail_width: Width of full arrow tail.
        :param length_includes_head: True if head is to be counted in
                                     calculating the length.
        :param head_width: Total width of the full arrow head
        :param head_length: Length of arrow head
        :param shape: Draw the left-half, right-half, or full arrow.
                      One of ['full', 'left', 'right'].
        :param overhang: Fraction that the arrow is swept back
                         (0 overhang means triangular shape).
                         Can be negative or greater than one.
        :param head_starts_at_zero: If True, the head starts being drawn at
                                    coordinate 0 instead of ending at
                                    coordinate 0.
        :param alpha: Opacity.
        :param cap_style: Cap style.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param face_color: Face color.
        :param fill: Whether to fill the rectangle.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        :param z_order: z-order for the arrow.
        """
        if not one_is_not_none(dx, x_head):
            raise ValueError('Must give dx or x_head')
        if not one_is_not_none(dy, y_head):
            raise ValueError('Must give dy or y_head')
        for kwargs in smart_zip_kwargs(
                x=x_tail, y=y_tail, x_head=x_head, y_head=y_head,
                dx=dx, dy=dy, width=tail_width,
                length_includes_head=length_includes_head,
                head_width=head_width, head_length=head_length,
                shape=shape, overhang=overhang,
                head_starts_at_zero=head_starts_at_zero,
                alpha=alpha, capstyle=cap_style,
                color=color, edgecolor=edge_color, facecolor=face_color,
                fill=fill, joinstyle=join_style, label=label,
                linestyle=line_style, linewidth=line_width,
                zorder=z_order
        ):
            kwargs = drop_none_values(kwargs)
            kwargs = apply_mappings(kwargs, kwarg_mappings)
            if kwargs['x_head'] is not None:
                kwargs['dx'] = kwargs['x_head'] - kwargs['x']
                kwargs.pop('x_head')
            if kwargs['y_head'] is not None:
                kwargs['dy'] = kwargs['y_head'] - kwargs['y']
                kwargs.pop('y_head')
            arrow = FancyArrow(**kwargs)
            self._axes.add_artist(arrow)

        return self

    def add_fancy_arrow_patch(
            self,
            x: FloatOrFloatIterable,
            y: FloatOrFloatIterable,
            dx: FloatOrFloatIterable,
            dy: FloatOrFloatIterable,
            path: Optional[Union[Path, PathIterable]] = None,
            arrow_style: Union[ArrowStyle, ArrowStyleIterable] = 'simple',
            connection_style: Union[
                ConnectionStyle, ConnectionStyleIterable
            ] = CONNECTION_STYLE.arc_3,
            tail_patch: Optional[Union[Patch, PatchIterable]] = None,
            head_patch: Optional[Union[Patch, PatchIterable]] = None,
            tail_shrink_factor: Optional[FloatOrFloatIterable] = 2,
            head_shrink_factor: Optional[FloatOrFloatIterable] = 2,
            mutation_scale: Optional[FloatOrFloatIterable] = 1,
            mutation_aspect: Optional[FloatOrFloatIterable] = None,
            dpi_cor: Optional[FloatOrFloatIterable] = 1,
            alpha: Optional[FloatOrFloatIterable] = None,
            cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            join_style: Optional[Union[JoinStyle, JoinStyleIterable]] = None,
            label: Optional[StrOrStrIterable] = None,
            line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
            line_width: Optional[FloatOrFloatIterable] = None,
            z_order: Optional[IntOrIntIterable] = None
    ):
        """
        Like Arrow, but lets you set head width and head height independently.

        :param x: The x-coordinate of the arrow tail.
        :param y: The y-coordinate of the arrow tail.
        :param dx: Arrow length in the x direction.
        :param dy: Arrow length in the y direction.
        :param path: If provided, an arrow is drawn along this path and
                     tail_patch, head_patch, tail_shrink_factor, and
                     head_shrink_factor are ignored.
        :param arrow_style: Describes how the fancy arrow will be drawn.
                            It can be string of the available arrowstyle names,
                            with optional comma-separated attributes,
                            or an ArrowStyle instance.
                            The optional attributes are meant to be scaled with
                            the mutation_scale.
        :param connection_style: Describes how the arrow ends are connected.
        :param tail_patch: Optional tail patch.
        :param head_patch: Optional head patch.
        :param tail_shrink_factor: Shrinking factor of the tail.
        :param head_shrink_factor: Shrinking factor of the head.
        :param mutation_scale: Value with which attributes of arrowstyle
                               (e.g., head_length) will be scaled.
        :param mutation_aspect: The height of the rectangle will be squeezed by
                                this value before the mutation and the mutated
                                box will be stretched by the inverse of it.
        :param dpi_cor: dpi_cor is currently used for linewidth-related things
                        and shrink factor. Mutation scale is affected by this.
        :param alpha: Opacity.
        :param cap_style: Cap style.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param face_color: Face color.
        :param fill: Whether to fill the rectangle.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        :param z_order: z-order for the arrow.
        """
        for kwargs in smart_zip_kwargs(
                x=x, y=y, dx=dx, dy=dy, path=path,
                arrowstyle=arrow_style, connectionstyle=connection_style,
                patchA=tail_patch, patchB=head_patch,
                shrinkA=tail_shrink_factor, shrinkB=head_shrink_factor,
                mutation_scale=mutation_scale, mutation_aspect=mutation_aspect,
                dpi_cor=dpi_cor,
                alpha=alpha, capstyle=cap_style,
                color=color, edgecolor=edge_color, facecolor=face_color,
                fill=fill, joinstyle=join_style, label=label,
                linestyle=line_style, linewidth=line_width,
                zorder=z_order
        ):
            x = kwargs.pop('x')
            y = kwargs.pop('y')
            dx = kwargs.pop('dx')
            dy = kwargs.pop('dy')
            kwargs['posA'] = x, y
            kwargs['posB'] = x + dx, y + dy
            kwargs = drop_none_values(kwargs)
            kwargs = apply_mappings(kwargs, kwarg_mappings)
            arrow = FancyArrowPatch(**kwargs)
            self._axes.add_artist(arrow)

        return self

    def add_fancy_box_patch(
            self,
            x: FloatOrFloatIterable,
            y: FloatOrFloatIterable,
            width: FloatOrFloatIterable,
            height: FloatOrFloatIterable,
            box_style: Union[
                BoxStyleType, BoxStyleTypeIterable] = BOX_STYLE.round,
            mutation_scale: Optional[FloatOrFloatIterable] = 1,
            mutation_aspect: Optional[FloatOrFloatIterable] = None,
            alpha: Optional[FloatOrFloatIterable] = None,
            cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            join_style: Optional[Union[JoinStyle, JoinStyleIterable]] = None,
            label: Optional[StrOrStrIterable] = None,
            line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
            line_width: Optional[FloatOrFloatIterable] = None,
            z_order: Optional[IntOrIntIterable] = None
    ):
        """
        A fancy box around a rectangle with lower left at xy = (x, y)
        with specified width and height.

        :param x: The left coord of the rectangle.
        :param y: The bottom coord of the rectangle.
        :param width: The rectangle width.
        :param height: The rectangle height.
        :param box_style: The box style.
        :param mutation_scale: Value with which attributes of arrowstyle
                               (e.g. head_length) will be scaled.
        :param mutation_aspect: The height of the rectangle will be squeezed by
                                this value before the mutation and the mutated
                                box will be stretched by the inverse of it.
        :param alpha: Opacity.
        :param cap_style: Cap style.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param face_color: Face color.
        :param fill: Whether to fill the rectangle.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        :param z_order: z-order for the box.
        """
        for kwargs in smart_zip_kwargs(
                x=x, y=y, width=width, height=height,
                boxstyle=box_style,
                mutation_scale=mutation_scale, mutation_aspect=mutation_aspect,
                alpha=alpha, fill=fill,
                color=color, edgecolor=edge_color, facecolor=face_color,
                capstyle=cap_style, joinstyle=join_style,
                label=label,
                linestyle=line_style, linewidth=line_width,
                zorder=z_order,
        ):
            kwargs = drop_none_values(kwargs)
            kwargs = apply_mappings(kwargs, kwarg_mappings)
            kwargs['xy'] = kwargs.pop('x'), kwargs.pop('y')
            fancy_box = FancyBboxPatch(**kwargs)
            self._axes.add_artist(fancy_box)

        return self

    def add_polygon(
            self,
            xy: Union[ndarray, NdArrayIterable],
            closed: BoolOrBoolIterable = True,
            alpha: Optional[FloatOrFloatIterable] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            label: Optional[StrOrStrIterable] = None,
            line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
            line_width: Optional[FloatOrFloatIterable] = None,
            cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            join_style: Optional[Union[JoinStyle, JoinStyleIterable]] = None,
            z_order: Optional[IntOrIntIterable] = None
    ) -> 'AxesFormatter':
        """
        Add a general polygon patch.

        :param xy: A numpy array with shape Nx2.
        :param closed: If True, the polygon will be closed so the starting and
                       ending points are the same.
        :param alpha: Opacity.
        :param cap_style: Cap style.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param face_color: Face color.
        :param fill: Whether to fill the rectangle.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        :param z_order: z-order for the polygon.
        """
        for kwargs in smart_zip_kwargs(
                xy=xy, closed=closed,
                alpha=alpha, color=color, edgecolor=edge_color,
                facecolor=face_color, fill=fill,
                label=label,
                linestyle=line_style, linewidth=line_width,
                capstyle=cap_style, joinstyle=join_style,
                zorder=z_order,
        ):
            kwargs = drop_none_values(kwargs)
            kwargs = apply_mappings(kwargs, kwarg_mappings)
            polygon = Polygon(**kwargs)
            self._axes.add_artist(polygon)

        return self

    def add_rectangle(
            self,
            width: FloatOrFloatIterable, 
            height: FloatOrFloatIterable,
            angle: FloatOrFloatIterable = 0.0,
            x_left: Optional[FloatOrFloatIterable] = None, 
            y_bottom: Optional[FloatOrFloatIterable] = None,
            x_center: Optional[FloatOrFloatIterable] = None, 
            y_center: Optional[FloatOrFloatIterable] = None,
            alpha: Optional[FloatOrFloatIterable] = None,
            cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            join_style: Optional[Union[JoinStyle, JoinStyleIterable]] = None,
            label: Optional[StrOrStrIterable] = None,
            line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
            line_width: Optional[FloatOrFloatIterable] = None,
            z_order: Optional[IntOrIntIterable] = None
    ) -> 'AxesFormatter':
        """
        Add a rectangle to the Axes.

        :param x_left: The left rectangle coordinate.
        :param y_bottom: The bottom rectangle coordinate.
        :param width: Rectangle width.
        :param height: Rectangle height.
        :param x_left: The left rectangle coordinate.
        :param y_bottom: The bottom rectangle coordinate.
        :param x_center: The center rectangle x-coordinate.
        :param y_center: The center rectangle y-coordinate.
        :param angle: Rotation in degrees anti-clockwise about xy (default=0.0)
        :param alpha: Opacity.
        :param cap_style: Cap style.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param face_color: Face color.
        :param fill: Whether to fill the rectangle.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        :param z_order: z-order for the rectangle.
        """
        for kwargs in smart_zip_kwargs(
                width=width, height=height, angle=angle,
                x_left=x_left, y_bottom=y_bottom,
                x_center=x_center, y_center=y_center,
                alpha=alpha, fill=fill, label=label,
                color=color, edgecolor=edge_color, facecolor=face_color,
                capstyle=cap_style, joinstyle=join_style,
                linestyle=line_style, linewidth=line_width,
                zorder=z_order
        ):

            if not one_is_not_none(x_left, x_center):
                raise ValueError('Give one of {x_left, x_center}')
            if not one_is_not_none(y_bottom, y_center):
                raise ValueError('Give one of {y_bottom, y_center}')
            if not (
                    all_are_none(x_left, y_bottom) or
                    all_are_none(x_center, y_center)
            ):
                raise ValueError(
                    'Give either {x_left, y_bottom} or {x_center, y_center}'
                )

            kwargs = drop_none_values(kwargs)
            kwargs = apply_mappings(kwargs, kwarg_mappings)

            if all_are_none(x_left, y_bottom):
                x_c = kwargs.pop('x_center')
                y_c = kwargs.pop('y_center')
                w = kwargs['width']
                h = kwargs['height']
                a = kwargs['angle']
                x_l = x_c - w / 2
                y_b = y_c - h / 2
                r = ((w / 2) ** 2 + (h / 2) ** 2) ** 0.5
                theta = atan2(h, w)
                xc_new = x_l + r * cos(theta + pi * a / 180)
                yc_new = y_b + r * sin(theta + pi * a / 180)
                kwargs['x'] = x_l + x_c - xc_new
                kwargs['y'] = y_b + y_c - yc_new
            else:
                kwargs['x'] = kwargs.pop('x_left')
                kwargs['y'] = kwargs.pop('y_bottom')

            kwargs['xy'] = kwargs.pop('x'), kwargs.pop('y')

            rectangle = Rectangle(**kwargs)
            self._axes.add_artist(rectangle)

        return self

    def add_regular_polygon(
            self,
            x_center: FloatOrFloatIterable,
            y_center: FloatOrFloatIterable,
            num_vertices: IntOrIntIterable,
            radius: FloatOrFloatIterable,
            angle: FloatOrFloatIterable = 0,
            alpha: Optional[FloatOrFloatIterable] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            label: Optional[StrOrStrIterable] = None,
            line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
            line_width: Optional[FloatOrFloatIterable] = None,
            cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            join_style: Optional[Union[JoinStyle, JoinStyleIterable]] = None,
            z_order: Optional[IntOrIntIterable] = None
    ) -> 'AxesFormatter':
        """
        Add a rectangle to the Axes.

        :param x_center: The x-coordinate of the center of the polygon.
        :param y_center: The y-coordinate of the center of the polygon.
        :param num_vertices: Number of vertices.
        :param radius: The distance from the center to each of the vertices.
        :param angle: Rotation in degrees anti-clockwise about xy
                            (default is 0.0)
        :param alpha: Opacity.
        :param cap_style: Cap style.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param face_color: Face color.
        :param fill: Whether to fill the rectangle.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        :param z_order: z-order for the polygon.
        """
        for kwargs in smart_zip_kwargs(
                x_center=x_center, y_center=y_center,
                numVertices=num_vertices, radius=radius, angle=angle,
                alpha=alpha, fill=fill, label=label,
                color=color, edgecolor=edge_color, facecolor=face_color,
                linestyle=line_style, linewidth=line_width,
                capstyle=cap_style, joinstyle=join_style,
                zorder=z_order,
        ):
            kwargs = drop_none_values(kwargs)
            kwargs = apply_mappings(kwargs, kwarg_mappings)
            kwargs['orientation'] = pi * kwargs.pop('angle') / 180
            polygon = RegularPolygon(**kwargs)
            self._axes.add_artist(polygon)

        return self

    def add_wedge(
            self,
            x_center: FloatOrFloatIterable,
            y_center: FloatOrFloatIterable,
            radius: FloatOrFloatIterable,
            theta_start: FloatOrFloatIterable,
            theta_end: FloatOrFloatIterable,
            width: Optional[FloatOrFloatIterable] = None,
            alpha: Optional[FloatOrFloatIterable] = None,
            cap_style: Optional[Union[CapStyle, CapStyleIterable]] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            join_style: Optional[Union[JoinStyle, JoinStyleIterable]] = None,
            label: Optional[StrOrStrIterable] = None,
            line_style: Optional[Union[LineStyle, LineStyleIterable]] = None,
            line_width: Optional[FloatOrFloatIterable] = None,
            z_order: Optional[IntOrIntIterable] = None
    ):
        """
        Add a wedge-shaped patch.

        :param x_center: The x-coordinate of the center of the ellipse.
        :param y_center: The y-coordinate of the center of the ellipse.
        :param radius: (Outer) radius.
        :param theta_start: Starting angle of the arc in degrees.
                            Relative to angle, e.g. if angle = 45 and
                            theta_start = 90 the absolute starting angle is 135.
        :param theta_end: Ending angle of the arc in degrees.
        :param width: If width is given, then a partial wedge is drawn from
                      inner radius - width to outer radius.
        :param alpha: Opacity.
        :param cap_style: Cap style.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param face_color: Face color.
        :param fill: Whether to fill the rectangle.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        :param z_order: z-order for the wedge.
        """
        for kwargs in smart_zip_kwargs(
                x_center=x_center, y_center=y_center, r=radius,
                theta1=theta_start, theta2=theta_end,
                width=width, alpha=alpha, fill=fill,
                color=color, edgecolor=edge_color, facecolor=face_color,
                capstyle=cap_style, joinstyle=join_style, linestyle=line_style,
                linewidth=line_width,
                label=label, zorder=z_order,
        ):
            kwargs = drop_none_values(kwargs)
            kwargs = apply_mappings(kwargs, kwarg_mappings)
            kwargs['orientation'] = pi * kwargs.pop('angle') / 180
            wedge = Wedge(**kwargs)
            self._axes.add_artist(wedge)

        return self

    @property
    def arcs(self) -> PatchListFormatter:
        """
        Return a list of the Arcs on the axes.
        """
        return PatchListFormatter([
            a for a in self._axes.get_children()
            if isinstance(a, Arc)
        ])

    @property
    def arrows(self) -> PatchListFormatter:
        """
        Return a list of the Arrows on the axes.
        """
        return PatchListFormatter([
            a for a in self._axes.get_children()
            if isinstance(a, Arrow)
        ])

    @property
    def circles(self) -> PatchListFormatter:
        """
        Return a list of the Circles on the axes.
        """
        return PatchListFormatter([
            c for c in self._axes.get_children()
            if isinstance(c, Circle)
        ])

    @property
    def ellipses(self) -> PatchListFormatter:
        """
        Return a list of the Ellipses on the axes.
        """
        return PatchListFormatter([
            e for e in self._axes.get_children()
            if isinstance(e, Ellipse)
        ])

    @property
    def fancy_arrows(self) -> PatchListFormatter:
        """
        Return a list of the FancyArrows on the axes.
        """
        return PatchListFormatter([
            a for a in self._axes.get_children()
            if isinstance(a, FancyArrow)
        ])

    @property
    def fancy_arrow_patches(self) -> PatchListFormatter:
        """
        Return a list of the FancyArrowPatches on the axes.
        """
        return PatchListFormatter([
            a for a in self._axes.get_children()
            if isinstance(a, FancyArrowPatch)
        ])

    @property
    def fancy_boxes(self) -> PatchListFormatter:
        """
        Return a list of the FancyBoxes on the axes.
        """
        return PatchListFormatter([
            b for b in self._axes.get_children()
            if isinstance(b, FancyBboxPatch)
        ])

    @property
    def polygons(self) -> PatchListFormatter:
        """
        Return a list of the Polygons on the axes.
        """
        return PatchListFormatter([
            p for p in self._axes.get_children()
            if isinstance(p, Polygon)
        ])

    @property
    def regular_polygons(self) -> PatchListFormatter:
        """
        Return a list of the RegularPolygons on the axes.
        """
        return PatchListFormatter([
            r for r in self._axes.get_children()
            if isinstance(r, RegularPolygon)
        ])

    @property
    def wedges(self) -> PatchListFormatter:
        """
        Return a list of the Wedges on the axes.
        """
        return PatchListFormatter([
            w for w in self._axes.get_children()
            if isinstance(w, Wedge)
        ])

    # endregion

    # region custom shapes

    def add_v_density(
            self, x: float,
            y_to_z: Series,
            color: Optional[Color] = 'k',
            color_min: Optional[Color] = None,
            width: float = 0.8,
            z_max: Optional[float] = None,
            h_align: H_ALIGN = 'center'
    ) -> 'AxesFormatter':
        """
        Add a vertical density bar to the plot.

        :param x: The x-coordinate of the bar.
        :param y_to_z: A mapping of the bar's y-coordinate to it density.
        :param color: The color of the density bar.
        :param color_min: Optional 2nd color to fade out to.
        :param width: The bar width.
        :param z_max: Value to scale down densities by to get to a range of
                      0 to 1. Defaults to max value of y_to_z.
        :param h_align: Horizontal alignment.
                        One of {'left', 'center', 'right'}.
        """
        check_h_align(h_align)

        if z_max is None:
            z_max = y_to_z.max()
        y = y_to_z.index.to_list()
        y_lowers = y[: -1]
        y_uppers = y[1:]

        if h_align == 'left':
            x_left = x
        elif h_align == 'center':
            x_left = x - width / 2
        elif h_align == 'right':
            x_left = x - width
        else:
            raise ValueError(f'h_align must be one of {H_ALIGN}')

        alphas = (
                y_to_z / z_max
        ).rolling(2).mean().shift(-1).dropna().clip(0.0, 1.0)

        if color_min is None:
            color_min = color
        colors = cross_fade(from_color=color_min, to_color=color,
                            amount=alphas)

        for y_lower, y_upper, alpha, color in zip(
                y_lowers, y_uppers, alphas, colors
        ):
            self.add_rectangle(
                x_left=x_left, y_bottom=y_lower,
                width=width, height=y_upper - y_lower,
                face_color=color, alpha=alpha
            )

        return self

    def add_h_density(
            self, y: float,
            x_to_z: Series,
            color: Optional[Color] = 'k',
            color_min: Optional[Color] = None,
            height: float = 0.8,
            z_max: Optional[float] = None,
            v_align: V_ALIGN = 'center'
    ) -> 'AxesFormatter':
        """
        Add a horizontal density bar to the plot.

        :param y: The y-coordinate of the bar.
        :param x_to_z: A mapping of the bar's x-coordinate to it density.
        :param color: The color of the density bar.
        :param color_min: Optional 2nd color to fade out to.
        :param height: The bar width.
        :param z_max: Value to scale down densities by to get to a range of
                      0 to 1. Defaults to max value of x_to_z.
        :param v_align: Vertical alignment.
                        One of {'top', 'center', 'bottom'}.
        """
        check_v_align(v_align)

        if z_max is None:
            z_max = x_to_z.max()
        x = x_to_z.index.to_list()
        x_lefts = x[: -1]
        x_rights = x[1:]

        if v_align == 'bottom':
            y_bottom = y
        elif v_align == 'center':
            y_bottom = y - height / 2
        else:
            y_bottom = y - height

        alphas = (
                x_to_z / z_max
        ).rolling(2).mean().shift(-1).dropna().clip(0.0, 1.0)

        if color_min is None:
            color_min = color
        colors = cross_fade(from_color=color_min, to_color=color,
                            amount=alphas)

        for x_left, x_right, alpha, color in zip(
                x_lefts, x_rights, alphas, colors
        ):
            self.add_rectangle(
                x_left=x_left, y_bottom=y_bottom,
                width=x_right-x_left, height=height,
                face_color=color, alpha=alpha
            )

        return self

    # endregion

    # region plots

    def add_v_bars(
            self,
            x: Union[str, FloatOrFloatIterable],
            y: Union[str, FloatOrFloatIterable],
            width: Union[str, FloatOrFloatIterable],
            box_style: Union[BoxStyle, Iterable[BoxStyle]],
            data: Optional[DataFrame] = None,
            y_0: Optional[Union[str, FloatOrFloatIterable]] = 0.0,
            h_align: H_ALIGN = 'center',
            mutation_scale: Union[str, FloatOrFloatIterable] = 1,
            mutation_aspect: Optional[Union[str, FloatOrFloatIterable]] = None,
            alpha: Optional[Union[str, FloatOrFloatIterable]] = None,
            cap_style: Optional[Union[
                StrOrStrIterable, CAP_STYLE, Iterable[CAP_STYLE]
            ]] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            line_style: Optional[Union[
                StrOrStrIterable, LINE_STYLE, Iterable[LINE_STYLE]
            ]] = None,
            line_width: Optional[FloatOrFloatIterable] = None
    ) -> 'AxesFormatter':
        """
        Add vertical bars to the plot with the given BoxStyle.

        :param x: X-coordinate for each bar, or name of column.
        :param y: Y-coordinate of top of each bar, or name of column.
        :param width: Width of each bar, or name of column.
        :param box_style: The style of each box, or name of column.
        :param data: Optional DataFrame to extract sequences of attributes.
        :param y_0: Y-coordinate of bottom of each bar. Defaults to 0.
        :param h_align: Horizontal alignment. One of {'left', 'center', 'right'}
        :param mutation_scale: Scaling factor applied to the attributes of the
                               box style (e.g. pad or rounding_size).
        :param mutation_aspect: The height of the rectangle will be squeezed by
                                this value before the mutation and the mutated
                                box will be stretched by the inverse of it.
                                For example, this allows different horizontal
                                and vertical padding.
        :param alpha: Opacity from 0 to 1.
        :param cap_style: One of {'butt', 'round', 'projecting'}
        :param color: Color for faces and edges.
        :param edge_color: Color for edges.
        :param face_color: Color for faces.
        :param fill: Whether bars are filled.
        :param line_style: Line style.
        :param line_width: Line width.
        """
        check_h_align(h_align)

        def get_data(item) -> Series:
            if data is None:
                return item
            if isinstance(item, str) and item in data.columns:
                return data[item]
            else:
                return item

        def make_iterable(item):
            if not isinstance(item, Iterable) or isinstance(item, str):
                item = [item] * len(x)
            return item

        x = get_data(x)
        y = make_iterable(get_data(y))
        y_0 = make_iterable(get_data(y_0))
        width = make_iterable(get_data(width))
        box_style = make_iterable(get_data(box_style))
        mutation_scale = make_iterable(get_data(mutation_scale))
        mutation_aspect = make_iterable(get_data(mutation_aspect))
        alpha = make_iterable(get_data(alpha))
        cap_style = make_iterable(get_data(cap_style))
        color = make_iterable(get_data(color))
        edge_color = make_iterable(get_data(edge_color))
        face_color = make_iterable(get_data(face_color))
        fill = make_iterable(get_data(fill))
        line_style = make_iterable(get_data(line_style))
        line_width = make_iterable(get_data(line_width))

        for (
                x_i, y_i, y_0_i, w_i, bs_i,
                ms_i, ma_i, a_i, cs_i,
                c_i, ec_i, fc_i,
                f_i, ls_i, lw_i
        ) in zip(
            x, y, y_0, width, box_style,
            mutation_scale, mutation_aspect, alpha, cap_style,
            color, edge_color, face_color,
            fill, line_style, line_width
        ):
            if h_align == 'left':
                x_p = x_i
            elif h_align == 'center':
                x_p = x_i - w_i / 2
            else:
                x_p = x_i - width

            self.add_fancy_box_patch(
                x=x_p, y=y_0_i, width=w_i, height=y_i - y_0_i,
                box_style=bs_i,
                mutation_scale=ms_i, mutation_aspect=ma_i,
                alpha=a_i, cap_style=cs_i,
                color=c_i, edge_color=ec_i, face_color=fc_i,
                fill=f_i, line_style=ls_i, line_width=lw_i
            )

        return self

    def add_v_pills(
            self,
            x: Union[str, FloatOrFloatIterable],
            y: Union[str, FloatOrFloatIterable],
            width: float,
            data: Optional[DataFrame] = None,
            y_0: Optional[Union[str, FloatOrFloatIterable]] = 0.0,
            h_align: H_ALIGN = 'center',
            alpha: Optional[Union[str, FloatOrFloatIterable]] = None,
            color: Optional[ColorOrColorIterable] = None,
            edge_color: Optional[ColorOrColorIterable] = None,
            face_color: Optional[ColorOrColorIterable] = None,
            fill: BoolOrBoolIterable = True,
            line_style: Optional[Union[
                StrOrStrIterable, LINE_STYLE, Iterable[LINE_STYLE]
            ]] = None,
            line_width: Optional[FloatOrFloatIterable] = None
    ) -> 'AxesFormatter':
        """
        Add vertical bars to the plot with the given BoxStyle.

        :param x: X-coordinate for each bar, or name of column.
        :param y: Y-coordinate of top of each bar, or name of column.
        :param width: Width of each bar, or name of column.
        :param data: Optional DataFrame to extract sequences of attributes.
        :param y_0: Y-coordinate of bottom of each bar. Defaults to 0.
        :param h_align: One of {'left', 'center', 'right'}.
        :param alpha: Opacity from 0 to 1.
        :param color: Color for faces and edges.
        :param edge_color: Color for edges.
        :param face_color: Color for faces.
        :param fill: Whether bars are filled.
        :param line_style: Line style.
        :param line_width: Line width.
        """
        mutation_aspect = (
                (self.width() / self.height()) *
                (self.get_y_height() / self.get_x_width())
        )
        self.add_v_bars(
            data=data, x=x, y=y, width=width,
            box_style=BoxStyle.Round(pad=0.0, rounding_size=width / 2),
            y_0=y_0, h_align=h_align,
            mutation_aspect=mutation_aspect,
            alpha=alpha,
            color=color, edge_color=edge_color, face_color=face_color,
            fill=fill, line_style=line_style, line_width=line_width
        )
        return self

    def add_line(
            self,
            x: FloatIterable, y: FloatIterable,
            smooth: Union[bool, int] = False, smooth_order: int = 2,
            alpha: Optional[float] = None,
            color: Optional[Color] = None,
            draw_style: Optional[Union[str, DRAW_STYLE]] = None,
            label: Optional[str] = None,
            line_style: Optional[LineStyle] = None,
            line_width: Optional[float] = None,
            marker: Optional[Union[str, MARKER_STYLE]] = None,
            marker_edge_color: Optional[Color] = None,
            marker_edge_width: Optional[float] = None,
            marker_face_color: Optional[Color] = None,
            marker_face_color_alt: Optional[Color] = None,
            marker_size: Optional[float] = None,
            z_order: Optional[int] = None
    ) -> 'AxesFormatter':
        """
        Add a line to the plot.

        :param x: X-coordinates of the line.
        :param y: Y-coordinates of the line.
        :param smooth: True or False or number of points. True -> 1,000 points.
        :param smooth_order: Order for smoothing e.g. 2 = quadratic, 3 = cubic
        :param alpha: Opacity of the line.
        :param color: Color of the line.
        :param draw_style: Draw style. One of {'default', 'steps', 'steps-pre',
                           'steps-mid', 'steps-post'}
        :param label: Label.
        :param line_style: Line Style. One of {'-', '--', '-.', ':', '',
                           (offset, on-off-seq), ...}
        :param line_width: Line width.
        :param marker: Marker style.
        :param marker_edge_color: Marker edge color.
        :param marker_edge_width: Marker edge width.
        :param marker_face_color: Marker face color.
        :param marker_face_color_alt: Alt marker face color.
        :param marker_size: Marker size.
        :param z_order: z-order for the line.
        """
        if smooth is not False:
            if smooth is True:
                smooth = 1000
            f_smooth = interp1d(x, y, kind=smooth_order)
            x_smooth = linspace(min(x), max(x), smooth)
            y_smooth = f_smooth(x_smooth)
            x = x_smooth
            y = y_smooth
        if draw_style is not None:
            draw_style = (
                draw_style if isinstance(draw_style, str)
                else DRAW_STYLE.get_name(draw_style)
            )
        if line_style is not None:
            line_style = (
                line_style if isinstance(line_style, str)
                else LINE_STYLE.get_name(line_style)
            )

        self._axes.plot(
            x, y, alpha=alpha, color=color,
            drawstyle=draw_style,
            label=label,
            ls=line_style,
            lw=line_width,
            marker=marker,
            markersize=marker_size,
            mec=marker_edge_color,
            mew=marker_edge_width,
            mfc=marker_face_color,
            mfcalt=marker_face_color_alt,
            zorder=z_order
        )
        return self

    # endregion

    # endregion

    def set_title_font_family(self, font_name: str) -> 'AxesFormatter':
        """
        Set the font family for the Axes title.

        :param font_name: Name of the font.
        """
        self.title.set_font_family(font_name)
        return self

    # region limits

    def get_x_lim(self) -> Tuple[float, float]:
        """
        Return the x-axis view limits.
        """
        return self._axes.get_xlim()

    def get_y_lim(self) -> Tuple[float, float]:
        """
        Return the y-axis view limits.
        """
        return self._axes.get_ylim()

    def set_x_lim(self, left: Optional[float] = None,
                  right: Optional[float] = None) -> 'AxesFormatter':
        """
        Set the limits of the x-axis.

        :param left: Lower limit.
        :param right: Upper limit.
        """
        self._axes.set_xlim(left=left, right=right)
        return self

    def set_y_lim(self, bottom: Optional[float] = None,
                  top: Optional[float] = None) -> 'AxesFormatter':
        """
        Set the limits of the y-axis.

        :param bottom: Lower limit.
        :param top: Upper limit.
        """
        self._axes.set_ylim(bottom=bottom, top=top)
        return self

    def get_x_min(self) -> float:
        """
        Return the x-axis lower view limit.
        """
        return self.get_x_lim()[0]

    def get_x_max(self) -> float:
        """
        Return the x-axis upper view limit.
        """
        return self.get_x_lim()[1]

    def get_x_width(self) -> float:

        return abs(self.get_x_max() - self.get_x_min())

    def get_y_height(self) -> float:

        return abs(self.get_y_max() - self.get_y_min())

    def set_x_min(self, left: float = None) -> 'AxesFormatter':
        """
        Set the x-axis lower view limit.
        """
        self.set_x_lim(left, None)
        return self

    def set_x_max(self, right: float = None) -> 'AxesFormatter':
        """
        Set the x-axis upper view limit.
        """
        self.set_x_lim(None, right)
        return self

    def get_y_min(self) -> float:
        """
        Return the y-axis lower view limit.
        """
        return self.get_y_lim()[0]

    def get_y_max(self) -> float:
        """
        Return the y-axis upper view limit.
        """
        return self.get_y_lim()[1]

    def set_y_min(self, bottom: float = None) -> 'AxesFormatter':
        """
        Set the y-axis lower view limit.
        """
        self.set_y_lim(bottom, None)
        return self

    def set_y_max(self, top: float = None) -> 'AxesFormatter':
        """
        Set the y-axis upper view limit.
        """
        self.set_y_lim(None, top)
        return self

    def width(self, units: FIGURE_UNITS = 'inches') -> float:
        """
        Return the width of the subplot.

        :param units: One of {'inches', 'pixels'}.
        """
        if units not in ('inches', 'pixels'):
            raise ValueError("units not in ('inches', 'pixels')")
        fig = self._axes.figure
        bbox = self.axes.get_window_extent().transformed(
            fig.dpi_scale_trans.inverted()
        )
        width = bbox.width
        if units == 'pixels':
            width *= fig.dpi
        return width

    def height(self, units: FIGURE_UNITS = 'inches') -> float:
        """
        Return the height of the subplot.

        :param units: One of {'inches', 'pixels'}
        """
        if units not in ('inches', 'pixels'):
            raise ValueError("units not in ('inches', 'pixels')")
        fig = self._axes.figure
        bbox = self.axes.get_window_extent().transformed(
            fig.dpi_scale_trans.inverted()
        )
        height = bbox.height
        if units == 'pixels':
            height *= fig.dpi
        return height

    # endregion

    # region frame

    def show_frame(self) -> 'AxesFormatter':
        """
        Show the frame.
        """
        self._axes.set_frame_on(True)
        return self

    def hide_frame(self) -> 'AxesFormatter':
        """
        Hide the frame.
        """
        self._axes.set_frame_on(False)
        return self

    # endregion

    # region grids

    def grid(
            self, value: bool = True,
            which: WHICH_TICKS = 'major',
            axis: WHICH_AXIS = 'both',
            color: Optional[Color] = None,
            line_width: Optional[float] = None,
            line_style: Optional[LineStyle] = None
    ) -> 'AxesFormatter':
        """
        Turn the grid on or off.

        :param value: True or False. Defaults to True.
        :param which: 'major', 'minor' or 'both'
        :param axis: 'x', 'y' or 'both'
        :param color: Color of the lines.
        :param line_width: Line width.
        :param line_style: Line Style. One of {'-', '--', '-.', ':', '',
                           (offset, on-off-seq), ...}
        """
        kwargs = {}
        if color is not None:
            kwargs['color'] = color
        if line_width is not None:
            kwargs['lw'] = line_width
        if line_style is not None:
            kwargs['ls'] = LINE_STYLE.get_line_style(line_style)

        self._axes.grid(b=value, which=which, axis=axis,
                        **kwargs)
        return self

    def add_major_xy_grid(
            self,
            color: Optional[Color] = '#888888',
            line_width: Optional[float] = None,
            line_style: Optional[LineStyle] = None
    ) -> 'AxesFormatter':
        """
        Add a major grid to both axes.

        :param color: Color of the lines.
        :param line_width: Line width.
        :param line_style: Line Style. One of {'-', '--', '-.', ':', '',
                           (offset, on-off-seq), ...}
        """
        self.grid(
            value=True, which='major', axis='both',
            color=color, line_width=line_width, line_style=line_style
        )
        return self

    def add_minor_xy_grid(
            self,
            color: Optional[Color] = '#bbbbbb',
            line_width: Optional[float] = None,
            line_style: Optional[LineStyle] = None
    ) -> 'AxesFormatter':
        """
        Add a minor grid to both axes.

        :param color: Color of the lines.
        :param line_width: Line width.
        :param line_style: Line Style. One of {'-', '--', '-.', ':', '',
                           (offset, on-off-seq), ...}
        """
        self.grid(
            value=True, which='minor', axis='both',
            color=color, line_width=line_width, line_style=line_style
        )
        return self

    def add_major_x_grid(
            self,
            color: Optional[Color] = '#888888',
            line_width: Optional[float] = None,
            line_style: Optional[LineStyle] = None
    ) -> 'AxesFormatter':
        """
        Add a major grid to the x-axis.

        :param color: Color of the lines.
        :param line_width: Line width.
        :param line_style: Line Style. One of {'-', '--', '-.', ':', '',
                           (offset, on-off-seq), ...}
        """
        self.grid(
            value=True, which='major', axis='x',
            color=color, line_width=line_width, line_style=line_style
        )
        return self

    def add_minor_x_grid(
            self,
            color: Optional[Color] = '#bbbbbb',
            line_width: Optional[float] = None,
            line_style: Optional[LineStyle] = None
    ) -> 'AxesFormatter':
        """
        Add a minor grid to the x-axis.

        :param color: Color of the lines.
        :param line_width: Line width.
        :param line_style: Line Style. One of {'-', '--', '-.', ':', '',
                           (offset, on-off-seq), ...}
        """
        self.grid(
            value=True, which='minor', axis='x',
            color=color, line_width=line_width, line_style=line_style
        )
        return self

    def add_major_y_grid(
            self,
            color: Optional[Color] = '#888888',
            line_width: Optional[float] = None,
            line_style: Optional[LineStyle] = None
    ) -> 'AxesFormatter':
        """
        Add a major grid to the y-axis.

        :param color: Color of the lines.
        :param line_width: Line width.
        :param line_style: Line Style. One of {'-', '--', '-.', ':', '',
                           (offset, on-off-seq), ...}
        """
        self.grid(
            value=True, which='major', axis='y',
            color=color, line_width=line_width, line_style=line_style
        )
        return self

    def add_minor_y_grid(
            self,
            color: Optional[Color] = '#bbbbbb',
            line_width: Optional[float] = None,
            line_style: Optional[LineStyle] = None
    ) -> 'AxesFormatter':
        """
        Add a minor grid to the y-axis.

        :param color: Color of the lines.
        :param line_width: Line width.
        :param line_style: Line Style. One of {'-', '--', '-.', ':', '',
                           (offset, on-off-seq), ...}
        """
        self.grid(
            value=True, which='minor', axis='y',
            color=color, line_width=line_width, line_style=line_style
        )
        return self

    # endregion

    def set_axis_below(self,
                       value: bool = True) -> 'AxesFormatter':
        """
        Set whether axis ticks and gridlines are above or below most artists.

        :param value: True or False
        """
        self._axes.set_axisbelow(b=value)
        return self

    def save(self,
             file_path: Union[str, Path],
             file_type: Optional[str] = None) -> 'AxesFormatter':
        """
        Save the plot to disk.

        :param file_path: The file path to save the plot object to.
        :param file_type: The type of file to save.
                          Defaults to png if can't be auto-detected from name.
        """
        save_plot(plot_object=self._axes,
                  file_path=file_path,
                  file_type=file_type)
        return self

    def tight_layout(self) -> 'AxesFormatter':
        """
        Call the tight_layout method on the Axes' figure.
        """
        self._axes.figure.tight_layout()
        return self

    def invert_x_axis(self) -> 'AxesFormatter':
        """
        Invert the x-axis.
        """
        self.x_axis.invert()
        return self

    def invert_y_axis(self) -> 'AxesFormatter':
        """
        Invert the y-axis.
        """
        self.y_axis.invert()
        return self

    def add_legend(
            self,
            handles: Optional[List[PathCollection]] = None,
            labels: Optional[List[str]] = None,
            location: Optional[LegendLocation] = None,
            n_cols: Optional[int] = None,
            font_size: Optional[str] = None,
            font_properties: Optional[Union[FontProperties, dict]] = None,
            line_points: Optional[int] = None,
            scatter_points: Optional[int] = None,
            scatter_y_offsets: Optional[ArrayLike] = None,
            marker_scale: Optional[float] = None,
            frame_on: Optional[bool] = None,
            shadow: Optional[bool] = None,
            frame_alpha: Optional[float] = None,
            face_color: Optional[Color] = None,
            edge_color: Optional[Color] = None,
            mode: Optional[str] = None,
            title: Optional[str] = None,
            title_font_size: Optional[FontSize] = None,
            label_spacing: Optional[float] = None,
            handle_length: Optional[float] = None,
            handle_text_pad: Optional[float] = None,
            border_axes_pad: Optional[float] = None,
            column_spacing: Optional[float] = None
    ) -> LegendFormatter:
        """
        Add a legend to the Axes.

        :param handles: A list of Artists (lines, patches) to be added to the
                        legend.
        :param labels: A list of labels to show next to the artists. The length
                       of handles and labels should be the same. If they are
                       not, they are truncated to the smaller of both lengths.
        :param location: The legend location.
        :param n_cols: The number of columns that the legend has. Default is 1.
        :param font_size: The font size of the legend. If the value is numeric
                          the size will be the absolute font size in points.
                          String values are relative to the current default font
                          size. This argument is only used if font_properties is
                          not specified.
        :param font_properties: The font properties of the legend. If None
                                (default), the current matplotlib.rcParams will
                                be used.
        :param line_points: The number of marker points in the legend when
                            creating a legend entry for a Line2D (line).
                            Default is None, which means using
                            rcParams["legend.numpoints"] (default: 1).
        :param scatter_points: The number of marker points in the legend when
        creating a legend entry for a PathCollection (scatter plot). Default is
        None, which means using rcParams["legend.scatterpoints"] (default: 1).
        :param scatter_y_offsets: The vertical offset (relative to the font
        size) for the markers created for a scatter plot legend entry. 0.0 is at
        the base the legend text, and 1.0 is at the top. To draw all markers at
        the same height, set to [0.5]. Default is [0.375, 0.5, 0.3125].
        :param marker_scale: The relative size of legend markers compared with
                             the originally drawn ones. Default is None, which
                             means using rcParams["legend.markerscale"]
                             (default: 1.0).
        :param frame_on: Whether the legend should be drawn on a patch (frame).
                         Default is None, which means using
                         rcParams["legend.frameon"] (default: True).
        :param shadow: Whether to draw a shadow behind the legend. Default is
                       None, which means using rcParams["legend.shadow"]
                       (default: False).
        :param frame_alpha: The alpha transparency of the legend's background.
                            Default is None, which means using
                            rcParams["legend.framealpha"] (default: 0.8). If
                            shadow is activated and framealpha is None, the
                            default value is ignored.
        :param face_color: The legend's background color. Default is None, which
                           means using rcParams["legend.facecolor"]
                           (default: 'inherit'). If "inherit", use
                           rcParams["axes.facecolor"] (default: 'white').
        :param edge_color: The legend's background patch edge color. Default is
                           None, which means using rcParams["legend.edgecolor"]
                           (default: '0.8'). If "inherit", use take
                           rcParams["axes.edgecolor"] (default: 'black').
        :param mode: If mode is set to "expand" the legend will be horizontally
                     expanded to fill the axes area (or bbox_to_anchor if
                     defines the legend's size).
        :param title: The legend's title. Default is no title (None).
        :param title_font_size: The fontsize of the legend's title. Default is
                                the default fontsize.
        :param label_spacing: The fractional whitespace inside the legend
        border, in font-size units. Default is None, which means using
        rcParams["legend.borderpad"] (default: 0.4).
        :param handle_length: The length of the legend handles, in font-size
        units. Default is None, which means using
        rcParams["legend.handlelength"] (default: 2.0).
        :param handle_text_pad: The pad between the legend handle and text, in
        font-size units. Default is None, which means using
        rcParams["legend.handletextpad"] (default: 0.8).
        :param border_axes_pad: The pad between the axes and legend border, in
        font-size units. Default is None, which means using
        rcParams["legend.borderaxespad"] (default: 0.5).
        :param column_spacing: The spacing between columns, in font-size units.
        Default is None, which means using rcParams["legend.columnspacing"]
        (default: 2.0).
        """
        kwargs = {}
        for kwarg, mpl_arg in zip(
            [handles, labels, n_cols, font_properties, font_size,
             line_points, scatter_points, scatter_y_offsets, marker_scale,
             frame_on, shadow, frame_alpha, face_color, edge_color,
             mode, title, title_font_size, label_spacing, handle_length,
             handle_text_pad, border_axes_pad, column_spacing, location],
            ['handles', 'labels', 'ncol', 'prop', 'fontsize',
             'numpoints', 'scatterpoints', 'scatteryoffsets', 'markerscale',
             'frameon', 'shadow', 'framealpha', 'facecolor', 'edgecolor',
             'mode', 'title', 'title_fontsize', 'labelspacing', 'handlelength',
             'handletextpad', 'borderaxespad', 'columnspacing', 'loc']
        ):
            if kwarg is not None:
                kwargs[mpl_arg] = kwarg
        self._legend = LegendFormatter(self._axes.legend(**kwargs))
        return self._legend

    def twin_x(self) -> 'AxesFormatter':

        return AxesFormatter(self.axes.twinx())

    def twin_y(self) -> 'AxesFormatter':

        return AxesFormatter(self.axes.twiny())

    def show(self) -> 'AxesFormatter':
        """
        Show the figure for the axes.
        """
        plt.show()
        return self
