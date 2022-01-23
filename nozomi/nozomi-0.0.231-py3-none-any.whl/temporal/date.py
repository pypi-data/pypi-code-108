"""
Nozomi
Date Module
author: hugh@blinkybeach.com
"""
from nozomi.errors.bad_request import BadRequest
from nozomi.data.codable import Codable
from typing import TypeVar, Type, Any
from datetime import datetime

T = TypeVar('T', bound='NozomiDate')


class NozomiDate(datetime, Codable):

    _DB_FORMAT_STRING = "%Y-%m-%d"
    _REQUEST_FORMAT_STRING = "%Y-%m-%d"
    _REQUEST_FORMAT_STRING_B = "%Y/%m/%d"
    _REQUEST_FORMAT_STRING_C = "%d/%m/%Y"
    _REQUEST_FORMAT_STRING_D = "%d-%m-%Y"

    @classmethod
    def decode(cls: Type[T], data: Any) -> T:

        assert isinstance(data, str)
        data = data.split('T')[0]
        date = cls.strptime(data, cls._DB_FORMAT_STRING)
        return cls(
            year=date.year,
            month=date.month,
            day=date.day
        )

    def encode(self) -> str:
        return self.strftime(self._REQUEST_FORMAT_STRING)

    @classmethod
    def today(cls: Type[T]) -> T:
        return cls.create_now()

    @classmethod
    def create_now(cls: Type[T]) -> T:
        """Return the current date, at UTC"""
        date = datetime.utcnow()
        return NozomiDate(
            year=date.year,
            month=date.month,
            day=date.day
        )

    @classmethod
    def strptime(
        cls: Type[T],
        date_string: str,
        format_string: str
    ) -> T:

        super_datetime = datetime.strptime(date_string, format_string)
        return NozomiDate(
            year=super_datetime.year,
            month=super_datetime.month,
            day=super_datetime.day
        )

    @classmethod
    def parse_from_request(cls: Type[T], data: Any) -> T:
        if not isinstance(data, str):
            raise BadRequest('Date must be a string')
        try:
            date = cls.strptime(data, cls._REQUEST_FORMAT_STRING)
            return cls(
                year=date.year,
                month=date.month,
                day=date.day
            )
        except Exception:
            pass  # Give another format a go
        try:
            date = cls.strptime(data, cls._REQUEST_FORMAT_STRING_B)
            return cls(
                year=date.year,
                month=date.month,
                day=date.day
            )
        except Exception:
            pass  # Give another format a go
        try:
            date = cls.strptime(data, cls._REQUEST_FORMAT_STRING_C)
            return cls(
                year=date.year,
                month=date.month,
                day=date.day
            )
        except Exception:
            pass  # Give another format a go
        try:
            date = cls.strptime(data, cls._REQUEST_FORMAT_STRING_D)
            return cls(
                year=date.year,
                month=date.month,
                day=date.day
            )
        except Exception:
            raise BadRequest(
                'Date format unrecognised, expected {fmt}'.format(
                    fmt=cls._REQUEST_FORMAT_STRING
                )
            )
