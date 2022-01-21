'''_478.py

ISO6336AbstractGearSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical import _429
from mastapy._internal.python_net import python_net_import

_ISO6336_ABSTRACT_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ISO6336AbstractGearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO6336AbstractGearSingleFlankRating',)


class ISO6336AbstractGearSingleFlankRating(_429.CylindricalGearSingleFlankRating):
    '''ISO6336AbstractGearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _ISO6336_ABSTRACT_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO6336AbstractGearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def roughness_factor(self) -> 'float':
        '''float: 'RoughnessFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RoughnessFactor

    @property
    def face_width_for_root_stress(self) -> 'float':
        '''float: 'FaceWidthForRootStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidthForRootStress

    @property
    def nominal_tooth_root_stress(self) -> 'float':
        '''float: 'NominalToothRootStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalToothRootStress

    @property
    def g(self) -> 'float':
        '''float: 'G' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.G

    @property
    def e(self) -> 'float':
        '''float: 'E' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.E

    @property
    def h(self) -> 'float':
        '''float: 'H' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.H

    @property
    def intermediate_angle(self) -> 'float':
        '''float: 'IntermediateAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntermediateAngle

    @property
    def stress_correction_factor(self) -> 'float':
        '''float: 'StressCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressCorrectionFactor

    @property
    def stress_correction_factor_bending_for_test_gears(self) -> 'float':
        '''float: 'StressCorrectionFactorBendingForTestGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressCorrectionFactorBendingForTestGears

    @property
    def form_factor(self) -> 'float':
        '''float: 'FormFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FormFactor

    @property
    def notch_parameter(self) -> 'float':
        '''float: 'NotchParameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NotchParameter
