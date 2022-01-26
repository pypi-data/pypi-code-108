from typing import Union

from propsettings.setting_type import SettingType


class Range(SettingType):

    def __init__(self, mn: Union[int, float], mx: Union[int, float]):
        self._min = mn
        self._max = mx

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max
