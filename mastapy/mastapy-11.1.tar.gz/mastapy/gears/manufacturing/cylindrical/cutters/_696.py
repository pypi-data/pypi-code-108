'''_696.py

InvoluteCutterDesign
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears import _299
from mastapy.gears.gear_designs.cylindrical import (
    _1040, _1001, _1021, _1039
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.cylindrical.cutters import _691
from mastapy._internal.python_net import python_net_import

_INVOLUTE_CUTTER_DESIGN = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters', 'InvoluteCutterDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('InvoluteCutterDesign',)


class InvoluteCutterDesign(_691.CylindricalGearRealCutterDesign):
    '''InvoluteCutterDesign

    This is a mastapy class.
    '''

    TYPE = _INVOLUTE_CUTTER_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InvoluteCutterDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_teeth(self) -> 'float':
        '''float: 'NumberOfTeeth' is the original name of this property.'''

        return self.wrapped.NumberOfTeeth

    @number_of_teeth.setter
    def number_of_teeth(self, value: 'float'):
        self.wrapped.NumberOfTeeth = float(value) if value else 0.0

    @property
    def hand(self) -> '_299.Hand':
        '''Hand: 'Hand' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.Hand)
        return constructor.new(_299.Hand)(value) if value is not None else None

    @hand.setter
    def hand(self, value: '_299.Hand'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.Hand = value

    @property
    def helix_angle(self) -> 'float':
        '''float: 'HelixAngle' is the original name of this property.'''

        return self.wrapped.HelixAngle

    @helix_angle.setter
    def helix_angle(self, value: 'float'):
        self.wrapped.HelixAngle = float(value) if value else 0.0

    @property
    def tooth_thickness(self) -> '_1040.ToothThicknessSpecificationBase':
        '''ToothThicknessSpecificationBase: 'ToothThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1040.ToothThicknessSpecificationBase.TYPE not in self.wrapped.ToothThickness.__class__.__mro__:
            raise CastException('Failed to cast tooth_thickness to ToothThicknessSpecificationBase. Expected: {}.'.format(self.wrapped.ToothThickness.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ToothThickness.__class__)(self.wrapped.ToothThickness) if self.wrapped.ToothThickness is not None else None

    @property
    def tooth_thickness_of_type_finish_tooth_thickness_design_specification(self) -> '_1001.FinishToothThicknessDesignSpecification':
        '''FinishToothThicknessDesignSpecification: 'ToothThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1001.FinishToothThicknessDesignSpecification.TYPE not in self.wrapped.ToothThickness.__class__.__mro__:
            raise CastException('Failed to cast tooth_thickness to FinishToothThicknessDesignSpecification. Expected: {}.'.format(self.wrapped.ToothThickness.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ToothThickness.__class__)(self.wrapped.ToothThickness) if self.wrapped.ToothThickness is not None else None

    @property
    def tooth_thickness_of_type_readonly_tooth_thickness_specification(self) -> '_1021.ReadonlyToothThicknessSpecification':
        '''ReadonlyToothThicknessSpecification: 'ToothThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1021.ReadonlyToothThicknessSpecification.TYPE not in self.wrapped.ToothThickness.__class__.__mro__:
            raise CastException('Failed to cast tooth_thickness to ReadonlyToothThicknessSpecification. Expected: {}.'.format(self.wrapped.ToothThickness.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ToothThickness.__class__)(self.wrapped.ToothThickness) if self.wrapped.ToothThickness is not None else None

    @property
    def tooth_thickness_of_type_tooth_thickness_specification(self) -> '_1039.ToothThicknessSpecification':
        '''ToothThicknessSpecification: 'ToothThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1039.ToothThicknessSpecification.TYPE not in self.wrapped.ToothThickness.__class__.__mro__:
            raise CastException('Failed to cast tooth_thickness to ToothThicknessSpecification. Expected: {}.'.format(self.wrapped.ToothThickness.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ToothThickness.__class__)(self.wrapped.ToothThickness) if self.wrapped.ToothThickness is not None else None
