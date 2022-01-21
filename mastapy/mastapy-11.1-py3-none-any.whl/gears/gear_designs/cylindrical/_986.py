'''_986.py

CylindricalGearSetMacroGeometryOptimiser
'''


from mastapy._internal import constructor
from mastapy.gears import _298
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_MACRO_GEOMETRY_OPTIMISER = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearSetMacroGeometryOptimiser')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetMacroGeometryOptimiser',)


class CylindricalGearSetMacroGeometryOptimiser(_298.GearSetOptimiser):
    '''CylindricalGearSetMacroGeometryOptimiser

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_MACRO_GEOMETRY_OPTIMISER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetMacroGeometryOptimiser.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def modify_basic_rack(self) -> 'bool':
        '''bool: 'ModifyBasicRack' is the original name of this property.'''

        return self.wrapped.ModifyBasicRack

    @modify_basic_rack.setter
    def modify_basic_rack(self, value: 'bool'):
        self.wrapped.ModifyBasicRack = bool(value) if value else False

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.'''

        return self.wrapped.FaceWidth

    @face_width.setter
    def face_width(self, value: 'float'):
        self.wrapped.FaceWidth = float(value) if value else 0.0

    @property
    def normal_module(self) -> 'float':
        '''float: 'NormalModule' is the original name of this property.'''

        return self.wrapped.NormalModule

    @normal_module.setter
    def normal_module(self, value: 'float'):
        self.wrapped.NormalModule = float(value) if value else 0.0

    @property
    def helix_angle(self) -> 'float':
        '''float: 'HelixAngle' is the original name of this property.'''

        return self.wrapped.HelixAngle

    @helix_angle.setter
    def helix_angle(self, value: 'float'):
        self.wrapped.HelixAngle = float(value) if value else 0.0

    @property
    def root_gear_profile_shift_coefficient(self) -> 'float':
        '''float: 'RootGearProfileShiftCoefficient' is the original name of this property.'''

        return self.wrapped.RootGearProfileShiftCoefficient

    @root_gear_profile_shift_coefficient.setter
    def root_gear_profile_shift_coefficient(self, value: 'float'):
        self.wrapped.RootGearProfileShiftCoefficient = float(value) if value else 0.0

    @property
    def root_gear_thickness_reduction(self) -> 'float':
        '''float: 'RootGearThicknessReduction' is the original name of this property.'''

        return self.wrapped.RootGearThicknessReduction

    @root_gear_thickness_reduction.setter
    def root_gear_thickness_reduction(self, value: 'float'):
        self.wrapped.RootGearThicknessReduction = float(value) if value else 0.0

    @property
    def normal_pressure_angle(self) -> 'float':
        '''float: 'NormalPressureAngle' is the original name of this property.'''

        return self.wrapped.NormalPressureAngle

    @normal_pressure_angle.setter
    def normal_pressure_angle(self, value: 'float'):
        self.wrapped.NormalPressureAngle = float(value) if value else 0.0

    @property
    def pressure_angle_input_is_active(self) -> 'bool':
        '''bool: 'PressureAngleInputIsActive' is the original name of this property.'''

        return self.wrapped.PressureAngleInputIsActive

    @pressure_angle_input_is_active.setter
    def pressure_angle_input_is_active(self, value: 'bool'):
        self.wrapped.PressureAngleInputIsActive = bool(value) if value else False

    @property
    def helix_angle_input_is_active(self) -> 'bool':
        '''bool: 'HelixAngleInputIsActive' is the original name of this property.'''

        return self.wrapped.HelixAngleInputIsActive

    @helix_angle_input_is_active.setter
    def helix_angle_input_is_active(self, value: 'bool'):
        self.wrapped.HelixAngleInputIsActive = bool(value) if value else False
