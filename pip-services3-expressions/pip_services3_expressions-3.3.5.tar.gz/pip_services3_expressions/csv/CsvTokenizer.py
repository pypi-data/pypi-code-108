# -*- coding: utf-8 -*-
from typing import Union, List

from pip_services3_expressions.csv.CsvConstant import CsvConstant
from pip_services3_expressions.csv.CsvQuoteState import CsvQuoteState
from pip_services3_expressions.csv.CsvSymbolState import CsvSymbolState
from pip_services3_expressions.csv.CsvWordState import CsvWordState
from pip_services3_expressions.tokenizers.AbstractTokenizer import AbstractTokenizer
from pip_services3_expressions.tokenizers.ICommentState import ICommentState
from pip_services3_expressions.tokenizers.INumberState import INumberState
from pip_services3_expressions.tokenizers.IWhitespaceState import IWhitespaceState


class CsvTokenizer(AbstractTokenizer):
    """
    Implements a tokenizer class for CSV files.
    """

    def __init__(self):
        """
        Constructs this object with default parameters.
        """
        super(CsvTokenizer, self).__init__()

        self.__field_separators: List[int] = [ord(',')]
        self.__quote_symbols: List[int] = [ord('"')]
        self.__end_of_line: str = "\n\r"

        self.number_state: Union[INumberState, None] = None
        self.whitespace_state: Union[IWhitespaceState, None] = None
        self.comment_state: Union[ICommentState, None] = None
        self.word_state = CsvWordState(self.field_separators, self.quote_symbols)
        self.symbol_state = CsvSymbolState()
        self.quote_state = CsvQuoteState()
        self.__assign_states()

    @property
    def field_separators(self) -> List[int]:
        """
        Separator for fields in CSV stream.
        """
        return self.__field_separators

    @field_separators.setter
    def field_separators(self, value: List[int]):
        """
        Separator for fields in CSV stream.
        """
        if value is None:
            raise Exception('value')

        for field_separator in value:
            if field_separator in [CsvConstant.CR, CsvConstant.LF, CsvConstant.Nil]:
                raise Exception('Invalid field separator.')

            for quote_symbol in self.quote_symbols:
                if field_separator == quote_symbol:
                    raise Exception('Invalid field separator.')

        self.__field_separators = value
        self.word_state = CsvWordState(value, self.quote_symbols)
        self.__assign_states()

    @property
    def end_of_line(self) -> str:
        """
        Separator for rows in CSV stream.
        """
        return self.__end_of_line

    @end_of_line.setter
    def end_of_line(self, value: str):
        """
        Separator for rows in CSV stream.
        """
        self.__end_of_line = value

    @property
    def quote_symbols(self) -> List[int]:
        """
        Character to quote strings.
        """
        return self.__quote_symbols

    @quote_symbols.setter
    def quote_symbols(self, value: List[int]):
        """
        Character to quote strings.
        """
        if value is None:
            raise Exception('value')

        for quote_symbol in value:
            if quote_symbol in [CsvConstant.CR, CsvConstant.LF, CsvConstant.Nil]:
                raise Exception('Invalid quote symbol.')

            for filed_separator in self.field_separators:
                if quote_symbol == filed_separator:
                    raise Exception('Invalid quote symbol.')

        self.__quote_symbols = value
        self.word_state = CsvWordState(self.field_separators, value)
        self.__assign_states()

    def __assign_states(self):
        """
        Assigns tokenizer states to correct characters.
        """
        self.clear_character_states()
        self.set_character_state(0x0000, 0xfffe, self.word_state)
        self.set_character_state(CsvConstant.CR, CsvConstant.CR, self.symbol_state)
        self.set_character_state(CsvConstant.LF, CsvConstant.LF, self.symbol_state)

        for field_separator in self.field_separators:
            self.set_character_state(field_separator, field_separator, self.symbol_state)

        for quote_symbol in self.quote_symbols:
            self.set_character_state(quote_symbol, quote_symbol, self.quote_state)
