'''_1257.py

CycloidalDiscModificationsSpecification
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.cycloidal import _1258, _1252
from mastapy.math_utility import _1333
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_MODIFICATIONS_SPECIFICATION = python_net_import('SMT.MastaAPI.Cycloidal', 'CycloidalDiscModificationsSpecification')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscModificationsSpecification',)


class CycloidalDiscModificationsSpecification(_0.APIBase):
    '''CycloidalDiscModificationsSpecification

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_MODIFICATIONS_SPECIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscModificationsSpecification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def generating_wheel_diameter_modification(self) -> 'float':
        '''float: 'GeneratingWheelDiameterModification' is the original name of this property.'''

        return self.wrapped.GeneratingWheelDiameterModification

    @generating_wheel_diameter_modification.setter
    def generating_wheel_diameter_modification(self, value: 'float'):
        self.wrapped.GeneratingWheelDiameterModification = float(value) if value else 0.0

    @property
    def generating_wheel_centre_circle_diameter_modification(self) -> 'float':
        '''float: 'GeneratingWheelCentreCircleDiameterModification' is the original name of this property.'''

        return self.wrapped.GeneratingWheelCentreCircleDiameterModification

    @generating_wheel_centre_circle_diameter_modification.setter
    def generating_wheel_centre_circle_diameter_modification(self, value: 'float'):
        self.wrapped.GeneratingWheelCentreCircleDiameterModification = float(value) if value else 0.0

    @property
    def angular_offset_modification(self) -> 'float':
        '''float: 'AngularOffsetModification' is the original name of this property.'''

        return self.wrapped.AngularOffsetModification

    @angular_offset_modification.setter
    def angular_offset_modification(self, value: 'float'):
        self.wrapped.AngularOffsetModification = float(value) if value else 0.0

    @property
    def specify_measured_profile_modification(self) -> 'bool':
        '''bool: 'SpecifyMeasuredProfileModification' is the original name of this property.'''

        return self.wrapped.SpecifyMeasuredProfileModification

    @specify_measured_profile_modification.setter
    def specify_measured_profile_modification(self, value: 'bool'):
        self.wrapped.SpecifyMeasuredProfileModification = bool(value) if value else False

    @property
    def direction_of_measured_modifications(self) -> '_1258.DirectionOfMeasuredModifications':
        '''DirectionOfMeasuredModifications: 'DirectionOfMeasuredModifications' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.DirectionOfMeasuredModifications)
        return constructor.new(_1258.DirectionOfMeasuredModifications)(value) if value is not None else None

    @direction_of_measured_modifications.setter
    def direction_of_measured_modifications(self, value: '_1258.DirectionOfMeasuredModifications'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.DirectionOfMeasuredModifications = value

    @property
    def measured_profile_modification(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'MeasuredProfileModification' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.MeasuredProfileModification) if self.wrapped.MeasuredProfileModification is not None else None

    @measured_profile_modification.setter
    def measured_profile_modification(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.MeasuredProfileModification = value

    @property
    def crowning_specification_method(self) -> '_1252.CrowningSpecificationMethod':
        '''CrowningSpecificationMethod: 'CrowningSpecificationMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.CrowningSpecificationMethod)
        return constructor.new(_1252.CrowningSpecificationMethod)(value) if value is not None else None

    @crowning_specification_method.setter
    def crowning_specification_method(self, value: '_1252.CrowningSpecificationMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.CrowningSpecificationMethod = value

    @property
    def crowning_radius(self) -> 'float':
        '''float: 'CrowningRadius' is the original name of this property.'''

        return self.wrapped.CrowningRadius

    @crowning_radius.setter
    def crowning_radius(self, value: 'float'):
        self.wrapped.CrowningRadius = float(value) if value else 0.0

    @property
    def distance_to_where_crowning_starts_from_lobe_centre(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DistanceToWhereCrowningStartsFromLobeCentre' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DistanceToWhereCrowningStartsFromLobeCentre) if self.wrapped.DistanceToWhereCrowningStartsFromLobeCentre is not None else None

    @distance_to_where_crowning_starts_from_lobe_centre.setter
    def distance_to_where_crowning_starts_from_lobe_centre(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DistanceToWhereCrowningStartsFromLobeCentre = value

    @property
    def coefficient_for_logarithmic_crowning(self) -> 'float':
        '''float: 'CoefficientForLogarithmicCrowning' is the original name of this property.'''

        return self.wrapped.CoefficientForLogarithmicCrowning

    @coefficient_for_logarithmic_crowning.setter
    def coefficient_for_logarithmic_crowning(self, value: 'float'):
        self.wrapped.CoefficientForLogarithmicCrowning = float(value) if value else 0.0
