from typing import Union, List, Optional

from matplotlib.collections import PathCollection
from matplotlib.font_manager import FontProperties
from matplotlib.legend import Legend

from compound_types.arrays import ArrayLike
from mpl_format.compound_types import Color, FontSize, LegendLocation, \
    StringMapper
from mpl_format.text.text_formatter import TextFormatter
from mpl_format.text.text_utils import map_text


class LegendFormatter(object):

    def __init__(self, legend: Legend):
        """
        Create a new legend formatter.
        """
        self._legend: Legend = legend

    @property
    def legend(self) -> Legend:
        return self._legend

    @property
    def title(self) -> TextFormatter:
        """
        Return a TextFormatter around the legend's title.
        """
        return TextFormatter(self._legend.get_title())

    # region set location

    def set_location(self, location: Union[int, str]) -> 'LegendFormatter':
        """
        Set the legend location.
        """
        self.recreate_legend(location=location)
        return self

    def set_location_best(self) -> 'LegendFormatter':
        """
        Set the legend location to 'best'.
        """
        self.set_location('best')
        return self

    def set_location_upper_left(self) -> 'LegendFormatter':
        """
        Set the legend location to 'upper left'.
        """
        self.set_location('upper left')
        return self

    def set_location_upper_center(self) -> 'LegendFormatter':
        """
        Set the legend location to 'upper center'.
        """
        self.set_location('upper center')
        return self

    def set_location_upper_right(self) -> 'LegendFormatter':
        """
        Set the legend location to 'upper right'.
        """
        self.set_location('upper right')
        return self

    def set_location_center_left(self) -> 'LegendFormatter':
        """
        Set the legend location to 'center left'.
        """
        self.set_location('center left')
        return self

    def set_location_center(self) -> 'LegendFormatter':
        """
        Set the legend location to 'center'.
        """
        self.set_location('center')
        return self

    def set_location_center_right(self) -> 'LegendFormatter':
        """
        Set the legend location to 'center right'.
        """
        self.set_location('center right')
        return self

    def set_location_lower_left(self) -> 'LegendFormatter':
        """
        Set the legend location to 'lower left'.
        """
        self.set_location('lower left')
        return self

    def set_location_lower_center(self) -> 'LegendFormatter':
        """
        Set the legend location to 'lower center'.
        """
        self.set_location('lower center')
        return self

    def set_location_lower_right(self) -> 'LegendFormatter':
        """
        Set the legend location to 'lower right'.
        """
        self.set_location('lower right')
        return self

    def set_location_left(self) -> 'LegendFormatter':
        """
        Set the legend location to 'center left'.
        """
        self.set_location('center left')
        return self

    def set_location_right(self) -> 'LegendFormatter':
        """
        Set the legend location to 'center right'.
        """
        self.set_location('center right')
        return self

    # endregion

    def recreate_legend(
            self, handles: Optional[List[PathCollection]] = None,
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
            column_spacing: Optional[float] = None) -> 'LegendFormatter':
        """

        :param handles: A list of Artists (lines, patches) to be added to the
                        legend.
        :param labels: A list of labels to show next to the artists. The length
                       of handles and labels should be the same. If they are
                       not, they are truncated to the smaller of both lengths.
        :param location: The location of the legend.
        :param n_cols: The number of columns that the legend has. Default is 1.
        :param font_size: The font size of the legend. If the value is numeric
                          the size will be the absolute font size in points.
                          String values are relative to the current default font
                          size. This argument is only used if font_properties is
                          not specified.
        :param font_properties: The font properties of the legend. If None
                                (default), the current matplotlib.rcParams
                                will be used.
        :param line_points: The number of marker points in the legend when
                            creating a legend entry for a Line2D (line).
                            Default is None, which means using
                            rcParams["legend.numpoints"] (default: 1).
        :param scatter_points: The number of marker points in the legend when
                               creating a legend entry for a PathCollection
                               (scatter plot). Default is None, which means
                               using rcParams["legend.scatterpoints"]
                               (default: 1).
        :param scatter_y_offsets: The vertical offset (relative to the font
                                  size) for the markers created for a scatter
                                  plot legend entry. 0.0 is at the base the
                                  legend text, and 1.0 is at the top. To draw
                                  all markers at the same height, set to [0.5].
                                  Default is [0.375, 0.5, 0.3125].
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
        :param face_color: The legend's background color. Default is None,
                           which means using rcParams["legend.facecolor"]
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
                              border, in font-size units. Default is None,
                              which means using rcParams["legend.borderpad"]
                              (default: 0.4).
        :param handle_length: The length of the legend handles, in font-size
                              units. Default is None, which means using
                              rcParams["legend.handlelength"] (default: 2.0).
        :param handle_text_pad: The pad between the legend handle and text, in
                                font-size units. Default is None, which means
                                using rcParams["legend.handletextpad"]
                                (default: 0.8).
        :param border_axes_pad: The pad between the axes and legend border, in
                                font-size units. Default is None, which means
                                using rcParams["legend.borderaxespad"]
                                (default: 0.5).
        :param column_spacing: The spacing between columns, in font-size units.
                               Default is None, which means using
                               rcParams["legend.columnspacing"] (default: 2.0).
        """
        kwargs = {}
        for kwarg, mpl_arg in zip(
                [handles, labels, n_cols, font_properties, font_size,
                 line_points, scatter_points, scatter_y_offsets,
                 marker_scale, frame_on, shadow, frame_alpha, face_color,
                 edge_color, mode, title,
                 title_font_size, label_spacing, handle_length, handle_text_pad,
                 border_axes_pad, column_spacing,
                 location],
                ['handles', 'labels', 'ncol', 'prop', 'fontsize', 'numpoints',
                 'scatterpoints', 'scatteryoffsets',
                 'markerscale', 'frameon', 'shadow', 'framealpha', 'facecolor',
                 'edgecolor', 'mode', 'title',
                 'title_fontsize', 'labelspacing', 'handlelength',
                 'handletextpad', 'borderaxespad', 'columnspacing',
                 'loc']
        ):
            if kwarg is not None:
                kwargs[mpl_arg] = kwarg

        if 'handles' not in kwargs.keys():
            kwargs['handles'] = self._legend.legendHandles
        if 'labels' not in kwargs.keys():
            kwargs['labels'] = [text.get_text() for text in self._legend.texts]

        self._legend = self._legend.axes.legend(**kwargs)
        return self

    def remove_entries(self, indices: List[int]) -> 'LegendFormatter':
        """
        Remove legend handles and labels from the legend at the given indices.
        N.B. this creates a new legend. May need to set the following properties
        manually afterwards as they cannot be automatically determined from the
        old legend:
        ['loc', 'markerfirst', 'fancybox', 'bbox_to_anchor' 'bbox_transform',
        'handler_map']

        :param indices: The indices of the legend entries to remove.
        """
        handles = self._legend.legendHandles
        labels = [text.get_text() for text in self._legend.texts]
        for entry_index in sorted(indices, reverse=True):
            handles.pop(entry_index)
            labels.pop(entry_index)
        legend = self._legend
        self.recreate_legend(
            handles=handles, labels=labels,
            n_cols=legend._ncol,
            font_properties=legend.prop,
            line_points=legend.numpoints,
            scatter_points=legend.scatterpoints,
            scatter_y_offsets=legend._scatteryoffsets,
            marker_scale=legend.markerscale,
            frame_on=legend.get_frame_on(),
            shadow=legend.shadow,
            frame_alpha=legend.get_frame().get_alpha(),
            face_color=legend.get_frame().get_facecolor(),
            edge_color=legend.get_frame().get_edgecolor(),
            mode=legend._mode,
            title=legend.get_title().get_text(),
            title_font_size=legend.get_title().get_fontsize(),
            label_spacing=legend.labelspacing,
            handle_length=legend.handlelength,
            handle_text_pad=legend.handletextpad,
            border_axes_pad=legend.borderaxespad,
            column_spacing=legend.columnspacing
        )
        return self

    def map_labels(
            self, mapping: StringMapper
    ) -> 'LegendFormatter':
        """
        Replace label text using a dictionary or function.

        :param mapping: Mappings to replace text.
        """
        handles, labels = self._legend.axes.get_legend_handles_labels()
        labels = [map_text(text=label, mapping=mapping) for label in labels]
        self.recreate_legend(labels=labels)
        return self

    def set_alpha(self, alpha: float) -> 'LegendFormatter':
        """
        Set the opacity of the legend frame.
        """
        self._legend.set_alpha(alpha=alpha)
        return self

    def set_face_color(self, color: Color) -> 'LegendFormatter':
        """
        Set the face color of the legend frame.
        """
        self._legend.get_frame().set_facecolor(color)
        return self

    def set_edge_color(self, color: Color) -> 'LegendFormatter':
        """
        Set the edge color of the legend frame.
        """
        self._legend.get_frame().set_edgecolor(color)
        return self

    def set_frame_on(self, on: bool = True) -> 'LegendFormatter':
        """
        Turn the frame on or off.
        """
        self._legend.set_frame_on(b=on)
        return self

    def set_z_order(self, level: int) -> 'LegendFormatter':
        """
        Set the z-order of the legend.
        """
        self._legend.set_zorder(level=level)
        return self

    def set_title_text(self, text: str) -> 'LegendFormatter':
        """
        Set the text of the legend title.
        """
        self.title.set_text(text)
        return self

    def set_title_font_family(self, font_name: str) -> 'LegendFormatter':
        """
        Set the font family of the legend title.
        """
        self.title.set_font_family(font_name)
        return self

    def set_title_font_size(self, font_size: FontSize) -> 'LegendFormatter':
        """
        Set the font size of the legend title.
        """
        self.title.set_size(font_size=font_size)
        return self

    def set_n_cols(self, n_cols: int) -> 'LegendFormatter':
        """
        Set the number of columns the legend has.

        N.B. this creates a new legend. May need to set the following properties
        manually afterwards as they cannot be automatically determined from the
        old legend:
        ['loc', 'markerfirst', 'fancybox', 'bbox_to_anchor' 'bbox_transform',
        'handler_map']
        """
        self.recreate_legend(n_cols=n_cols)
        return self

    def set_line_points(self, num_points: int) -> 'LegendFormatter':
        """
        Set the number of points for a line legend entry.

        N.B. this creates a new legend. May need to set the following properties
        manually afterwards as they cannot be automatically determined from the
        old legend:
        ['loc', 'markerfirst', 'fancybox', 'bbox_to_anchor' 'bbox_transform',
        'handler_map']
        """
        self.recreate_legend(line_points=num_points)
        return self

    def set_scatter_points(self, num_points: int) -> 'LegendFormatter':
        """
        Set the number of points for a scatter legend entry.

        N.B. this creates a new legend. May need to set the following properties
        manually afterwards as they cannot be automatically determined from the
        old legend:
        ['loc', 'markerfirst', 'fancybox', 'bbox_to_anchor' 'bbox_transform',
        'handler_map']
        """
        self.recreate_legend(scatter_points=num_points)
        return self

    def set_shadow(self, on: bool = True) -> 'LegendFormatter':
        """
        Turn the shadow on or off for the legend frame.
        """
        self._legend.shadow = on
        return self
