'''_985.py

CylindricalGearSetFlankDesign
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_FLANK_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearSetFlankDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetFlankDesign',)


class CylindricalGearSetFlankDesign(_0.APIBase):
    '''CylindricalGearSetFlankDesign

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_FLANK_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetFlankDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def base_helix_angle(self) -> 'float':
        '''float: 'BaseHelixAngle' is the original name of this property.'''

        return self.wrapped.BaseHelixAngle

    @base_helix_angle.setter
    def base_helix_angle(self, value: 'float'):
        self.wrapped.BaseHelixAngle = float(value) if value else 0.0

    @property
    def normal_pressure_angle(self) -> 'float':
        '''float: 'NormalPressureAngle' is the original name of this property.'''

        return self.wrapped.NormalPressureAngle

    @normal_pressure_angle.setter
    def normal_pressure_angle(self, value: 'float'):
        self.wrapped.NormalPressureAngle = float(value) if value else 0.0

    @property
    def normal_base_pitch(self) -> 'float':
        '''float: 'NormalBasePitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalBasePitch

    @property
    def normal_base_pitch_set_by_changing_normal_module(self) -> 'float':
        '''float: 'NormalBasePitchSetByChangingNormalModule' is the original name of this property.'''

        return self.wrapped.NormalBasePitchSetByChangingNormalModule

    @normal_base_pitch_set_by_changing_normal_module.setter
    def normal_base_pitch_set_by_changing_normal_module(self, value: 'float'):
        self.wrapped.NormalBasePitchSetByChangingNormalModule = float(value) if value else 0.0

    @property
    def normal_base_pitch_set_by_changing_normal_pressure_angle(self) -> 'float':
        '''float: 'NormalBasePitchSetByChangingNormalPressureAngle' is the original name of this property.'''

        return self.wrapped.NormalBasePitchSetByChangingNormalPressureAngle

    @normal_base_pitch_set_by_changing_normal_pressure_angle.setter
    def normal_base_pitch_set_by_changing_normal_pressure_angle(self, value: 'float'):
        self.wrapped.NormalBasePitchSetByChangingNormalPressureAngle = float(value) if value else 0.0

    @property
    def transverse_base_pitch(self) -> 'float':
        '''float: 'TransverseBasePitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseBasePitch

    @property
    def transverse_pressure_angle(self) -> 'float':
        '''float: 'TransversePressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransversePressureAngle

    @property
    def transverse_pressure_angle_normal_pressure_angle(self) -> 'float':
        '''float: 'TransversePressureAngleNormalPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransversePressureAngleNormalPressureAngle

    @property
    def minimum_transverse_contact_ratio(self) -> 'float':
        '''float: 'MinimumTransverseContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumTransverseContactRatio

    @property
    def minimum_total_contact_ratio(self) -> 'float':
        '''float: 'MinimumTotalContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumTotalContactRatio

    @property
    def flank_name(self) -> 'str':
        '''str: 'FlankName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FlankName
