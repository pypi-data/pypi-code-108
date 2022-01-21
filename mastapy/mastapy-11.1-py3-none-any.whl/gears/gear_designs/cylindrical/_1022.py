'''_1022.py

RelativeMeasurementViewModel
'''


from typing import Generic, TypeVar

from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RELATIVE_MEASUREMENT_VIEW_MODEL = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'RelativeMeasurementViewModel')


__docformat__ = 'restructuredtext en'
__all__ = ('RelativeMeasurementViewModel',)


T = TypeVar('T')


class RelativeMeasurementViewModel(_0.APIBase, Generic[T]):
    '''RelativeMeasurementViewModel

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _RELATIVE_MEASUREMENT_VIEW_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RelativeMeasurementViewModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
