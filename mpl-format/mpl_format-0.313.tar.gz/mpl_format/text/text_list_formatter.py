from typing import List

from mpl_format.compound_types import FontSize
from mpl_format.literals import TEXT_V_ALIGN, H_ALIGN
from mpl_format.text.text_formatter import TextFormatter
from mpl_format.text.text_utils import \
    HORIZONTAL_ALIGNMENTS, VERTICAL_ALIGNMENTS


class TextListFormatter(object):

    def __init__(self, text_list: List[TextFormatter]):

        self._text_list: List[TextFormatter] = text_list

    # region set size

    def set_size(self, font_size: FontSize) -> 'TextListFormatter':
        """
        Set the font size for each Text element.
        """
        for text in self._text_list:
            text.set_size(font_size)
        return self

    def set_size_xx_small(self) -> 'TextListFormatter':
        self.set_size('xx-small')
        return self

    def set_size_x_small(self) -> 'TextListFormatter':
        self.set_size('x-small')
        return self

    def set_size_small(self) -> 'TextListFormatter':
        self.set_size('small')
        return self

    def set_size_medium(self) -> 'TextListFormatter':
        self.set_size('medium')
        return self

    def set_size_large(self) -> 'TextListFormatter':
        self.set_size('large')
        return self

    def set_size_x_large(self) -> 'TextListFormatter':
        self.set_size('x-large')
        return self

    def set_size_xx_large(self) -> 'TextListFormatter':
        self.set_size('xx-large')
        return self

    def set_size_larger(self) -> 'TextListFormatter':
        self.set_size('larger')
        return self

    def set_size_smaller(self) -> 'TextListFormatter':
        self.set_size('smaller')
        return self

    # endregion

    # region set font family

    def set_font_family(self, font_name: str) -> 'TextListFormatter':
        """
        Set the font family to the given font name.

        :param font_name: Name of the font to set.
        """
        for text in self._text_list:
            text.set_font_family(font_name)
        return self

    def set_font_family_serif(self) -> 'TextListFormatter':
        """
        Set the font family to 'serif'
        """
        self.set_font_family('serif')
        return self

    def set_font_family_sans_serif(self) -> 'TextListFormatter':
        """
        Set the font family to 'sans-serif'
        """
        self.set_font_family('sans-serif')
        return self

    def set_font_family_cursive(self) -> 'TextListFormatter':
        """
        Set the font family to 'cursive'
        """
        self.set_font_family('cursive')
        return self

    def set_font_family_fantasy(self) -> 'TextListFormatter':
        """
        Set the font family to 'fantasy'
        """
        self.set_font_family('fantasy')
        return self

    def set_font_family_monospace(self) -> 'TextListFormatter':
        """
        Set the font family to 'monospace'
        """
        self.set_font_family('monospace')
        return self

    def set_font_family_benton_sans_f(self) -> 'TextListFormatter':
        """
        Set the font family to 'BentonSansF'
        """
        self.set_font_family('BentonSansF')
        return self

    def set_font_family_quarto(self) -> 'TextListFormatter':
        """
        Set the font family to 'Quarto'
        """
        self.set_font_family('Quarto')
        return self

    def set_font_family_calibri(self) -> 'TextListFormatter':
        """
        Set the font family to 'Calibri'
        """
        self.set_font_family('Calibri')
        return self

    # endregion

    # region set alignment

    def set_ha(self, alignment: H_ALIGN) -> 'TextListFormatter':

        if alignment not in HORIZONTAL_ALIGNMENTS:
            raise ValueError(
                f'alignment must be one of {HORIZONTAL_ALIGNMENTS}'
            )
        for text in self._text_list:
            text.set_ha(alignment=alignment)
        return self

    def set_ha_left(self) -> 'TextListFormatter':

        return self.set_ha('left')

    def set_ha_center(self) -> 'TextListFormatter':

        return self.set_ha('center')

    def set_ha_right(self) -> 'TextListFormatter':

        return self.set_ha('right')

    def set_va(self, alignment: TEXT_V_ALIGN) -> 'TextListFormatter':

        if alignment not in VERTICAL_ALIGNMENTS:
            raise ValueError(
                f'alignment must be one of {VERTICAL_ALIGNMENTS}'
            )
        for text in self._text_list:
            text.set_va(alignment=alignment)
        return self

    def set_va_top(self) -> 'TextListFormatter':

        return self.set_va('top')

    def set_va_center(self) -> 'TextListFormatter':

        return self.set_va('center')

    def set_va_bottom(self) -> 'TextListFormatter':

        return self.set_va('bottom')

    def set_va_baseline(self) -> 'TextListFormatter':

        return self.set_va('baseline')

    def set_va_center_baseline(self) -> 'TextListFormatter':

        return self.set_va('center_baseline')

    # endregion

    @property
    def texts(self) -> List[str]:

        return[t.to_string() for t in self._text_list]
