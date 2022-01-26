"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import sys
import platform
from typing import Any, Callable, Optional
from pathlib import Path
from datetime import datetime, timezone
from functools import cached_property

# * Third Party Imports --------------------------------------------------------------------------------->
import attr
from yarl import URL
from tzlocal import get_localzone, reload_localzone

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.utility.enums import OperatingSystem
from gidapptools.utility.helper import utc_now, make_pretty, memory_in_use
from gidapptools.utility._debug_tools import dprint
from gidapptools.general_helper.general import is_frozen
from gidapptools.general_helper.date_time import DatetimeFmt
from gidapptools.general_helper.conversion import bytes2human
from gidapptools.general_helper.string_helper import StringCase, StringCaseConverter
from gidapptools.abstract_classes.abstract_meta_item import AbstractMetaItem

reload_localzone()
print = dprint

# endregion[Imports]

# region [TODO]

# - Make into a class

# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]

def url_converter(in_url: str) -> Optional[URL]:
    if in_url is None:
        return in_url
    return URL(in_url)


@attr.s(auto_attribs=True, auto_detect=True, kw_only=True, frozen=True)
class MetaInfo(AbstractMetaItem):
    app_name: str = attr.ib(default=None)
    app_author: str = attr.ib(default=None)
    version: str = attr.ib(default=None)
    url: URL = attr.ib(converter=url_converter, default=None)
    pid: int = attr.ib(factory=os.getpid)
    os: OperatingSystem = attr.ib(factory=OperatingSystem.determine_operating_system)
    os_release: str = attr.ib(factory=platform.release)
    python_version: str = attr.ib(factory=platform.python_version)
    started_at: datetime = attr.ib(factory=utc_now)
    base_mem_use: int = attr.ib(default=memory_in_use())
    is_dev: bool = attr.ib(default=None, converter=attr.converters.default_if_none(False))
    is_gui: bool = attr.ib(default=None, converter=attr.converters.default_if_none(False))
    local_tz: timezone = attr.ib(default=get_localzone())

    @cached_property
    def is_frozen(self) -> bool:
        return is_frozen()

    @cached_property
    def frozen_folder_path(self) -> Optional[Path]:
        if self.is_frozen is True:
            return Path(sys._MEIPASS)

    @classmethod
    @property
    def __default_configuration__(cls) -> dict[str, Any]:
        default_configuration = {}
        return default_configuration

    @property
    def pretty_is_dev(self) -> str:
        return "Yes" if self.is_dev else "No"

    @property
    def pretty_app_name(self) -> str:
        return StringCaseConverter.convert_to(self.app_name, StringCase.TITLE)

    @property
    def pretty_app_author(self) -> str:
        return StringCaseConverter.convert_to(self.app_author, StringCase.TITLE)

    @property
    def pretty_base_mem_use(self) -> str:
        return bytes2human(self.base_mem_use)

    @property
    def pretty_started_at(self) -> str:
        return DatetimeFmt.STANDARD.strf(self.started_at)

    def as_dict(self, pretty: bool = False) -> dict[str, Any]:

        if pretty is True:
            return make_pretty(self)
        return attr.asdict(self)

    def to_storager(self, storager: Callable = None) -> None:
        if storager is None:
            return
        storager(self)

    def clean_up(self, **kwargs) -> None:
        pass


    # region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
