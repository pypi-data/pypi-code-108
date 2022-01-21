'''_1886.py

AsymmetricSphericalRollerBearing
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.bearings.bearing_designs.rolling import _1909
from mastapy._internal.python_net import python_net_import

_ASYMMETRIC_SPHERICAL_ROLLER_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'AsymmetricSphericalRollerBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('AsymmetricSphericalRollerBearing',)


class AsymmetricSphericalRollerBearing(_1909.RollerBearing):
    '''AsymmetricSphericalRollerBearing

    This is a mastapy class.
    '''

    TYPE = _ASYMMETRIC_SPHERICAL_ROLLER_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AsymmetricSphericalRollerBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def major_diameter_offset_from_roller_centre(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MajorDiameterOffsetFromRollerCentre' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MajorDiameterOffsetFromRollerCentre) if self.wrapped.MajorDiameterOffsetFromRollerCentre is not None else None

    @major_diameter_offset_from_roller_centre.setter
    def major_diameter_offset_from_roller_centre(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MajorDiameterOffsetFromRollerCentre = value

    @property
    def element_profile_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ElementProfileRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ElementProfileRadius) if self.wrapped.ElementProfileRadius is not None else None

    @element_profile_radius.setter
    def element_profile_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ElementProfileRadius = value

    @property
    def outer_race_groove_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterRaceGrooveRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterRaceGrooveRadius) if self.wrapped.OuterRaceGrooveRadius is not None else None

    @outer_race_groove_radius.setter
    def outer_race_groove_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterRaceGrooveRadius = value

    @property
    def inner_race_groove_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerRaceGrooveRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerRaceGrooveRadius) if self.wrapped.InnerRaceGrooveRadius is not None else None

    @inner_race_groove_radius.setter
    def inner_race_groove_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerRaceGrooveRadius = value

    @property
    def inner_rib_chamfer(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerRibChamfer' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerRibChamfer) if self.wrapped.InnerRibChamfer is not None else None

    @inner_rib_chamfer.setter
    def inner_rib_chamfer(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerRibChamfer = value

    @property
    def inner_rib_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerRibDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerRibDiameter) if self.wrapped.InnerRibDiameter is not None else None

    @inner_rib_diameter.setter
    def inner_rib_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerRibDiameter = value
