'''_1975.py

CylindricalGearOptimizationStep
'''


from mastapy._internal import constructor
from mastapy.system_model.optimization import _1979
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_OPTIMIZATION_STEP = python_net_import('SMT.MastaAPI.SystemModel.Optimization', 'CylindricalGearOptimizationStep')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearOptimizationStep',)


class CylindricalGearOptimizationStep(_1979.OptimizationStep):
    '''CylindricalGearOptimizationStep

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_OPTIMIZATION_STEP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearOptimizationStep.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_advanced_ltca(self) -> 'bool':
        '''bool: 'UseAdvancedLTCA' is the original name of this property.'''

        return self.wrapped.UseAdvancedLTCA

    @use_advanced_ltca.setter
    def use_advanced_ltca(self, value: 'bool'):
        self.wrapped.UseAdvancedLTCA = bool(value) if value else False

    @property
    def include_extended_tip_contact(self) -> 'bool':
        '''bool: 'IncludeExtendedTipContact' is the original name of this property.'''

        return self.wrapped.IncludeExtendedTipContact

    @include_extended_tip_contact.setter
    def include_extended_tip_contact(self, value: 'bool'):
        self.wrapped.IncludeExtendedTipContact = bool(value) if value else False

    @property
    def include_tip_edge_stresses(self) -> 'bool':
        '''bool: 'IncludeTipEdgeStresses' is the original name of this property.'''

        return self.wrapped.IncludeTipEdgeStresses

    @include_tip_edge_stresses.setter
    def include_tip_edge_stresses(self, value: 'bool'):
        self.wrapped.IncludeTipEdgeStresses = bool(value) if value else False
