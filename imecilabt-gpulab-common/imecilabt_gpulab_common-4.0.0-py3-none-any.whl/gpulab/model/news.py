import datetime
import json
import re
from dataclasses import dataclass, field

# import dataclasses_json
import dateutil.parser

from typing import Optional, List, Union

from stringcase import camelcase

from dataclass_dict_convert import dataclass_dict_convert, dataclass_auto_type_check


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass_auto_type_check
@dataclass(frozen=True)
class News:
    id: str
    created: datetime.datetime
    enabled: bool
    type: str
    title: str
    text: str
    tags: List[str]
    not_before: Optional[datetime.datetime] = field(default=None)
    not_after: Optional[datetime.datetime] = field(default=None)

    def __post_init__(self):
        assert self.created.tzinfo is not None, 'created ({}) is a naive datetime'.format(self.created)
        assert self.not_before is None or self.not_before.tzinfo is not None, \
            'not_before ({}) is a naive datetime'.format(self.not_before)
        assert self.not_after is None or self.not_after.tzinfo is not None, \
            'not_after ({}) is a naive datetime'.format(self.not_after)

    def make_copy(self) -> 'News':
      return News.from_dict(self.to_dict())

# Example:
# {
#     "id": "9a6355d0-6d06-11ea-a8da-7b5b9b861935",
#     "created": "2020-03-30T06:38:34Z",
#     "enabled": true,  //messages can be disabled without deleting them
#     "type": "WARNING",  //INFO (new hardware, ...), WARNING (maintenance announcement, ...) or CRITICAL (currently down, ...)
#     "title": "Planned Maintenance Friday Morning",
#     "text": "There will be a maintenance friday morning. Jobs will keep running, but the website and CLI might be temporarily offline.",
#     "notBefore": "2020-03-24T06:38:34Z",
#     "notAfter": "2020-03-30T06:38:34Z",
#     "tags": [ "MAINTENANCE", "WEBSITE", "CLI" ]  //flexible systems of tags that can be used to determine where and how to show the messages. (Not fixed yet, will be determined by used how this is used.)
#  }
