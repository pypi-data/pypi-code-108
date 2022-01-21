'''_993.py

CylindricalMeshedGearFlank
'''


from mastapy._internal import constructor
from mastapy.utility_gui.charts import (
    _1626, _1617, _1622, _1623
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.cylindrical import _981
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_MESHED_GEAR_FLANK = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalMeshedGearFlank')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalMeshedGearFlank',)


class CylindricalMeshedGearFlank(_0.APIBase):
    '''CylindricalMeshedGearFlank

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_MESHED_GEAR_FLANK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalMeshedGearFlank.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def sliding_factor_at_tooth_tip(self) -> 'float':
        '''float: 'SlidingFactorAtToothTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidingFactorAtToothTip

    @property
    def clearance_from_form_diameter_to_sap_diameter(self) -> 'float':
        '''float: 'ClearanceFromFormDiameterToSAPDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClearanceFromFormDiameterToSAPDiameter

    @property
    def dedendum_path_of_contact(self) -> 'float':
        '''float: 'DedendumPathOfContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DedendumPathOfContact

    @property
    def specific_sliding_at_sap(self) -> 'float':
        '''float: 'SpecificSlidingAtSAP' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpecificSlidingAtSAP

    @property
    def specific_sliding_at_eap(self) -> 'float':
        '''float: 'SpecificSlidingAtEAP' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpecificSlidingAtEAP

    @property
    def specific_sliding_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'SpecificSlidingChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.SpecificSlidingChart.__class__.__mro__:
            raise CastException('Failed to cast specific_sliding_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.SpecificSlidingChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SpecificSlidingChart.__class__)(self.wrapped.SpecificSlidingChart) if self.wrapped.SpecificSlidingChart is not None else None

    @property
    def form_over_dimension(self) -> 'float':
        '''float: 'FormOverDimension' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FormOverDimension

    @property
    def length_of_addendum_path_of_contact(self) -> 'float':
        '''float: 'LengthOfAddendumPathOfContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthOfAddendumPathOfContact

    @property
    def partial_contact_ratio(self) -> 'float':
        '''float: 'PartialContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PartialContactRatio

    @property
    def load_direction_angle(self) -> 'float':
        '''float: 'LoadDirectionAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDirectionAngle

    @property
    def profile_line_length_of_the_active_tooth_flank(self) -> 'float':
        '''float: 'ProfileLineLengthOfTheActiveToothFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileLineLengthOfTheActiveToothFlank

    @property
    def flank_name(self) -> 'str':
        '''str: 'FlankName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FlankName

    @property
    def lowest_point_of_fewest_tooth_contacts(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'LowestPointOfFewestToothContacts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.LowestPointOfFewestToothContacts) if self.wrapped.LowestPointOfFewestToothContacts is not None else None

    @property
    def highest_point_of_fewest_tooth_contacts(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'HighestPointOfFewestToothContacts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.HighestPointOfFewestToothContacts) if self.wrapped.HighestPointOfFewestToothContacts is not None else None

    @property
    def start_of_active_profile(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'StartOfActiveProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.StartOfActiveProfile) if self.wrapped.StartOfActiveProfile is not None else None

    @property
    def end_of_active_profile(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'EndOfActiveProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.EndOfActiveProfile) if self.wrapped.EndOfActiveProfile is not None else None
