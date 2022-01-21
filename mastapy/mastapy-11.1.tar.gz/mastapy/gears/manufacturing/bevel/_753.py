'''_753.py

ConicalSetMicroGeometryConfigBase
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears import _291
from mastapy.gears.analysis import _1175
from mastapy._internal.python_net import python_net_import

_CONICAL_SET_MICRO_GEOMETRY_CONFIG_BASE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'ConicalSetMicroGeometryConfigBase')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalSetMicroGeometryConfigBase',)


class ConicalSetMicroGeometryConfigBase(_1175.GearSetImplementationDetail):
    '''ConicalSetMicroGeometryConfigBase

    This is a mastapy class.
    '''

    TYPE = _CONICAL_SET_MICRO_GEOMETRY_CONFIG_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalSetMicroGeometryConfigBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def compound_layer_thickness(self) -> 'float':
        '''float: 'CompoundLayerThickness' is the original name of this property.'''

        return self.wrapped.CompoundLayerThickness

    @compound_layer_thickness.setter
    def compound_layer_thickness(self, value: 'float'):
        self.wrapped.CompoundLayerThickness = float(value) if value else 0.0

    @property
    def number_of_points_for_interpolated_surface_u(self) -> 'int':
        '''int: 'NumberOfPointsForInterpolatedSurfaceU' is the original name of this property.'''

        return self.wrapped.NumberOfPointsForInterpolatedSurfaceU

    @number_of_points_for_interpolated_surface_u.setter
    def number_of_points_for_interpolated_surface_u(self, value: 'int'):
        self.wrapped.NumberOfPointsForInterpolatedSurfaceU = int(value) if value else 0

    @property
    def number_of_points_for_interpolated_surface_v(self) -> 'int':
        '''int: 'NumberOfPointsForInterpolatedSurfaceV' is the original name of this property.'''

        return self.wrapped.NumberOfPointsForInterpolatedSurfaceV

    @number_of_points_for_interpolated_surface_v.setter
    def number_of_points_for_interpolated_surface_v(self, value: 'int'):
        self.wrapped.NumberOfPointsForInterpolatedSurfaceV = int(value) if value else 0

    @property
    def write_contact_chart_to_file_after_solve(self) -> 'bool':
        '''bool: 'WriteContactChartToFileAfterSolve' is the original name of this property.'''

        return self.wrapped.WriteContactChartToFileAfterSolve

    @write_contact_chart_to_file_after_solve.setter
    def write_contact_chart_to_file_after_solve(self, value: 'bool'):
        self.wrapped.WriteContactChartToFileAfterSolve = bool(value) if value else False

    @property
    def file_location_for_contact_chart(self) -> 'str':
        '''str: 'FileLocationForContactChart' is the original name of this property.'''

        return self.wrapped.FileLocationForContactChart

    @file_location_for_contact_chart.setter
    def file_location_for_contact_chart(self, value: 'str'):
        self.wrapped.FileLocationForContactChart = str(value) if value else ''

    @property
    def deflection_from_bending_option(self) -> '_291.DeflectionFromBendingOption':
        '''DeflectionFromBendingOption: 'DeflectionFromBendingOption' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.DeflectionFromBendingOption)
        return constructor.new(_291.DeflectionFromBendingOption)(value) if value is not None else None

    @deflection_from_bending_option.setter
    def deflection_from_bending_option(self, value: '_291.DeflectionFromBendingOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.DeflectionFromBendingOption = value

    @property
    def single_tooth_stiffness(self) -> 'float':
        '''float: 'SingleToothStiffness' is the original name of this property.'''

        return self.wrapped.SingleToothStiffness

    @single_tooth_stiffness.setter
    def single_tooth_stiffness(self, value: 'float'):
        self.wrapped.SingleToothStiffness = float(value) if value else 0.0

    @property
    def number_of_rows_for_flank_grid(self) -> 'int':
        '''int: 'NumberOfRowsForFlankGrid' is the original name of this property.'''

        return self.wrapped.NumberOfRowsForFlankGrid

    @number_of_rows_for_flank_grid.setter
    def number_of_rows_for_flank_grid(self, value: 'int'):
        self.wrapped.NumberOfRowsForFlankGrid = int(value) if value else 0

    @property
    def number_of_columns_for_grid(self) -> 'int':
        '''int: 'NumberOfColumnsForGrid' is the original name of this property.'''

        return self.wrapped.NumberOfColumnsForGrid

    @number_of_columns_for_grid.setter
    def number_of_columns_for_grid(self, value: 'int'):
        self.wrapped.NumberOfColumnsForGrid = int(value) if value else 0

    @property
    def number_of_rows_for_fillet_grid(self) -> 'int':
        '''int: 'NumberOfRowsForFilletGrid' is the original name of this property.'''

        return self.wrapped.NumberOfRowsForFilletGrid

    @number_of_rows_for_fillet_grid.setter
    def number_of_rows_for_fillet_grid(self, value: 'int'):
        self.wrapped.NumberOfRowsForFilletGrid = int(value) if value else 0
