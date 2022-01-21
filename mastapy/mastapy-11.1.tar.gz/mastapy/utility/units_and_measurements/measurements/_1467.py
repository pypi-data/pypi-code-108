'''_1467.py

MomentPerUnitPressure
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_MOMENT_PER_UNIT_PRESSURE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'MomentPerUnitPressure')


__docformat__ = 'restructuredtext en'
__all__ = ('MomentPerUnitPressure',)


class MomentPerUnitPressure(_1398.MeasurementBase):
    '''MomentPerUnitPressure

    This is a mastapy class.
    '''

    TYPE = _MOMENT_PER_UNIT_PRESSURE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MomentPerUnitPressure.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
