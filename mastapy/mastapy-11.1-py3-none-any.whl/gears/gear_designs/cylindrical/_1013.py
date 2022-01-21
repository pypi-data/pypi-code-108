'''_1013.py

LinearBacklashSepcification
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.cylindrical import _994, _991
from mastapy._internal.cast_exception import CastException
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_LINEAR_BACKLASH_SEPCIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'LinearBacklashSepcification')


__docformat__ = 'restructuredtext en'
__all__ = ('LinearBacklashSepcification',)


class LinearBacklashSepcification(_0.APIBase):
    '''LinearBacklashSepcification

    This is a mastapy class.
    '''

    TYPE = _LINEAR_BACKLASH_SEPCIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LinearBacklashSepcification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def flank_name(self) -> 'str':
        '''str: 'FlankName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FlankName

    @property
    def normal_backlash(self) -> '_994.CylindricalMeshLinearBacklashSpecification':
        '''CylindricalMeshLinearBacklashSpecification: 'NormalBacklash' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _994.CylindricalMeshLinearBacklashSpecification.TYPE not in self.wrapped.NormalBacklash.__class__.__mro__:
            raise CastException('Failed to cast normal_backlash to CylindricalMeshLinearBacklashSpecification. Expected: {}.'.format(self.wrapped.NormalBacklash.__class__.__qualname__))

        return constructor.new_override(self.wrapped.NormalBacklash.__class__)(self.wrapped.NormalBacklash) if self.wrapped.NormalBacklash is not None else None

    @property
    def circumferential_backlash_pitch_circle(self) -> '_994.CylindricalMeshLinearBacklashSpecification':
        '''CylindricalMeshLinearBacklashSpecification: 'CircumferentialBacklashPitchCircle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _994.CylindricalMeshLinearBacklashSpecification.TYPE not in self.wrapped.CircumferentialBacklashPitchCircle.__class__.__mro__:
            raise CastException('Failed to cast circumferential_backlash_pitch_circle to CylindricalMeshLinearBacklashSpecification. Expected: {}.'.format(self.wrapped.CircumferentialBacklashPitchCircle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CircumferentialBacklashPitchCircle.__class__)(self.wrapped.CircumferentialBacklashPitchCircle) if self.wrapped.CircumferentialBacklashPitchCircle is not None else None

    @property
    def circumferential_backlash_reference_circle(self) -> '_994.CylindricalMeshLinearBacklashSpecification':
        '''CylindricalMeshLinearBacklashSpecification: 'CircumferentialBacklashReferenceCircle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _994.CylindricalMeshLinearBacklashSpecification.TYPE not in self.wrapped.CircumferentialBacklashReferenceCircle.__class__.__mro__:
            raise CastException('Failed to cast circumferential_backlash_reference_circle to CylindricalMeshLinearBacklashSpecification. Expected: {}.'.format(self.wrapped.CircumferentialBacklashReferenceCircle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CircumferentialBacklashReferenceCircle.__class__)(self.wrapped.CircumferentialBacklashReferenceCircle) if self.wrapped.CircumferentialBacklashReferenceCircle is not None else None

    @property
    def radial_backlash(self) -> '_994.CylindricalMeshLinearBacklashSpecification':
        '''CylindricalMeshLinearBacklashSpecification: 'RadialBacklash' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _994.CylindricalMeshLinearBacklashSpecification.TYPE not in self.wrapped.RadialBacklash.__class__.__mro__:
            raise CastException('Failed to cast radial_backlash to CylindricalMeshLinearBacklashSpecification. Expected: {}.'.format(self.wrapped.RadialBacklash.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RadialBacklash.__class__)(self.wrapped.RadialBacklash) if self.wrapped.RadialBacklash is not None else None

    @property
    def linear_backlash(self) -> 'List[_994.CylindricalMeshLinearBacklashSpecification]':
        '''List[CylindricalMeshLinearBacklashSpecification]: 'LinearBacklash' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LinearBacklash, constructor.new(_994.CylindricalMeshLinearBacklashSpecification))
        return value
