from propsettings.setting_type import SettingType


class List(SettingType):

    def __init__(self, list_type: type, elements_setting_type: SettingType = None):
        self._type = list_type
        self._elements_setting_type = elements_setting_type

    @property
    def type(self):
        return self._type

    @property
    def elements_setting_type(self):
        return self._elements_setting_type

    def has_elements_setting_type(self):
        return self._elements_setting_type is not None
