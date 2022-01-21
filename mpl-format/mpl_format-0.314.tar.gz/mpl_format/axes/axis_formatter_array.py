from typing import Iterable, Iterator, Tuple

from numpy import ndarray

from mpl_format.axes import AxisFormatter
from mpl_format.compound_types import StringMapper, FontSize
from mpl_format.literals import ROTATION_MODE, AXIS_SCALE


class AxisFormatterArray(object):

    def __init__(self, axes: ndarray):
        """
        Create a new AxesFormatterArray

        :param axes: Array of AxisFormatter instances.
        """
        self._axes = axes

    def axes(self) -> Iterable[AxisFormatter]:

        return self._axes

    def __getitem__(self, item) -> AxisFormatter:

        return self._axes[item]

    @property
    def flat(self) -> Iterator[AxisFormatter]:
        return self._axes.flat

    @property
    def n_dim(self) -> int:
        return self._axes.ndim

    @property
    def size(self) -> int:
        return self._axes.size

    @property
    def shape(self) -> Tuple[int, ...]:
        return self._axes.shape

    # region labels

    def set_label_text(self, text: str) -> 'AxisFormatterArray':
        """
        Set the text of the Axis label.

        :param text: Text for the Axis label.
        """
        for axis in self._axes.flat:
            axis.set_label_text(text=text)
        return self

    def set_label_font_family(self, font_name: str) -> 'AxisFormatterArray':
        """
        Set the font family for the Axis label.

        :param font_name: Name of the font to use.
        """
        for axis in self._axes.flat:
            axis.set_label_font_family(font_name=font_name)
        return self

    def replace_label_text(self, old: str, new: str) -> 'AxisFormatterArray':
        """
        Replace the old label text with the new.

        :param old: The old label text to replace.
        :param new: The new label text to replace.
        """
        for axis in self._axes.flat:
            axis.replace_label_text(old=old, new=new)
        return self

    def map_label_text(
            self, mapping: StringMapper
    ) -> 'AxisFormatterArray':
        """
        Map the label text using a dictionary or function.

        :param mapping: Dictionary or a function mapping old text to new text.
        """
        for axis in self._axes.flat:
            axis.map_label_text(mapping=mapping)
        return self

    def rotate_label(
            self, rotation: int,
            how: ROTATION_MODE = 'absolute'
    ) -> 'AxisFormatterArray':
        """
        Set the rotation of the axis label.

        :param rotation: The rotation value to set in degrees.
        :param how: 'absolute' or 'relative'
        """
        for axis in self._axes.flat:
            axis.rotate_label(
                rotation=rotation,
                how=how
            )
        return self

    def remove_label(self) -> 'AxisFormatterArray':
        """
        Remove the Axis label.
        """
        for axis in self._axes.flat:
            axis.remove_label()
        return self

    def wrap_label(self, max_width: int) -> 'AxisFormatterArray':
        """
        Wrap the axis label text if it exceeds a given width of characters.

        :param max_width: The maximum character width per line.
        """
        for axis in self._axes.flat:
            axis.wrap_label(max_width=max_width)
        return self

    def set_label_size(self, font_size: FontSize) -> 'AxisFormatterArray':
        """
        Set the font size for the axis label.

        :param font_size: The font size in points or size name.
        """
        for axis in self._axes.flat:
            axis.set_label_size(font_size=font_size)
        return self

    # endregion
    
    # region tick labels

    def rotate_tick_labels(
            self, rotation: int,
            how: ROTATION_MODE = 'absolute'
    ) -> 'AxisFormatterArray':
        """
        Set the rotation of axis tick labels.

        :param rotation: The rotation value to set in degrees.
        :param how: 'absolute' or 'relative'
        """
        for axis in self._axes.flat:
            axis.rotate_tick_labels(
                rotation=rotation, how=how
            )
        return self

    def wrap_tick_labels(self, max_width: int) -> 'AxisFormatterArray':
        """
        Wrap the text for each tick label with new lines if it exceeds
        a given width of characters.

        :param max_width: The maximum character width per line.
        """
        for axis in self._axes.flat:
            axis.wrap_tick_labels(max_width=max_width)
        return self

    def set_format_integer(self,
                           categorical: bool = False,
                           kmbt: bool = False) -> 'AxisFormatterArray':
        """
        Format an axis with currency symbols and separators.

        :param categorical: Whether the axis is displaying categorical items
                            e.g. for bar plots.
        :param kmbt: Whether to abbreviate numbers using K, M, B and T for
                     thousands, millions, billions and trillions.
        """
        for axis in self._axes.flat:
            axis.set_format_integer(
                categorical=categorical, kmbt=kmbt
            )
        return self

    def set_format_currency(
            self, symbol: str = '$', num_decimals: int = 0,
            categorical: bool = False,
            kmbt: bool = False
    ) -> 'AxisFormatterArray':
        """
        Format an axis with currency symbols and separators.

        :param symbol: The currency symbol to use.
        :param num_decimals: The number of decimal places to use
                             (typically 0 or 2).
        :param categorical: Whether the axis is displaying categorical items
                            e.g. for bar plots.
        :param kmbt: Whether to abbreviate numbers using K, M, B and T for
                     thousands, millions, billions and trillions.
        """
        for axis in self._axes.flat:
            axis.set_format_currency(
                symbol=symbol,
                num_decimals=num_decimals,
                categorical=categorical,
                kmbt=kmbt
            )
        return self

    def set_format_percent(self, num_decimals: int = 0,
                           multiply_100: bool = True,
                           categorical: bool = False) -> 'AxisFormatterArray':
        """
        Format an axis as a percentage.

        :param num_decimals: Number of decimal places for the resulting label.
        :param multiply_100: Whether to multiply the existing value by 100
                             before formatting.
        :param categorical: Whether the axis is displaying categorical items
                            e.g. for bar plots.
        """
        for axis in self._axes.flat:
            axis.set_format_percent(
                num_decimals=num_decimals,
                multiply_100=multiply_100,
                categorical=categorical
            )
        return self

    def set_tick_label_size(self, font_size: FontSize) -> 'AxisFormatterArray':
        """
        Set the font size for the axis tick labels.

        :param font_size: The font size in points or size name.
        """
        for axis in self._axes.flat:
            axis.set_tick_label_size(font_size=font_size)
        return self

    def map_tick_label_text(
            self, mapping: StringMapper
    ) -> 'AxisFormatterArray':
        """
        Map the tick label text using a dictionary or function.

        :param mapping: Dictionary or a function mapping old text to new text.
        """
        for axis in self._axes.flat:
            axis.map_tick_label_text(mapping=mapping)
        return self

    # endregion

    # region set scale

    def set_scale(self, scale: AXIS_SCALE) -> 'AxisFormatterArray':
        """
        Set the scale for the Axis.

        :param scale: One of ['log', 'linear', 'symlog', 'logit']
        """
        for axis in self._axes.flat:
            axis.set_scale(scale=scale)
        return self

    def set_scale_log(self) -> 'AxisFormatterArray':
        """
        Set the scale of the axis to logarithmic.
        """
        for axis in self._axes.flat:
            axis.set_scale_log()
        return self

    def set_scale_linear(self) -> 'AxisFormatterArray':
        """
        Set the scale of the axis to logarithmic.
        """
        for axis in self._axes.flat:
            axis.set_scale_linear()
        return self

    def set_scale_symmetrical_log(self) -> 'AxisFormatterArray':
        """
        Set the scale of the axis to symmetrical logarithmic.
        """
        for axis in self._axes.flat:
            axis.set_scale_symmetrical_log()
        return self

    def set_scale_logit(self) -> 'AxisFormatterArray':
        """
        Set the scale of the axis to logit.
        """
        for axis in self._axes.flat:
            axis.set_scale_logit()
        return self

    # endregion
    
    # region inversion

    def set_inverted(self, inverted: bool = True) -> 'AxisFormatterArray':
        """
        Set the Axis inversion property.

        :param inverted: True or False.
        """
        for axis in self._axes.flat:
            axis.set_inverted(inverted=inverted)
        return self

    def invert(self) -> 'AxisFormatterArray':
        """
        Flip the Axis inversion property.
        """
        for axis in self._axes.flat:
            axis.invert()
        return self

    # endregion
