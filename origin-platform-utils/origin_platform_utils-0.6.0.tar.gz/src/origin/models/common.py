from enum import Enum
from serpyco import field
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Generic, TypeVar, List

from origin.serialize import Serializable


# -- Data objects ------------------------------------------------------------


class EnergyDirection(Enum):
    """
    TODO
    """
    production = 'production'  # E18
    consumption = 'consumption'  # E17


@dataclass
class Address(Serializable):
    """
    TODO Which international standard does this convey to?
    """
    street_code: Optional[str] = field(default=None)
    street_name: Optional[str] = field(default=None)
    building_number: Optional[str] = field(default=None)
    floor_id: Optional[str] = field(default=None)
    room_id: Optional[str] = field(default=None)
    post_code: Optional[str] = field(default=None)
    city_name: Optional[str] = field(default=None)
    city_sub_division_name: Optional[str] = field(default=None)
    municipality_code: Optional[str] = field(default=None)
    location_description: Optional[str] = field(default=None)

    def __str__(self) -> str:
        """
        Creates a string representation of the address.
        """
        return self.format()

    def format(self, separator: str = '\n') -> str:
        """
        Creates a string representation of the address.
        """
        return separator.join(self.parts)

    @property
    def parts(self) -> List[str]:
        """
        TODO
        """
        return []


# -- Value Ranges ------------------------------------------------------------


@dataclass
class DateRange(Serializable):
    """
    A range of dates.
    """
    from_: Optional[date] = field(default=None, dict_key='from')
    to_: Optional[date] = field(default=None, dict_key='to')


@dataclass
class DateTimeRange(Serializable):
    """
    A range of datetimes.
    """
    from_: Optional[datetime] = field(default=None, dict_key='from')
    to_: Optional[datetime] = field(default=None, dict_key='to')


# -- API & Querying ----------------------------------------------------------


TOrderKey = TypeVar('TOrderKey', bound=Enum)


class Order(Enum):
    """
    TODO
    """
    asc = 'asc'
    desc = 'desc'


@dataclass
class ResultOrdering(Serializable, Generic[TOrderKey]):
    """
    Ordering of query results.
    """
    key: Optional[TOrderKey] = field(default=None)
    order: Order = field(default=Order.asc)

    @property
    def asc(self) -> bool:
        return self.order is Order.asc

    @property
    def desc(self) -> bool:
        return self.order is Order.desc
