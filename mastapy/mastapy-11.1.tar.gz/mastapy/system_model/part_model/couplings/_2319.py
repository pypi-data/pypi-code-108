'''_2319.py

ClutchHalf
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model.couplings import _2324
from mastapy._internal.python_net import python_net_import

_CLUTCH_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'ClutchHalf')


__docformat__ = 'restructuredtext en'
__all__ = ('ClutchHalf',)


class ClutchHalf(_2324.CouplingHalf):
    '''ClutchHalf

    This is a mastapy class.
    '''

    TYPE = _CLUTCH_HALF

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClutchHalf.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def is_mounted_on_shaft_outer(self) -> 'bool':
        '''bool: 'IsMountedOnShaftOuter' is the original name of this property.'''

        return self.wrapped.IsMountedOnShaftOuter

    @is_mounted_on_shaft_outer.setter
    def is_mounted_on_shaft_outer(self, value: 'bool'):
        self.wrapped.IsMountedOnShaftOuter = bool(value) if value else False

    @property
    def specify_clutch_half_dimensions(self) -> 'bool':
        '''bool: 'SpecifyClutchHalfDimensions' is the original name of this property.'''

        return self.wrapped.SpecifyClutchHalfDimensions

    @specify_clutch_half_dimensions.setter
    def specify_clutch_half_dimensions(self, value: 'bool'):
        self.wrapped.SpecifyClutchHalfDimensions = bool(value) if value else False
