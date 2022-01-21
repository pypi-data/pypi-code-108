'''_1901.py

FourPointContactBallBearing
'''


from mastapy.bearings.bearing_designs.rolling import _1900, _1906
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal.python_net import python_net_import

_FOUR_POINT_CONTACT_BALL_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'FourPointContactBallBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('FourPointContactBallBearing',)


class FourPointContactBallBearing(_1906.MultiPointContactBallBearing):
    '''FourPointContactBallBearing

    This is a mastapy class.
    '''

    TYPE = _FOUR_POINT_CONTACT_BALL_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FourPointContactBallBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def contact_angle_and_internal_clearance_definition(self) -> '_1900.FourPointContactAngleDefinition':
        '''FourPointContactAngleDefinition: 'ContactAngleAndInternalClearanceDefinition' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ContactAngleAndInternalClearanceDefinition)
        return constructor.new(_1900.FourPointContactAngleDefinition)(value) if value is not None else None

    @contact_angle_and_internal_clearance_definition.setter
    def contact_angle_and_internal_clearance_definition(self, value: '_1900.FourPointContactAngleDefinition'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ContactAngleAndInternalClearanceDefinition = value

    @property
    def contact_angle_under_radial_load(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ContactAngleUnderRadialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ContactAngleUnderRadialLoad) if self.wrapped.ContactAngleUnderRadialLoad is not None else None

    @property
    def contact_angle_under_axial_load(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ContactAngleUnderAxialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ContactAngleUnderAxialLoad) if self.wrapped.ContactAngleUnderAxialLoad is not None else None

    @property
    def nominal_radial_internal_clearance(self) -> 'float':
        '''float: 'NominalRadialInternalClearance' is the original name of this property.'''

        return self.wrapped.NominalRadialInternalClearance

    @nominal_radial_internal_clearance.setter
    def nominal_radial_internal_clearance(self, value: 'float'):
        self.wrapped.NominalRadialInternalClearance = float(value) if value else 0.0

    @property
    def assembly_axial_internal_clearance(self) -> 'float':
        '''float: 'AssemblyAxialInternalClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AssemblyAxialInternalClearance
