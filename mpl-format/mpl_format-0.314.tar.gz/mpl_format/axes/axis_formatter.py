from typing import Optional, Tuple

from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.text import Text
from matplotlib.ticker import FuncFormatter, MultipleLocator, FixedLocator

from mpl_format.axes.ticks_formatter import TicksFormatter
from mpl_format.compound_types import FontSize, StringMapper
from mpl_format.literals import ROTATION_MODE, AXIS_SCALE, WHICH_AXIS
from mpl_format.text.text_formatter import TextFormatter
from mpl_format.text.text_list_formatter import TextListFormatter
from mpl_format.utils.number_utils import format_as_integer


class AxisFormatter(object):

    def __init__(self, axis: Axis, direction: WHICH_AXIS, axes: Axes):
        """
        Create a new AxisFormatter

        :param axis: The matplotlib Axis instance to wrap.
        :param direction: 'x' or 'y'
        :param axes: Parent Axes instance.
        """
        self._axis: Axis = axis
        self._direction: str = direction
        self._axes: Axes = axes
        self._label: TextFormatter = TextFormatter(self._axis.label)
        self._ticks: TicksFormatter = TicksFormatter(
            axis=direction, which='both', axes=self._axes)
        self._major_ticks: TicksFormatter = TicksFormatter(
            axis=direction, which='major', axes=self._axes)
        self._minor_ticks: TicksFormatter = TicksFormatter(
            axis=direction, which='minor', axes=self._axes)

    # region properties

    @property
    def axis(self) -> Axis:
        """
        Return the wrapped matplotlib Axis object.
        """
        return self._axis

    @property
    def label(self) -> TextFormatter:
        """
        Return a TextFormatter wrapping the axis label.
        """
        return self._label

    @property
    def tick_labels(self) -> TextListFormatter:

        return TextListFormatter([
            TextFormatter(text) for text in self._axis.get_ticklabels()
        ])

    @property
    def ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the ticks on the axis.
        """
        return self._ticks

    @property
    def major_ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the major ticks on the axis.
        """
        return self._major_ticks

    @property
    def minor_ticks(self) -> TicksFormatter:
        """
        Return a TicksFormatter for the minor ticks on the axis.
        """
        return self._minor_ticks

    # endregion

    # region labels

    def set_label_text(self, text: str) -> 'AxisFormatter':
        """
        Set the text of the Axis label.

        :param text: Text for the Axis label.
        """
        self.label.set_text(text)
        return self

    def set_label_font_family(self, font_name: str) -> 'AxisFormatter':
        """
        Set the font family for the Axis label.

        :param font_name: Name of the font to use.
        """
        self.label.set_font_family(font_name)
        return self

    def replace_label_text(self, old: str, new: str) -> 'AxisFormatter':
        """
        Replace the old label text with the new.

        :param old: The old label text to replace.
        :param new: The new label text to replace.
        """
        self.label.replace(old=old, new=new)
        return self

    def map_label_text(
            self, mapping: StringMapper
    ) -> 'AxisFormatter':
        """
        Map the label text using a dictionary or function.

        :param mapping: Dictionary or a function mapping old text to new text.
        """
        self.label.map(mapping)
        return self

    def rotate_label(
            self, rotation: int,
            how: ROTATION_MODE = 'absolute'
    ) -> 'AxisFormatter':
        """
        Set the rotation of the axis label.

        :param rotation: The rotation value to set in degrees.
        :param how: 'absolute' or 'relative'
        """
        self.label.rotate(rotation, how)
        return self

    def remove_label(self) -> 'AxisFormatter':
        """
        Remove the Axis label.
        """
        self.set_label_text('')
        return self

    def wrap_label(self, max_width: int) -> 'AxisFormatter':
        """
        Wrap the axis label text if it exceeds a given width of characters.

        :param max_width: The maximum character width per line.
        """
        self.label.wrap(max_width=max_width)
        return self

    def set_label_size(self, font_size: FontSize) -> 'AxisFormatter':
        """
        Set the font size for the axis label.

        :param font_size: The font size in points or size name.
        """
        self.label.set_size(font_size)
        return self

    # endregion

    # region tick labels

    def set_format_integer(self,
                           categorical: bool = False,
                           kmbt: bool = False) -> 'AxisFormatter':
        """
        Format an axis with currency symbols and separators.

        :param categorical: Whether the axis is displaying categorical items
                            e.g. for bar plots.
        :param kmbt: Whether to abbreviate numbers using K, M, B and T for
                     thousands, millions, billions and trillions.
        """
        def to_integer(text: Text):
            if isinstance(text, Text):
                t = text.get_text()
            else:
                t = str(text)
            if t == '':
                return ''
            number = float(t)
            return format_as_integer(number=number, kmbt=kmbt)

        if not categorical:
            tick = FuncFormatter(lambda x, pos: to_integer(x))
            self._axis.set_major_formatter(tick)
        else:
            self._axis.set_ticklabels([
                to_integer(text) for text in self._axis.get_ticklabels()
            ])

        return self

    def set_format_currency(
            self,
            symbol: str = '$',
            num_decimals: int = 0,
            categorical: bool = False,
            kmbt: bool = False
    ) -> 'AxisFormatter':
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

        def to_currency(text: Text):
            if isinstance(text, Text):
                t = text.get_text()
            else:
                t = str(text)
            if t == '':
                return ''
            number = float(t)
            if not kmbt:
                return f'{symbol}{number:,.{num_decimals}f}'
            else:
                for power, abbrev in zip(
                        [12, 9, 6, 3],
                        ['T', 'B', 'M', 'K']
                ):
                    if number >= 10 ** power:
                        num = number / 10 ** power
                        if num == int(num):
                            num = int(num)
                        return f'{symbol}{num:,}{abbrev}'
                if number == int(number):
                    number = int(number)
                return f'{symbol}{number:,.{num_decimals}f}'

        if not categorical:
            tick = FuncFormatter(lambda x, pos: to_currency(x))
            self._axis.set_major_formatter(tick)
        else:
            self._axis.set_ticklabels([
                to_currency(text) for text in self._axis.get_ticklabels()
            ])

        return self

    def set_format_percent(
            self,
            num_decimals: int = 0,
            multiply_100: bool = True,
            categorical: bool = False
    ) -> 'AxisFormatter':
        """
        Format an axis as a percentage.

        :param num_decimals: Number of decimal places for the resulting label.
        :param multiply_100: Whether to multiply the existing value by 100
                             before formatting.
        :param categorical: Whether the axis is displaying categorical items
                            e.g. for bar plots.
        """
        if not categorical:
            def percent_formatter(value, pos):
                value = float(value)
                if multiply_100:
                    value *= 100
                return f'{value:.{num_decimals}f}%'
            self._axis.set_major_formatter(FuncFormatter(percent_formatter))
        else:
            def to_percent(text: Text):
                t = text.get_text()
                if t == '':
                    return ''
                number = float(t)
                if multiply_100:
                    number *= 100
                return f'{number:.{num_decimals}f}%'
            self._axis.set_ticklabels([
                to_percent(text) for text in self._axis.get_ticklabels()
            ])

        return self

    # endregion

    # region set scale

    def set_scale(self, scale: AXIS_SCALE) -> 'AxisFormatter':
        """
        Set the scale for the Axis.

        :param scale: One of ['log', 'linear', 'symlog', 'logit']
        """
        if self._direction == 'x':
            self._axes.set_xscale(value=scale)
        else:
            self._axes.set_yscale(value=scale)
        return self

    def set_scale_log(self) -> 'AxisFormatter':
        """
        Set the scale of the axis to logarithmic.
        """
        self.set_scale('log')
        return self

    def set_scale_linear(self) -> 'AxisFormatter':
        """
        Set the scale of the axis to logarithmic.
        """
        self.set_scale('linear')
        return self

    def set_scale_symmetrical_log(self) -> 'AxisFormatter':
        """
        Set the scale of the axis to symmetrical logarithmic.
        """
        self.set_scale('symlog')
        return self

    def set_scale_logit(self) -> 'AxisFormatter':
        """
        Set the scale of the axis to logit.
        """
        self.set_scale('logit')
        return self

    # endregion

    # region inversion

    def set_inverted(self, inverted: bool = True) -> 'AxisFormatter':
        """
        Set the Axis inversion property.

        :param inverted: True or False.
        """
        self._axis.set_inverted(inverted=inverted)
        return self

    def invert(self) -> 'AxisFormatter':
        """
        Flip the Axis inversion property.
        """
        self._axis.set_inverted(inverted=not self._axis.get_inverted())
        return self

    # endregion

    # region tick spacing

    def set_tick_spacing(
            self, major: float,
            minor: Optional[float] = None,
            major_offset: float = 0,
            categorical: bool = False
    ) -> 'AxisFormatter':
        """
        Set the spacing of ticks on the Axis.

        :param major: Spacing for major ticks.
        :param minor: Optional spacing for minor ticks.
        :param major_offset: Optional offset index to start major ticks.
                             Only applies if categorical is True.
        :param categorical: Whether the axis is displaying categorical items
                            e.g. for bar plots.
        """
        if categorical:
            self._axis.set_major_locator(
                FixedLocator([
                    t for t in self._axis.get_ticklocs()
                    if (t - major_offset) % major == 0
                ])
            )
            if minor is not None:
                self._axis.set_minor_locator(MultipleLocator(minor))
        else:
            self._axis.set_major_locator(MultipleLocator(base=major))
            if minor is not None:
                self._axis.set_minor_locator(MultipleLocator(base=minor))

        return self

    def keep_ticks(
            self,
            label_spacing: Optional[int] = None,
            tick_spacing: Optional[int] = None,
            start: int = 0, end: Optional[int] = None
    ) -> 'AxisFormatter':
        """
        Keep only some tick labels and locations of a categorical axis.

        :param label_spacing: Spacing of labels to keep.
        :param tick_spacing: Spacing of ticks to keep.
        :param start: Index of the first label to keep.
        :param end: Index of the last label to keep,
                    if it is n * spacing from start.
        """
        if label_spacing is not None:
            labels = self._axis.get_ticklabels()
            num_labels = len(labels)
            if end is None or end > num_labels - 1:
                end = num_labels - 1
            self._axis.set_ticklabels([
                label.get_text() if (
                        start <= i <= end and (i - start) % label_spacing == 0
                ) else Text()
                for i, label in enumerate(labels)
            ])
        if tick_spacing is not None:
            locations = self._axis.get_ticklocs()
            self._axis.set_ticks([
                location for i, location in enumerate(locations)
                if (i - start) % tick_spacing == 0
            ])
        return self

    # endregion

    # region limits

    def get_lim(self) -> Tuple[float, float]:
        """
        Return the axis view limits.
        """
        if self._direction == 'x':
            return self._axes.get_xlim()
        else:
            return self._axes.get_ylim()

    def get_min(self) -> float:
        """
        Return the axis lower view limit.
        """
        if self._direction == 'x':
            return self._axes.get_xlim()[0]
        else:
            return self._axes.get_ylim()[0]

    def get_max(self) -> float:
        """
        Return the axis upper view limit.
        """
        if self._direction == 'x':
            return self._axes.get_xlim()[1]
        else:
            return self._axes.get_ylim()[1]

    def set_min(self, value: float = None) -> 'AxisFormatter':
        """
        Set the axis lower view limit.
        """
        if self._direction == 'x':
            self._axes.set_xlim(value, None)
        else:
            self._axes.set_ylim(value, None)
        return self

    def set_max(self, value: float = None) -> 'AxisFormatter':
        """
        Set the axis upper view limit.
        """
        if self._direction == 'x':
            self._axes.set_xlim(None, value)
        else:
            self._axes.set_ylim(None, value)
        return self

    # endregion
