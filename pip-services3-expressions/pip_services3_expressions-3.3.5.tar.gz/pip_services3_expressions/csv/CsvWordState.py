# -*- coding: utf-8 -*-
from typing import List

from pip_services3_expressions.csv.CsvConstant import CsvConstant
from pip_services3_expressions.tokenizers.generic.GenericWordState import GenericWordState


class CsvWordState(GenericWordState):
    """
    Implements a word state to tokenize CSV stream.
    """

    def __init__(self, filed_separators: List[int], quote_symbols: List[int]):
        """
        Constructs this object with specified parameters.
        :param filed_separators: Separators for fields in CSV stream.
        :param quote_symbols: Delimiters character to quote strings.
        """
        super(CsvWordState, self).__init__()

        self.clear_word_chars()
        self.set_word_chars(0x0000, 0xfffe, True)

        self.set_word_chars(CsvConstant.CR, CsvConstant.CR, False)
        self.set_word_chars(CsvConstant.LF, CsvConstant.LF, False)

        for field_separator in filed_separators:
            self.set_word_chars(field_separator, field_separator, False)

        for quote_symbol in quote_symbols:
            self.set_word_chars(quote_symbol, quote_symbol, False)
