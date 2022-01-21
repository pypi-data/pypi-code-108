from matplotlib.text import Text
from typing import Dict, Union, Callable

from mpl_format.compound_types import FontSize
from mpl_format.enums import FONT_SIZE
from mpl_format.literals import ROTATION_MODE, H_ALIGN, TEXT_V_ALIGN
from mpl_format.text.text_utils import wrap_text, remove_parenthesized_text, \
    HORIZONTAL_ALIGNMENTS, VERTICAL_ALIGNMENTS


class TextFormatter(object):

    def __init__(self, text: Text):
        """
        Create a new TextFormatter for a matplotlib Text instance.

        :param text: The matplotlib Text instance to wrap.
        """
        self._text: Text = text

    @property
    def text(self) -> Text:
        """
        Return the wrapped matplotlib Text instance.
        """
        return self._text

    def to_string(self) -> str:
        """
        Return the text of the wrapped matplotlib Text instance.
        """
        return self._text.get_text()

    def wrap(self, max_width: int) -> 'TextFormatter':
        """
        Wrap the text with new lines if it exceeds a given width of characters.

        :param max_width: The maximum character width per line.
        """
        wrapped = wrap_text(self.to_string(), max_width=max_width)
        self._text.set_text(wrapped)
        return self

    def rotate(
            self, rotation: Union[str, int],
            how: ROTATION_MODE = 'absolute'
    ) -> 'TextFormatter':
        """
        Set the rotation of the text.

        :param rotation: The rotation value to set in degrees, 'horizontal'
                         or 'vertical'.
        :param how: 'absolute' or 'relative'
        """
        if how == 'relative' and not isinstance(rotation, str):
            self._text.set_rotation(self._text.get_rotation() + rotation)
        elif how == 'absolute':
            self._text.set_rotation(rotation)
        else:
            raise ValueError("`how` must be 'absolute' or 'relative'")
        return self

    def map(
            self, mapping: Union[Dict[str, str], Callable[[str], str]]
    ) -> 'TextFormatter':
        """
        Replace text using a dictionary or function.

        :param mapping: Mappings to replace text.
        """
        if isinstance(mapping, dict):
            if self.to_string() in mapping.keys():
                self._text.set_text(mapping[self.to_string()])
        elif callable(mapping):
            self._text.set_text(mapping(self.to_string()))
        else:
            raise TypeError('mapping must be a dict or callable')
        return self

    def remove_parenthesized_text(self) -> 'TextFormatter':
        """
        Remove any text inside parentheses, along with the parentheses.
        """
        self._text.set_text(remove_parenthesized_text(self.to_string()))
        return self

    def replace(self, old: str, new: str) -> 'TextFormatter':
        """
        Replace old text with new text.

        :param old: The text to remove.
        :param new: The text to insert.
        """
        self._text.set_text(
            self.to_string().replace(old, new)
        )
        return self

    def set_text(self, text: str) -> 'TextFormatter':
        """
        Set the text string.
        """
        self._text.set_text(text)
        return self

    def clear(self) -> 'TextFormatter':
        """
        Clear the text string.
        """
        self.set_text('')
        return self

    # region set size

    def set_size(self, font_size: FontSize) -> 'TextFormatter':
        """
        Set the font size for the Text.
        """
        if isinstance(font_size, FONT_SIZE):
            font_size = font_size.get_name()
        self._text.set_fontsize(font_size)
        return self
    
    def set_size_xx_small(self) -> 'TextFormatter':
        self.set_size('xx-small')
        return self

    def set_size_x_small(self) -> 'TextFormatter':
        self.set_size('x-small')
        return self

    def set_size_small(self) -> 'TextFormatter':
        self.set_size('small')
        return self

    def set_size_medium(self) -> 'TextFormatter':
        self.set_size('medium')
        return self

    def set_size_large(self) -> 'TextFormatter':
        self.set_size('large')
        return self

    def set_size_x_large(self) -> 'TextFormatter':
        self.set_size('x-large')
        return self

    def set_size_xx_large(self) -> 'TextFormatter':
        self.set_size('xx-large')
        return self

    def set_size_larger(self) -> 'TextFormatter':
        self.set_size('larger')
        return self

    def set_size_smaller(self) -> 'TextFormatter':
        self.set_size('smaller')
        return self

    # endregion

    # region set font family

    def set_font_family(self, font_name: str) -> 'TextFormatter':
        """
        Set the font family to the given font name.

        :param font_name: Name of the font to set.
        """
        self._text.set_fontfamily(fontname=font_name)
        return self

    def set_font_family_serif(self) -> 'TextFormatter':
        """
        Set the font family to 'serif'
        """
        self.set_font_family('serif')
        return self

    def set_font_family_sans_serif(self) -> 'TextFormatter':
        """
        Set the font family to 'sans-serif'
        """
        self.set_font_family('sans-serif')
        return self

    def set_font_family_cursive(self) -> 'TextFormatter':
        """
        Set the font family to 'cursive'
        """
        self.set_font_family('cursive')
        return self

    def set_font_family_fantasy(self) -> 'TextFormatter':
        """
        Set the font family to 'fantasy'
        """
        self.set_font_family('fantasy')
        return self

    def set_font_family_monospace(self) -> 'TextFormatter':
        """
        Set the font family to 'monospace'
        """
        self.set_font_family('monospace')
        return self

    def set_font_family_benton_sans_f(self) -> 'TextFormatter':
        """
        Set the font family to 'BentonSansF'
        """
        self.set_font_family('BentonSansF')
        return self

    def set_font_family_quarto(self) -> 'TextFormatter':
        """
        Set the font family to 'Quarto'
        """
        self.set_font_family('Quarto')
        return self

    def set_font_family_calibri(self) -> 'TextFormatter':
        """
        Set the font family to 'Calibri'
        """
        self.set_font_family('Calibri')
        return self

    # endregion

    # region set alignment

    def set_ha(self, alignment: H_ALIGN) -> 'TextFormatter':

        if alignment not in HORIZONTAL_ALIGNMENTS:
            raise ValueError(
                f'alignment must be one of {HORIZONTAL_ALIGNMENTS}'
            )
        self._text.set_horizontalalignment(align=alignment)
        return self

    def set_ha_left(self) -> 'TextFormatter':

        return self.set_ha('left')

    def set_ha_center(self) -> 'TextFormatter':

        return self.set_ha('center')

    def set_ha_right(self) -> 'TextFormatter':

        return self.set_ha('right')

    def set_va(self, alignment: TEXT_V_ALIGN) -> 'TextFormatter':

        if alignment not in VERTICAL_ALIGNMENTS:
            raise ValueError(
                f'alignment must be one of {VERTICAL_ALIGNMENTS}'
            )
        self._text.set_verticalalignment(align=alignment)
        return self

    def set_va_top(self) -> 'TextFormatter':

        return self.set_va('top')

    def set_va_center(self) -> 'TextFormatter':

        return self.set_va('center')

    def set_va_bottom(self) -> 'TextFormatter':

        return self.set_va('bottom')

    def set_va_baseline(self) -> 'TextFormatter':

        return self.set_va('baseline')

    def set_va_center_baseline(self) -> 'TextFormatter':

        return self.set_va('center_baseline')

    # endregion
