'''_1023.py

RelativeValuesSpecification
'''


from typing import Generic, TypeVar

from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RELATIVE_VALUES_SPECIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'RelativeValuesSpecification')


__docformat__ = 'restructuredtext en'
__all__ = ('RelativeValuesSpecification',)


T = TypeVar('T', bound='RelativeValuesSpecification')


class RelativeValuesSpecification(_0.APIBase, Generic[T]):
    '''RelativeValuesSpecification

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _RELATIVE_VALUES_SPECIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RelativeValuesSpecification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
