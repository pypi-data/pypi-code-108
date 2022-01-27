"""Module containing the attributes for gtunrealdevice."""

from pathlib import Path
from pathlib import PurePath
from datetime import datetime

__version__ = '0.0.2'
version = __version__
__edition__ = 'Community'
edition = __edition__

__all__ = [
    'version',
    'edition'
]


class Data:
    # app yaml files
    devices_info_filename = str(
        PurePath(
            Path.home(),
            '.geekstrident',
            'gtunrealdevice',
            'devices_info.yaml'
        )
    )

    @classmethod
    def is_devices_info_file_exist(cls):
        fn = cls.devices_info_filename
        file_obj = Path(fn)
        return file_obj.exists()

    @classmethod
    def create_devices_info_file(cls):
        if cls.is_devices_info_file_exist():
            return True

        fn = cls.devices_info_filename
        file_obj = Path(fn)
        if not file_obj.parent.exists():
            file_obj.parent.mkdir(parents=True, exist_ok=True)
        file_obj.touch()
        fmt = '{:%Y-%m-%d %H:%M:%S.%f} - {} file is created.'
        print(fmt.format(datetime.now(), fn))
        return True
