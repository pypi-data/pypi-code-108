'''_963.py

CylindricalGearAbstractRack
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.gear_designs.cylindrical import (
    _969, _996, _964, _966,
    _980, _1031
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.cylindrical.cutters import _692
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_ABSTRACT_RACK = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearAbstractRack')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearAbstractRack',)


class CylindricalGearAbstractRack(_0.APIBase):
    '''CylindricalGearAbstractRack

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_ABSTRACT_RACK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearAbstractRack.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def basic_rack_tooth_depth_factor(self) -> 'float':
        '''float: 'BasicRackToothDepthFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRackToothDepthFactor

    @property
    def basic_rack_addendum_factor(self) -> 'float':
        '''float: 'BasicRackAddendumFactor' is the original name of this property.'''

        return self.wrapped.BasicRackAddendumFactor

    @basic_rack_addendum_factor.setter
    def basic_rack_addendum_factor(self, value: 'float'):
        self.wrapped.BasicRackAddendumFactor = float(value) if value else 0.0

    @property
    def basic_rack_dedendum_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'BasicRackDedendumFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.BasicRackDedendumFactor) if self.wrapped.BasicRackDedendumFactor is not None else None

    @basic_rack_dedendum_factor.setter
    def basic_rack_dedendum_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.BasicRackDedendumFactor = value

    @property
    def use_maximum_edge_radius(self) -> 'bool':
        '''bool: 'UseMaximumEdgeRadius' is the original name of this property.'''

        return self.wrapped.UseMaximumEdgeRadius

    @use_maximum_edge_radius.setter
    def use_maximum_edge_radius(self, value: 'bool'):
        self.wrapped.UseMaximumEdgeRadius = bool(value) if value else False

    @property
    def maximum_possible_cutter_edge_radius(self) -> 'float':
        '''float: 'MaximumPossibleCutterEdgeRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPossibleCutterEdgeRadius

    @property
    def basic_rack_tip_thickness(self) -> 'float':
        '''float: 'BasicRackTipThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRackTipThickness

    @property
    def cutter_tip_width_normal_module(self) -> 'float':
        '''float: 'CutterTipWidthNormalModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CutterTipWidthNormalModule

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def gear(self) -> '_969.CylindricalGearDesign':
        '''CylindricalGearDesign: 'Gear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _969.CylindricalGearDesign.TYPE not in self.wrapped.Gear.__class__.__mro__:
            raise CastException('Failed to cast gear to CylindricalGearDesign. Expected: {}.'.format(self.wrapped.Gear.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Gear.__class__)(self.wrapped.Gear) if self.wrapped.Gear is not None else None

    @property
    def shaper_for_agma_rating(self) -> '_692.CylindricalGearShaper':
        '''CylindricalGearShaper: 'ShaperForAGMARating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_692.CylindricalGearShaper)(self.wrapped.ShaperForAGMARating) if self.wrapped.ShaperForAGMARating is not None else None

    @property
    def left_flank(self) -> '_964.CylindricalGearAbstractRackFlank':
        '''CylindricalGearAbstractRackFlank: 'LeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _964.CylindricalGearAbstractRackFlank.TYPE not in self.wrapped.LeftFlank.__class__.__mro__:
            raise CastException('Failed to cast left_flank to CylindricalGearAbstractRackFlank. Expected: {}.'.format(self.wrapped.LeftFlank.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LeftFlank.__class__)(self.wrapped.LeftFlank) if self.wrapped.LeftFlank is not None else None

    @property
    def left_flank_of_type_cylindrical_gear_basic_rack_flank(self) -> '_966.CylindricalGearBasicRackFlank':
        '''CylindricalGearBasicRackFlank: 'LeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _966.CylindricalGearBasicRackFlank.TYPE not in self.wrapped.LeftFlank.__class__.__mro__:
            raise CastException('Failed to cast left_flank to CylindricalGearBasicRackFlank. Expected: {}.'.format(self.wrapped.LeftFlank.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LeftFlank.__class__)(self.wrapped.LeftFlank) if self.wrapped.LeftFlank is not None else None

    @property
    def left_flank_of_type_cylindrical_gear_pinion_type_cutter_flank(self) -> '_980.CylindricalGearPinionTypeCutterFlank':
        '''CylindricalGearPinionTypeCutterFlank: 'LeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _980.CylindricalGearPinionTypeCutterFlank.TYPE not in self.wrapped.LeftFlank.__class__.__mro__:
            raise CastException('Failed to cast left_flank to CylindricalGearPinionTypeCutterFlank. Expected: {}.'.format(self.wrapped.LeftFlank.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LeftFlank.__class__)(self.wrapped.LeftFlank) if self.wrapped.LeftFlank is not None else None

    @property
    def left_flank_of_type_standard_rack_flank(self) -> '_1031.StandardRackFlank':
        '''StandardRackFlank: 'LeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1031.StandardRackFlank.TYPE not in self.wrapped.LeftFlank.__class__.__mro__:
            raise CastException('Failed to cast left_flank to StandardRackFlank. Expected: {}.'.format(self.wrapped.LeftFlank.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LeftFlank.__class__)(self.wrapped.LeftFlank) if self.wrapped.LeftFlank is not None else None

    @property
    def right_flank(self) -> '_964.CylindricalGearAbstractRackFlank':
        '''CylindricalGearAbstractRackFlank: 'RightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _964.CylindricalGearAbstractRackFlank.TYPE not in self.wrapped.RightFlank.__class__.__mro__:
            raise CastException('Failed to cast right_flank to CylindricalGearAbstractRackFlank. Expected: {}.'.format(self.wrapped.RightFlank.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RightFlank.__class__)(self.wrapped.RightFlank) if self.wrapped.RightFlank is not None else None

    @property
    def right_flank_of_type_cylindrical_gear_basic_rack_flank(self) -> '_966.CylindricalGearBasicRackFlank':
        '''CylindricalGearBasicRackFlank: 'RightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _966.CylindricalGearBasicRackFlank.TYPE not in self.wrapped.RightFlank.__class__.__mro__:
            raise CastException('Failed to cast right_flank to CylindricalGearBasicRackFlank. Expected: {}.'.format(self.wrapped.RightFlank.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RightFlank.__class__)(self.wrapped.RightFlank) if self.wrapped.RightFlank is not None else None

    @property
    def right_flank_of_type_cylindrical_gear_pinion_type_cutter_flank(self) -> '_980.CylindricalGearPinionTypeCutterFlank':
        '''CylindricalGearPinionTypeCutterFlank: 'RightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _980.CylindricalGearPinionTypeCutterFlank.TYPE not in self.wrapped.RightFlank.__class__.__mro__:
            raise CastException('Failed to cast right_flank to CylindricalGearPinionTypeCutterFlank. Expected: {}.'.format(self.wrapped.RightFlank.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RightFlank.__class__)(self.wrapped.RightFlank) if self.wrapped.RightFlank is not None else None

    @property
    def right_flank_of_type_standard_rack_flank(self) -> '_1031.StandardRackFlank':
        '''StandardRackFlank: 'RightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1031.StandardRackFlank.TYPE not in self.wrapped.RightFlank.__class__.__mro__:
            raise CastException('Failed to cast right_flank to StandardRackFlank. Expected: {}.'.format(self.wrapped.RightFlank.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RightFlank.__class__)(self.wrapped.RightFlank) if self.wrapped.RightFlank is not None else None

    @property
    def flanks(self) -> 'List[_964.CylindricalGearAbstractRackFlank]':
        '''List[CylindricalGearAbstractRackFlank]: 'Flanks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Flanks, constructor.new(_964.CylindricalGearAbstractRackFlank))
        return value

    @property
    def both_flanks(self) -> '_964.CylindricalGearAbstractRackFlank':
        '''CylindricalGearAbstractRackFlank: 'BothFlanks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _964.CylindricalGearAbstractRackFlank.TYPE not in self.wrapped.BothFlanks.__class__.__mro__:
            raise CastException('Failed to cast both_flanks to CylindricalGearAbstractRackFlank. Expected: {}.'.format(self.wrapped.BothFlanks.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BothFlanks.__class__)(self.wrapped.BothFlanks) if self.wrapped.BothFlanks is not None else None

    @property
    def both_flanks_of_type_cylindrical_gear_basic_rack_flank(self) -> '_966.CylindricalGearBasicRackFlank':
        '''CylindricalGearBasicRackFlank: 'BothFlanks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _966.CylindricalGearBasicRackFlank.TYPE not in self.wrapped.BothFlanks.__class__.__mro__:
            raise CastException('Failed to cast both_flanks to CylindricalGearBasicRackFlank. Expected: {}.'.format(self.wrapped.BothFlanks.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BothFlanks.__class__)(self.wrapped.BothFlanks) if self.wrapped.BothFlanks is not None else None

    @property
    def both_flanks_of_type_cylindrical_gear_pinion_type_cutter_flank(self) -> '_980.CylindricalGearPinionTypeCutterFlank':
        '''CylindricalGearPinionTypeCutterFlank: 'BothFlanks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _980.CylindricalGearPinionTypeCutterFlank.TYPE not in self.wrapped.BothFlanks.__class__.__mro__:
            raise CastException('Failed to cast both_flanks to CylindricalGearPinionTypeCutterFlank. Expected: {}.'.format(self.wrapped.BothFlanks.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BothFlanks.__class__)(self.wrapped.BothFlanks) if self.wrapped.BothFlanks is not None else None

    @property
    def both_flanks_of_type_standard_rack_flank(self) -> '_1031.StandardRackFlank':
        '''StandardRackFlank: 'BothFlanks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1031.StandardRackFlank.TYPE not in self.wrapped.BothFlanks.__class__.__mro__:
            raise CastException('Failed to cast both_flanks to StandardRackFlank. Expected: {}.'.format(self.wrapped.BothFlanks.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BothFlanks.__class__)(self.wrapped.BothFlanks) if self.wrapped.BothFlanks is not None else None

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def output_default_report_to(self, file_path: 'str'):
        ''' 'OutputDefaultReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputDefaultReportTo(file_path if file_path else '')

    def get_default_report_with_encoded_images(self) -> 'str':
        ''' 'GetDefaultReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetDefaultReportWithEncodedImages()
        return method_result

    def output_active_report_to(self, file_path: 'str'):
        ''' 'OutputActiveReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportTo(file_path if file_path else '')

    def output_active_report_as_text_to(self, file_path: 'str'):
        ''' 'OutputActiveReportAsTextTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportAsTextTo(file_path if file_path else '')

    def get_active_report_with_encoded_images(self) -> 'str':
        ''' 'GetActiveReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetActiveReportWithEncodedImages()
        return method_result

    def output_named_report_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportTo(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_masta_report(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsMastaReport' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsMastaReport(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_text_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsTextTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsTextTo(report_name if report_name else '', file_path if file_path else '')

    def get_named_report_with_encoded_images(self, report_name: 'str') -> 'str':
        ''' 'GetNamedReportWithEncodedImages' is the original name of this method.

        Args:
            report_name (str)

        Returns:
            str
        '''

        report_name = str(report_name)
        method_result = self.wrapped.GetNamedReportWithEncodedImages(report_name if report_name else '')
        return method_result
