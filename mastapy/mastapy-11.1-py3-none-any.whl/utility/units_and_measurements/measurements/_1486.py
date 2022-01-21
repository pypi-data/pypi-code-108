'''_1486.py

SafetyFactor
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_SAFETY_FACTOR = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'SafetyFactor')


__docformat__ = 'restructuredtext en'
__all__ = ('SafetyFactor',)


class SafetyFactor(_1398.MeasurementBase):
    '''SafetyFactor

    This is a mastapy class.
    '''

    TYPE = _SAFETY_FACTOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SafetyFactor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
