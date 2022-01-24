#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""LabJack device utilities."""
from __future__ import annotations

import logging
import warnings
from typing import Dict, Iterable, List, Union

from aenum import EnumMeta
from labjack.ljm import constants

from ..utils.enum import AutoNumberNameEnum, NameEnum

logger = logging.getLogger(__name__)


class TSeriesDIOChannel(NameEnum, init="address"):  # type:ignore
    """
    Digital Input/Output (DIO) addresses for various LabJack devices from T-Series.

    NOTE: not all DIO addresses are available on all devices. This is defined as
    `dio` attribute of `LabJackDeviceType`.
    """
    FIO0 = 0
    FIO1 = 1
    FIO2 = 2
    FIO3 = 3
    FIO4 = 4
    FIO5 = 5
    FIO6 = 6
    FIO7 = 7
    EIO0 = 8
    EIO1 = 9
    EIO2 = 10
    EIO3 = 11
    EIO4 = 12
    EIO5 = 13
    EIO6 = 14
    EIO7 = 15
    CIO0 = 16
    CIO1 = 17
    CIO2 = 18
    CIO3 = 19
    MIO0 = 20
    MIO1 = 21
    MIO2 = 22


def _build_p_id_lookup_dict(
    lab_jack_device_types: Iterable["DeviceType"],
) -> Dict[int, List]:
    """
    Build lookup dictionary of `DeviceType` instances based on their `p_id`. Note:
    `p_id` is not unique for each device type.

    :param lab_jack_device_types: `DeviceType` instances to iterate over
    :return: `int`-based lookup dictionary
    """
    ret: Dict[int, List] = dict()
    for lab_jack_device_type in lab_jack_device_types:
        if lab_jack_device_type.p_id not in ret:
            ret[lab_jack_device_type.p_id] = list()
        ret[lab_jack_device_type.p_id].append(lab_jack_device_type)
    return ret


# NOTE: super metaclass has to match metaclass of `super(DeviceType)`!
class DeviceTypeMeta(EnumMeta):
    def __new__(metacls, clsname, bases, clsdict, **kwargs):
        cls = EnumMeta.__new__(metacls, clsname, bases, clsdict, **kwargs)
        cls._get_by_p_id = _build_p_id_lookup_dict(cls)
        return cls


class AmbiguousProductIdWarning(UserWarning):
    pass


class DeviceType(AutoNumberNameEnum,
                 metaclass=DeviceTypeMeta,
                 init="value p_id type_str ain_max_resolution dio pulse_out_addr"
                 ):
    """
    LabJack device types.

    Can be also looked up by ambigious Product ID (`p_id`) or by instance name:
    ```python
    LabJackDeviceType(4) is LabJackDeviceType('T4')
    ```
    """

    ANY = (), constants.dtANY, "ANY", 0, (), ()
    T4 = (), constants.dtT4, "T4", 4, (
        TSeriesDIOChannel.FIO4,
        TSeriesDIOChannel.FIO5,
        TSeriesDIOChannel.FIO6,
        TSeriesDIOChannel.FIO7,
        TSeriesDIOChannel.EIO0,
        TSeriesDIOChannel.EIO1,
        TSeriesDIOChannel.EIO2,
        TSeriesDIOChannel.EIO3,
        TSeriesDIOChannel.EIO4,
        TSeriesDIOChannel.EIO5,
        TSeriesDIOChannel.EIO6,
        TSeriesDIOChannel.EIO7,
        TSeriesDIOChannel.CIO0,
        TSeriesDIOChannel.CIO1,
        TSeriesDIOChannel.CIO2,
        TSeriesDIOChannel.CIO3,
    ), (
        TSeriesDIOChannel.FIO6,
        TSeriesDIOChannel.FIO7,
    )

    T7 = (), constants.dtT7, "T7", 8, (
        TSeriesDIOChannel.FIO0,
        TSeriesDIOChannel.FIO1,
        TSeriesDIOChannel.FIO2,
        TSeriesDIOChannel.FIO3,
        TSeriesDIOChannel.FIO4,
        TSeriesDIOChannel.FIO5,
        TSeriesDIOChannel.FIO6,
        TSeriesDIOChannel.FIO7,
        TSeriesDIOChannel.EIO0,
        TSeriesDIOChannel.EIO1,
        TSeriesDIOChannel.EIO2,
        TSeriesDIOChannel.EIO3,
        TSeriesDIOChannel.EIO4,
        TSeriesDIOChannel.EIO5,
        TSeriesDIOChannel.EIO6,
        TSeriesDIOChannel.EIO7,
        TSeriesDIOChannel.CIO0,
        TSeriesDIOChannel.CIO1,
        TSeriesDIOChannel.CIO2,
        TSeriesDIOChannel.CIO3,
        TSeriesDIOChannel.MIO0,
        TSeriesDIOChannel.MIO1,
        TSeriesDIOChannel.MIO2,
    ), (
        TSeriesDIOChannel.FIO0,
        TSeriesDIOChannel.FIO2,
        TSeriesDIOChannel.FIO3,
        TSeriesDIOChannel.FIO4,
        TSeriesDIOChannel.FIO5,
    )

    T7_PRO = (), constants.dtT7, "T7", 12, (
        TSeriesDIOChannel.FIO0,
        TSeriesDIOChannel.FIO1,
        TSeriesDIOChannel.FIO2,
        TSeriesDIOChannel.FIO3,
        TSeriesDIOChannel.FIO4,
        TSeriesDIOChannel.FIO5,
        TSeriesDIOChannel.FIO6,
        TSeriesDIOChannel.FIO7,
        TSeriesDIOChannel.EIO0,
        TSeriesDIOChannel.EIO1,
        TSeriesDIOChannel.EIO2,
        TSeriesDIOChannel.EIO3,
        TSeriesDIOChannel.EIO4,
        TSeriesDIOChannel.EIO5,
        TSeriesDIOChannel.EIO6,
        TSeriesDIOChannel.EIO7,
        TSeriesDIOChannel.CIO0,
        TSeriesDIOChannel.CIO1,
        TSeriesDIOChannel.CIO2,
        TSeriesDIOChannel.CIO3,
        TSeriesDIOChannel.MIO0,
        TSeriesDIOChannel.MIO1,
        TSeriesDIOChannel.MIO2,
    ), (
        TSeriesDIOChannel.FIO0,
        TSeriesDIOChannel.FIO2,
        TSeriesDIOChannel.FIO3,
        TSeriesDIOChannel.FIO4,
        TSeriesDIOChannel.FIO5,
    )
    # DIGIT = (), constants.dtDIGIT, 'DIGIT', 0, ()
    # SERIES = (), constants.dtTSERIES, 'SERIES', 0, ()

    @classmethod
    def get_by_p_id(cls, p_id: int) -> Union[DeviceType, List[DeviceType]]:
        """
        Get LabJack device type instance via LabJack product ID.

        Note: Product ID is not unambiguous for LabJack devices.

        :param p_id: Product ID of a LabJack device
        :return: Instance or list of instances of `LabJackDeviceType`
        :raises ValueError: when Product ID is unknown
        """
        instances_list = cls._get_by_p_id.get(p_id)
        if instances_list is None:
            raise ValueError(f"Unknown LabJack Product ID: {p_id}")
        if len(instances_list) > 1:
            warnings.warn(
                f"Product ID {p_id} matches multiple device types: "
                f"{', '.join(instance.name for instance in instances_list)}.",
                AmbiguousProductIdWarning,
            )
            ret = instances_list
        else:
            ret = instances_list[0]
        return ret
