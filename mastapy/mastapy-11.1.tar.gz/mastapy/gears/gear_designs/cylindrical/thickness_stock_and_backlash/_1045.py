'''_1045.py

NoValueSpecification
'''


from typing import Generic, TypeVar

from mastapy.gears.gear_designs.cylindrical import _1037
from mastapy._internal.python_net import python_net_import

_NO_VALUE_SPECIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.ThicknessStockAndBacklash', 'NoValueSpecification')


__docformat__ = 'restructuredtext en'
__all__ = ('NoValueSpecification',)


T = TypeVar('T')


class NoValueSpecification(_1037.TolerancedValueSpecification['T'], Generic[T]):
    '''NoValueSpecification

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _NO_VALUE_SPECIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NoValueSpecification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
