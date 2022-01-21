'''_1404.py

UnitGradient
'''


from mastapy.utility.units_and_measurements import _1403
from mastapy._internal.python_net import python_net_import

_UNIT_GRADIENT = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements', 'UnitGradient')


__docformat__ = 'restructuredtext en'
__all__ = ('UnitGradient',)


class UnitGradient(_1403.Unit):
    '''UnitGradient

    This is a mastapy class.
    '''

    TYPE = _UNIT_GRADIENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UnitGradient.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
