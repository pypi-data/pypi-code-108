'''_474.py

ISO63362006GearSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical.iso6336 import _469, _480
from mastapy._internal.python_net import python_net_import

_ISO63362006_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ISO63362006GearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO63362006GearSingleFlankRating',)


class ISO63362006GearSingleFlankRating(_480.ISO6336AbstractMetalGearSingleFlankRating):
    '''ISO63362006GearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _ISO63362006_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO63362006GearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def nominal_tooth_root_stress(self) -> 'float':
        '''float: 'NominalToothRootStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalToothRootStress

    @property
    def rim_thickness_factor(self) -> 'float':
        '''float: 'RimThicknessFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RimThicknessFactor

    @property
    def rim_thickness_over_whole_depth(self) -> 'float':
        '''float: 'RimThicknessOverWholeDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RimThicknessOverWholeDepth

    @property
    def work_hardening_factor_for_reference_contact_stress(self) -> 'float':
        '''float: 'WorkHardeningFactorForReferenceContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkHardeningFactorForReferenceContactStress

    @property
    def work_hardening_factor_for_static_contact_stress(self) -> 'float':
        '''float: 'WorkHardeningFactorForStaticContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkHardeningFactorForStaticContactStress

    @property
    def tooth_fatigue_fracture_results(self) -> '_469.CylindricalGearToothFatigueFractureResults':
        '''CylindricalGearToothFatigueFractureResults: 'ToothFatigueFractureResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_469.CylindricalGearToothFatigueFractureResults)(self.wrapped.ToothFatigueFractureResults) if self.wrapped.ToothFatigueFractureResults is not None else None
