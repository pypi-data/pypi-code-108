'''_1476.py

PowerSmallPerUnitTime
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_POWER_SMALL_PER_UNIT_TIME = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'PowerSmallPerUnitTime')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerSmallPerUnitTime',)


class PowerSmallPerUnitTime(_1398.MeasurementBase):
    '''PowerSmallPerUnitTime

    This is a mastapy class.
    '''

    TYPE = _POWER_SMALL_PER_UNIT_TIME

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerSmallPerUnitTime.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
