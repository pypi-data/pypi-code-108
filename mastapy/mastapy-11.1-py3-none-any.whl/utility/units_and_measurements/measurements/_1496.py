'''_1496.py

ThermalContactCoefficient
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_THERMAL_CONTACT_COEFFICIENT = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'ThermalContactCoefficient')


__docformat__ = 'restructuredtext en'
__all__ = ('ThermalContactCoefficient',)


class ThermalContactCoefficient(_1398.MeasurementBase):
    '''ThermalContactCoefficient

    This is a mastapy class.
    '''

    TYPE = _THERMAL_CONTACT_COEFFICIENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ThermalContactCoefficient.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
