'''_614.py

RealPlungeShaverOutputs
'''


from typing import List

from mastapy.gears.manufacturing.cylindrical.plunge_shaving import _605, _611
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.gears.manufacturing.cylindrical import _573
from mastapy.gears.manufacturing.cylindrical.cutters import _688
from mastapy._internal.python_net import python_net_import

_REAL_PLUNGE_SHAVER_OUTPUTS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.PlungeShaving', 'RealPlungeShaverOutputs')


__docformat__ = 'restructuredtext en'
__all__ = ('RealPlungeShaverOutputs',)


class RealPlungeShaverOutputs(_611.PlungeShaverOutputs):
    '''RealPlungeShaverOutputs

    This is a mastapy class.
    '''

    TYPE = _REAL_PLUNGE_SHAVER_OUTPUTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RealPlungeShaverOutputs.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def lead_measurement_method(self) -> '_605.MicroGeometryDefinitionMethod':
        '''MicroGeometryDefinitionMethod: 'LeadMeasurementMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.LeadMeasurementMethod)
        return constructor.new(_605.MicroGeometryDefinitionMethod)(value) if value is not None else None

    @lead_measurement_method.setter
    def lead_measurement_method(self, value: '_605.MicroGeometryDefinitionMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.LeadMeasurementMethod = value

    @property
    def profile_measurement_method(self) -> '_605.MicroGeometryDefinitionMethod':
        '''MicroGeometryDefinitionMethod: 'ProfileMeasurementMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ProfileMeasurementMethod)
        return constructor.new(_605.MicroGeometryDefinitionMethod)(value) if value is not None else None

    @profile_measurement_method.setter
    def profile_measurement_method(self, value: '_605.MicroGeometryDefinitionMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ProfileMeasurementMethod = value

    @property
    def specify_face_width(self) -> 'bool':
        '''bool: 'SpecifyFaceWidth' is the original name of this property.'''

        return self.wrapped.SpecifyFaceWidth

    @specify_face_width.setter
    def specify_face_width(self, value: 'bool'):
        self.wrapped.SpecifyFaceWidth = bool(value) if value else False

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.'''

        return self.wrapped.FaceWidth

    @face_width.setter
    def face_width(self, value: 'float'):
        self.wrapped.FaceWidth = float(value) if value else 0.0

    @property
    def lowest_shaver_tip_diameter(self) -> 'float':
        '''float: 'LowestShaverTipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LowestShaverTipDiameter

    @property
    def highest_shaver_tip_diameter(self) -> 'float':
        '''float: 'HighestShaverTipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HighestShaverTipDiameter

    @property
    def left_flank_micro_geometry(self) -> '_573.CylindricalGearSpecifiedMicroGeometry':
        '''CylindricalGearSpecifiedMicroGeometry: 'LeftFlankMicroGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_573.CylindricalGearSpecifiedMicroGeometry)(self.wrapped.LeftFlankMicroGeometry) if self.wrapped.LeftFlankMicroGeometry is not None else None

    @property
    def right_flank_micro_geometry(self) -> '_573.CylindricalGearSpecifiedMicroGeometry':
        '''CylindricalGearSpecifiedMicroGeometry: 'RightFlankMicroGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_573.CylindricalGearSpecifiedMicroGeometry)(self.wrapped.RightFlankMicroGeometry) if self.wrapped.RightFlankMicroGeometry is not None else None

    @property
    def shaver(self) -> '_688.CylindricalGearPlungeShaver':
        '''CylindricalGearPlungeShaver: 'Shaver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_688.CylindricalGearPlungeShaver)(self.wrapped.Shaver) if self.wrapped.Shaver is not None else None

    @property
    def micro_geometry(self) -> 'List[_573.CylindricalGearSpecifiedMicroGeometry]':
        '''List[CylindricalGearSpecifiedMicroGeometry]: 'MicroGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MicroGeometry, constructor.new(_573.CylindricalGearSpecifiedMicroGeometry))
        return value

    def face_width_requires_calculation(self):
        ''' 'FaceWidthRequiresCalculation' is the original name of this method.'''

        self.wrapped.FaceWidthRequiresCalculation()

    def calculate_micro_geometry(self):
        ''' 'CalculateMicroGeometry' is the original name of this method.'''

        self.wrapped.CalculateMicroGeometry()
