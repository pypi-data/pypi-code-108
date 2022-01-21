'''_1478.py

PressurePerUnitTime
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_PRESSURE_PER_UNIT_TIME = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'PressurePerUnitTime')


__docformat__ = 'restructuredtext en'
__all__ = ('PressurePerUnitTime',)


class PressurePerUnitTime(_1398.MeasurementBase):
    '''PressurePerUnitTime

    This is a mastapy class.
    '''

    TYPE = _PRESSURE_PER_UNIT_TIME

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PressurePerUnitTime.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
