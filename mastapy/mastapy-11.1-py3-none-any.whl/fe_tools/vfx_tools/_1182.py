'''_1182.py

ProSolveOptions
'''


from typing import List

from mastapy._internal.implicit import enum_with_selected_value, overridable
from mastapy.fe_tools.vfx_tools.vfx_enums import _1184, _1183
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PRO_SOLVE_OPTIONS = python_net_import('SMT.MastaAPI.FETools.VfxTools', 'ProSolveOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('ProSolveOptions',)


class ProSolveOptions(_0.APIBase):
    '''ProSolveOptions

    This is a mastapy class.
    '''

    TYPE = _PRO_SOLVE_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ProSolveOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def type_of_solver(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ProSolveSolverType':
        '''enum_with_selected_value.EnumWithSelectedValue_ProSolveSolverType: 'TypeOfSolver' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ProSolveSolverType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.TypeOfSolver, value) if self.wrapped.TypeOfSolver is not None else None

    @type_of_solver.setter
    def type_of_solver(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ProSolveSolverType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ProSolveSolverType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.TypeOfSolver = value

    @property
    def use_out_of_core_solver(self) -> 'bool':
        '''bool: 'UseOutOfCoreSolver' is the original name of this property.'''

        return self.wrapped.UseOutOfCoreSolver

    @use_out_of_core_solver.setter
    def use_out_of_core_solver(self, value: 'bool'):
        self.wrapped.UseOutOfCoreSolver = bool(value) if value else False

    @property
    def mpc_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ProSolveMpcType':
        '''enum_with_selected_value.EnumWithSelectedValue_ProSolveMpcType: 'MPCType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ProSolveMpcType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.MPCType, value) if self.wrapped.MPCType is not None else None

    @mpc_type.setter
    def mpc_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ProSolveMpcType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ProSolveMpcType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.MPCType = value

    @property
    def penalty_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PenaltyFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PenaltyFactor) if self.wrapped.PenaltyFactor is not None else None

    @penalty_factor.setter
    def penalty_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PenaltyFactor = value

    @property
    def use_jacobian_checking(self) -> 'bool':
        '''bool: 'UseJacobianChecking' is the original name of this property.'''

        return self.wrapped.UseJacobianChecking

    @use_jacobian_checking.setter
    def use_jacobian_checking(self, value: 'bool'):
        self.wrapped.UseJacobianChecking = bool(value) if value else False

    @property
    def compensate_for_singularities_in_model(self) -> 'bool':
        '''bool: 'CompensateForSingularitiesInModel' is the original name of this property.'''

        return self.wrapped.CompensateForSingularitiesInModel

    @compensate_for_singularities_in_model.setter
    def compensate_for_singularities_in_model(self, value: 'bool'):
        self.wrapped.CompensateForSingularitiesInModel = bool(value) if value else False

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
