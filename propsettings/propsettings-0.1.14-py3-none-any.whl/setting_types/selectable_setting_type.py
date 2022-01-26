from typing import Tuple, List, Callable, Optional

from propsettings.setting_type import SettingType


class Selectable(SettingType):

    def __init__(self, options: List[Tuple[str, object]],
                 selected_callback: Optional[Callable[[object, str, object], None]] = None):
        self._options = options
        self._selected_callback = selected_callback

    @property
    def options(self):
        return self._options

    def call_selected_callback(self, instance: object, option_name: str, option_data: object):
        if self._selected_callback is not None:
            self._selected_callback(instance, option_name, option_data)
