'''_708.py

RackShape
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical.cutters import _690, _686, _687
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.cylindrical.cutters.tangibles import _701
from mastapy._internal.python_net import python_net_import

_RACK_SHAPE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters.Tangibles', 'RackShape')


__docformat__ = 'restructuredtext en'
__all__ = ('RackShape',)


class RackShape(_701.CutterShapeDefinition):
    '''RackShape

    This is a mastapy class.
    '''

    TYPE = _RACK_SHAPE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RackShape.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def edge_radius(self) -> 'float':
        '''float: 'EdgeRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EdgeRadius

    @property
    def protuberance(self) -> 'float':
        '''float: 'Protuberance' is the original name of this property.'''

        return self.wrapped.Protuberance

    @protuberance.setter
    def protuberance(self, value: 'float'):
        self.wrapped.Protuberance = float(value) if value else 0.0

    @property
    def actual_protuberance(self) -> 'float':
        '''float: 'ActualProtuberance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ActualProtuberance

    @property
    def addendum(self) -> 'float':
        '''float: 'Addendum' is the original name of this property.'''

        return self.wrapped.Addendum

    @addendum.setter
    def addendum(self, value: 'float'):
        self.wrapped.Addendum = float(value) if value else 0.0

    @property
    def addendum_form(self) -> 'float':
        '''float: 'AddendumForm' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AddendumForm

    @property
    def protuberance_pressure_angle(self) -> 'float':
        '''float: 'ProtuberancePressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProtuberancePressureAngle

    @property
    def protuberance_height(self) -> 'float':
        '''float: 'ProtuberanceHeight' is the original name of this property.'''

        return self.wrapped.ProtuberanceHeight

    @protuberance_height.setter
    def protuberance_height(self, value: 'float'):
        self.wrapped.ProtuberanceHeight = float(value) if value else 0.0

    @property
    def minimum_protuberance_height(self) -> 'float':
        '''float: 'MinimumProtuberanceHeight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumProtuberanceHeight

    @property
    def protuberance_relative_to_main_blade_pressure_angle_nearest_hob_tip(self) -> 'float':
        '''float: 'ProtuberanceRelativeToMainBladePressureAngleNearestHobTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProtuberanceRelativeToMainBladePressureAngleNearestHobTip

    @property
    def maximum_protuberance_blade_pressure_angle(self) -> 'float':
        '''float: 'MaximumProtuberanceBladePressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumProtuberanceBladePressureAngle

    @property
    def minimum_protuberance_blade_pressure_angle(self) -> 'float':
        '''float: 'MinimumProtuberanceBladePressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumProtuberanceBladePressureAngle

    @property
    def semi_topping_pressure_angle(self) -> 'float':
        '''float: 'SemiToppingPressureAngle' is the original name of this property.'''

        return self.wrapped.SemiToppingPressureAngle

    @semi_topping_pressure_angle.setter
    def semi_topping_pressure_angle(self, value: 'float'):
        self.wrapped.SemiToppingPressureAngle = float(value) if value else 0.0

    @property
    def semi_topping_height(self) -> 'float':
        '''float: 'SemiToppingHeight' is the original name of this property.'''

        return self.wrapped.SemiToppingHeight

    @semi_topping_height.setter
    def semi_topping_height(self, value: 'float'):
        self.wrapped.SemiToppingHeight = float(value) if value else 0.0

    @property
    def semi_topping_start(self) -> 'float':
        '''float: 'SemiToppingStart' is the original name of this property.'''

        return self.wrapped.SemiToppingStart

    @semi_topping_start.setter
    def semi_topping_start(self, value: 'float'):
        self.wrapped.SemiToppingStart = float(value) if value else 0.0

    @property
    def normal_thickness(self) -> 'float':
        '''float: 'NormalThickness' is the original name of this property.'''

        return self.wrapped.NormalThickness

    @normal_thickness.setter
    def normal_thickness(self, value: 'float'):
        self.wrapped.NormalThickness = float(value) if value else 0.0

    @property
    def dedendum(self) -> 'float':
        '''float: 'Dedendum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Dedendum

    @property
    def hob_whole_depth(self) -> 'float':
        '''float: 'HobWholeDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HobWholeDepth

    @property
    def has_semi_topping_blade(self) -> 'bool':
        '''bool: 'HasSemiToppingBlade' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasSemiToppingBlade

    @property
    def edge_height(self) -> 'float':
        '''float: 'EdgeHeight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EdgeHeight

    @property
    def protuberance_length(self) -> 'float':
        '''float: 'ProtuberanceLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProtuberanceLength

    @property
    def maximum_edge_radius(self) -> 'float':
        '''float: 'MaximumEdgeRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumEdgeRadius

    @property
    def flat_root_width(self) -> 'float':
        '''float: 'FlatRootWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FlatRootWidth

    @property
    def flat_tip_width(self) -> 'float':
        '''float: 'FlatTipWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FlatTipWidth

    @property
    def main_blade_pressure_angle_nearest_hob_root(self) -> 'float':
        '''float: 'MainBladePressureAngleNearestHobRoot' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MainBladePressureAngleNearestHobRoot

    @property
    def main_blade_pressure_angle_nearest_hob_tip(self) -> 'float':
        '''float: 'MainBladePressureAngleNearestHobTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MainBladePressureAngleNearestHobTip

    @property
    def design(self) -> '_690.CylindricalGearRackDesign':
        '''CylindricalGearRackDesign: 'Design' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _690.CylindricalGearRackDesign.TYPE not in self.wrapped.Design.__class__.__mro__:
            raise CastException('Failed to cast design to CylindricalGearRackDesign. Expected: {}.'.format(self.wrapped.Design.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Design.__class__)(self.wrapped.Design) if self.wrapped.Design is not None else None

    @property
    def design_of_type_cylindrical_gear_grinding_worm(self) -> '_686.CylindricalGearGrindingWorm':
        '''CylindricalGearGrindingWorm: 'Design' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _686.CylindricalGearGrindingWorm.TYPE not in self.wrapped.Design.__class__.__mro__:
            raise CastException('Failed to cast design to CylindricalGearGrindingWorm. Expected: {}.'.format(self.wrapped.Design.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Design.__class__)(self.wrapped.Design) if self.wrapped.Design is not None else None

    @property
    def design_of_type_cylindrical_gear_hob_design(self) -> '_687.CylindricalGearHobDesign':
        '''CylindricalGearHobDesign: 'Design' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _687.CylindricalGearHobDesign.TYPE not in self.wrapped.Design.__class__.__mro__:
            raise CastException('Failed to cast design to CylindricalGearHobDesign. Expected: {}.'.format(self.wrapped.Design.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Design.__class__)(self.wrapped.Design) if self.wrapped.Design is not None else None
