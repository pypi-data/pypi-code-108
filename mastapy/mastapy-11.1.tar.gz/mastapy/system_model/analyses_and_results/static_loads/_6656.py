'''_6656.py

PointLoadLoadCase
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import overridable, enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.part_model import _2212
from mastapy.nodal_analysis.varying_input_components import _90, _91
from mastapy.system_model.analyses_and_results.static_loads import _6655, _6700
from mastapy._internal.python_net import python_net_import

_POINT_LOAD_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'PointLoadLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('PointLoadLoadCase',)


class PointLoadLoadCase(_6700.VirtualComponentLoadCase):
    '''PointLoadLoadCase

    This is a mastapy class.
    '''

    TYPE = _POINT_LOAD_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PointLoadLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def tangential_load(self) -> 'float':
        '''float: 'TangentialLoad' is the original name of this property.'''

        return self.wrapped.TangentialLoad

    @tangential_load.setter
    def tangential_load(self, value: 'float'):
        self.wrapped.TangentialLoad = float(value) if value else 0.0

    @property
    def radial_load(self) -> 'float':
        '''float: 'RadialLoad' is the original name of this property.'''

        return self.wrapped.RadialLoad

    @radial_load.setter
    def radial_load(self, value: 'float'):
        self.wrapped.RadialLoad = float(value) if value else 0.0

    @property
    def magnitude_radial_force(self) -> 'float':
        '''float: 'MagnitudeRadialForce' is the original name of this property.'''

        return self.wrapped.MagnitudeRadialForce

    @magnitude_radial_force.setter
    def magnitude_radial_force(self, value: 'float'):
        self.wrapped.MagnitudeRadialForce = float(value) if value else 0.0

    @property
    def angle_of_radial_force(self) -> 'float':
        '''float: 'AngleOfRadialForce' is the original name of this property.'''

        return self.wrapped.AngleOfRadialForce

    @angle_of_radial_force.setter
    def angle_of_radial_force(self, value: 'float'):
        self.wrapped.AngleOfRadialForce = float(value) if value else 0.0

    @property
    def twist_theta_z(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TwistThetaZ' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TwistThetaZ) if self.wrapped.TwistThetaZ is not None else None

    @twist_theta_z.setter
    def twist_theta_z(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.TwistThetaZ = value

    @property
    def twist_theta_x(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TwistThetaX' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TwistThetaX) if self.wrapped.TwistThetaX is not None else None

    @twist_theta_x.setter
    def twist_theta_x(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.TwistThetaX = value

    @property
    def twist_theta_y(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TwistThetaY' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TwistThetaY) if self.wrapped.TwistThetaY is not None else None

    @twist_theta_y.setter
    def twist_theta_y(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.TwistThetaY = value

    @property
    def displacement_x(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DisplacementX' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DisplacementX) if self.wrapped.DisplacementX is not None else None

    @displacement_x.setter
    def displacement_x(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DisplacementX = value

    @property
    def displacement_y(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DisplacementY' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DisplacementY) if self.wrapped.DisplacementY is not None else None

    @displacement_y.setter
    def displacement_y(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DisplacementY = value

    @property
    def displacement_z(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DisplacementZ' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DisplacementZ) if self.wrapped.DisplacementZ is not None else None

    @displacement_z.setter
    def displacement_z(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DisplacementZ = value

    @property
    def force_specification_options(self) -> 'enum_with_selected_value.EnumWithSelectedValue_PointLoadLoadCase_ForceSpecification':
        '''enum_with_selected_value.EnumWithSelectedValue_PointLoadLoadCase_ForceSpecification: 'ForceSpecificationOptions' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_PointLoadLoadCase_ForceSpecification.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ForceSpecificationOptions, value) if self.wrapped.ForceSpecificationOptions is not None else None

    @force_specification_options.setter
    def force_specification_options(self, value: 'enum_with_selected_value.EnumWithSelectedValue_PointLoadLoadCase_ForceSpecification.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_PointLoadLoadCase_ForceSpecification.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ForceSpecificationOptions = value

    @property
    def component_design(self) -> '_2212.PointLoad':
        '''PointLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2212.PointLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def force_x(self) -> '_90.ForceInputComponent':
        '''ForceInputComponent: 'ForceX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_90.ForceInputComponent)(self.wrapped.ForceX) if self.wrapped.ForceX is not None else None

    @property
    def force_y(self) -> '_90.ForceInputComponent':
        '''ForceInputComponent: 'ForceY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_90.ForceInputComponent)(self.wrapped.ForceY) if self.wrapped.ForceY is not None else None

    @property
    def axial_load(self) -> '_90.ForceInputComponent':
        '''ForceInputComponent: 'AxialLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_90.ForceInputComponent)(self.wrapped.AxialLoad) if self.wrapped.AxialLoad is not None else None

    @property
    def moment_x(self) -> '_91.MomentInputComponent':
        '''MomentInputComponent: 'MomentX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_91.MomentInputComponent)(self.wrapped.MomentX) if self.wrapped.MomentX is not None else None

    @property
    def moment_y(self) -> '_91.MomentInputComponent':
        '''MomentInputComponent: 'MomentY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_91.MomentInputComponent)(self.wrapped.MomentY) if self.wrapped.MomentY is not None else None

    @property
    def moment_z(self) -> '_91.MomentInputComponent':
        '''MomentInputComponent: 'MomentZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_91.MomentInputComponent)(self.wrapped.MomentZ) if self.wrapped.MomentZ is not None else None

    def get_harmonic_load_data_for_import(self) -> '_6655.PointLoadHarmonicLoadData':
        ''' 'GetHarmonicLoadDataForImport' is the original name of this method.

        Returns:
            mastapy.system_model.analyses_and_results.static_loads.PointLoadHarmonicLoadData
        '''

        method_result = self.wrapped.GetHarmonicLoadDataForImport()
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
