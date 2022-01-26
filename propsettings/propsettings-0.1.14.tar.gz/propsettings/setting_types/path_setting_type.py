from propsettings.setting_type import SettingType


class Path(SettingType):

    def __init__(self, is_folder: bool, extensions: list):
        self._is_folder = is_folder
        self._extensions = extensions

    @property
    def is_folder(self):
        return self._is_folder

    @property
    def extensions(self):
        return self._extensions
