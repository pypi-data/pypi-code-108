'''_6575.py

CylindricalGearLoadCase
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.part_model.gears import _2265, _2267
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6576, _6605
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1052
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'CylindricalGearLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearLoadCase',)


class CylindricalGearLoadCase(_6605.GearLoadCase):
    '''CylindricalGearLoadCase

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def override_micro_geometry(self) -> 'bool':
        '''bool: 'OverrideMicroGeometry' is the original name of this property.'''

        return self.wrapped.OverrideMicroGeometry

    @override_micro_geometry.setter
    def override_micro_geometry(self, value: 'bool'):
        self.wrapped.OverrideMicroGeometry = bool(value) if value else False

    @property
    def speed(self) -> 'float':
        '''float: 'Speed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Speed

    @property
    def torque(self) -> 'float':
        '''float: 'Torque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Torque

    @property
    def power(self) -> 'float':
        '''float: 'Power' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Power

    @property
    def reversed_bending_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ReversedBendingFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ReversedBendingFactor) if self.wrapped.ReversedBendingFactor is not None else None

    @reversed_bending_factor.setter
    def reversed_bending_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ReversedBendingFactor = value

    @property
    def lateral_reaction_force(self) -> 'float':
        '''float: 'LateralReactionForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LateralReactionForce

    @property
    def vertical_reaction_force(self) -> 'float':
        '''float: 'VerticalReactionForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VerticalReactionForce

    @property
    def axial_reaction_force(self) -> 'float':
        '''float: 'AxialReactionForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialReactionForce

    @property
    def lateral_reaction_moment(self) -> 'float':
        '''float: 'LateralReactionMoment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LateralReactionMoment

    @property
    def vertical_reaction_moment(self) -> 'float':
        '''float: 'VerticalReactionMoment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VerticalReactionMoment

    @property
    def component_design(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2265.CylindricalGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CylindricalGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def gear_manufacture_errors(self) -> '_6576.CylindricalGearManufactureError':
        '''CylindricalGearManufactureError: 'GearManufactureErrors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6576.CylindricalGearManufactureError)(self.wrapped.GearManufactureErrors) if self.wrapped.GearManufactureErrors is not None else None

    @property
    def overridden_micro_geometry(self) -> '_1052.CylindricalGearMicroGeometry':
        '''CylindricalGearMicroGeometry: 'OverriddenMicroGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1052.CylindricalGearMicroGeometry)(self.wrapped.OverriddenMicroGeometry) if self.wrapped.OverriddenMicroGeometry is not None else None

    @property
    def planetaries(self) -> 'List[CylindricalGearLoadCase]':
        '''List[CylindricalGearLoadCase]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(CylindricalGearLoadCase))
        return value
