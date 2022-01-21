'''_1401.py

SafetyFactorUnit
'''


from mastapy.utility.units_and_measurements import _1403
from mastapy._internal.python_net import python_net_import

_SAFETY_FACTOR_UNIT = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements', 'SafetyFactorUnit')


__docformat__ = 'restructuredtext en'
__all__ = ('SafetyFactorUnit',)


class SafetyFactorUnit(_1403.Unit):
    '''SafetyFactorUnit

    This is a mastapy class.
    '''

    TYPE = _SAFETY_FACTOR_UNIT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SafetyFactorUnit.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
