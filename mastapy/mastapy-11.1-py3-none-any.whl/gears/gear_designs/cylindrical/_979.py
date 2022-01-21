'''_979.py

CylindricalGearPinionTypeCutter
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.gear_designs.cylindrical import _980, _963
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_PINION_TYPE_CUTTER = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearPinionTypeCutter')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearPinionTypeCutter',)


class CylindricalGearPinionTypeCutter(_963.CylindricalGearAbstractRack):
    '''CylindricalGearPinionTypeCutter

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_PINION_TYPE_CUTTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearPinionTypeCutter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_teeth(self) -> 'int':
        '''int: 'NumberOfTeeth' is the original name of this property.'''

        return self.wrapped.NumberOfTeeth

    @number_of_teeth.setter
    def number_of_teeth(self, value: 'int'):
        self.wrapped.NumberOfTeeth = int(value) if value else 0

    @property
    def nominal_addendum_factor(self) -> 'float':
        '''float: 'NominalAddendumFactor' is the original name of this property.'''

        return self.wrapped.NominalAddendumFactor

    @nominal_addendum_factor.setter
    def nominal_addendum_factor(self, value: 'float'):
        self.wrapped.NominalAddendumFactor = float(value) if value else 0.0

    @property
    def nominal_dedendum_factor(self) -> 'float':
        '''float: 'NominalDedendumFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalDedendumFactor

    @property
    def profile_shift_coefficient(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ProfileShiftCoefficient' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ProfileShiftCoefficient) if self.wrapped.ProfileShiftCoefficient is not None else None

    @profile_shift_coefficient.setter
    def profile_shift_coefficient(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ProfileShiftCoefficient = value

    @property
    def left_flank(self) -> '_980.CylindricalGearPinionTypeCutterFlank':
        '''CylindricalGearPinionTypeCutterFlank: 'LeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_980.CylindricalGearPinionTypeCutterFlank)(self.wrapped.LeftFlank) if self.wrapped.LeftFlank is not None else None

    @property
    def right_flank(self) -> '_980.CylindricalGearPinionTypeCutterFlank':
        '''CylindricalGearPinionTypeCutterFlank: 'RightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_980.CylindricalGearPinionTypeCutterFlank)(self.wrapped.RightFlank) if self.wrapped.RightFlank is not None else None
