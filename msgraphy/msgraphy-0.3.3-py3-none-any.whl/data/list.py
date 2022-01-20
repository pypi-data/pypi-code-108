import typing
from msgraphy.data import graphdataclass
from msgraphy.data.file import BaseItem


@graphdataclass
class List(BaseItem):
    display_name: str = None
    list_info: dict = None
    system: dict = None
    fields: typing.List = None


@graphdataclass
class ListColumn:
    id: str
    column_group: str
    description: str
    display_name: str
    enforce_unique_values: bool
    hidden: bool
    indexed: bool
    name: str
    read_only: bool
    required: bool
    lookup: dict = None
    person_or_group = None
    text = None
    date_time = None
    number = None