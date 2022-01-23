"""
Nozomi
SQL Conforming Protocol Module
author: hugh@blinkybeach.com
"""
from nozomi.security.random_number import RandomNumber
from typing import Union


class _Placebo:
    pass


try:
    from psycopg2.extensions import ISQLQuote
    from psycopg2.extensions import QuotedString
except ImportError:
    ISQLQuote = _Placebo
    QuotedString = None


class SQLConforming(ISQLQuote):

    _QUOTE_LENGTH = 32

    sql_representation: bytes = NotImplemented

    def __conform__(self, protocol):
        if protocol == ISQLQuote:
            return self
        return

    def getquoted(self) -> bytes:
        return self.sql_representation

    def quote_string(self, string: str) -> bytes:
        """Return a quoted string"""
        if not QuotedString:
            raise NotImplementedError('Install Psycopg2')
        return QuotedString(string).getquoted()

    def dollar_quote_string(self, string: str) -> str:
        """Return a safely $$ quoted SQL string"""
        tag_valid = False
        while tag_valid is False:
            tag = self._generate_tag()
            if tag not in string:
                tag_valid = True
            continue
        return tag + string + tag

    def _generate_tag(self) -> str:
        """Return a"""
        return '$A' + RandomNumber(
            self._QUOTE_LENGTH
        ).dash_free_urlsafe_base64.replace('=', '') + '$'

    def adapt_bool(self, boolean_data: bool) -> bytes:
        assert isinstance(boolean_data, bool)
        if boolean_data is True:
            return 'true'.encode()
        return 'false'.encode()

    def adapt_integer(self, integer: int) -> bytes:
        assert isinstance(integer, int)
        return str(integer).encode()

    def adapt_string(self, string: str) -> bytes:
        return self.dollar_quote_string(string).encode()


BaseTypes = Union[str, int, list, dict, float]
AnySQLConforming = Union[SQLConforming, BaseTypes]
