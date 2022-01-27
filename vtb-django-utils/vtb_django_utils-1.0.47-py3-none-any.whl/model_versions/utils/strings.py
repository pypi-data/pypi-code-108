from typing import Union

from django.contrib.postgres.fields import ArrayField

from .consts import VERSION_DELIMITER


def str_to_int_arr(version: str):
    return list(map(int, version.split(VERSION_DELIMITER)))


def int_arr_to_str(version_arr: Union[list, tuple, ArrayField]):
    return VERSION_DELIMITER.join(map(str, version_arr))


def is_last_version_less(last_version: str, new_version: str) -> bool:
    """ Сравнивает две версии в виде строк по значению """
    if last_version:
        last_version_parts = str_to_int_arr(last_version)
        new_version_parts = str_to_int_arr(new_version)
        for last, new in zip(last_version_parts, new_version_parts):
            if int(last) < int(new):
                return True
    return False
