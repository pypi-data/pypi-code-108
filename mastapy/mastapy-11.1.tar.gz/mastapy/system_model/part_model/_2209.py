'''_2209.py

Part
'''


from typing import List

from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.math_utility import _1317
from mastapy.system_model.connections_and_sockets import _2014
from mastapy.system_model.import_export import _1983
from mastapy.system_model.part_model import _2176
from mastapy.system_model import _1951
from mastapy._internal.python_net import python_net_import

_PART = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Part')


__docformat__ = 'restructuredtext en'
__all__ = ('Part',)


class Part(_1951.DesignEntity):
    '''Part

    This is a mastapy class.
    '''

    TYPE = _PART

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Part.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def editable_name(self) -> 'str':
        '''str: 'EditableName' is the original name of this property.'''

        return self.wrapped.EditableName

    @editable_name.setter
    def editable_name(self, value: 'str'):
        self.wrapped.EditableName = str(value) if value else ''

    @property
    def unique_name(self) -> 'str':
        '''str: 'UniqueName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UniqueName

    @property
    def mass(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Mass' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Mass) if self.wrapped.Mass is not None else None

    @mass.setter
    def mass(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Mass = value

    @property
    def two_d_drawing(self) -> 'Image':
        '''Image: 'TwoDDrawing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.TwoDDrawing)
        return value

    @property
    def three_d_view_orientated_in_xy_plane_with_z_axis_pointing_out_of_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInXyPlaneWithZAxisPointingOutOfTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInXyPlaneWithZAxisPointingOutOfTheScreen)
        return value

    @property
    def three_d_view_orientated_in_xy_plane_with_z_axis_pointing_into_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInXyPlaneWithZAxisPointingIntoTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInXyPlaneWithZAxisPointingIntoTheScreen)
        return value

    @property
    def three_d_view_orientated_in_yz_plane_with_x_axis_pointing_into_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInYzPlaneWithXAxisPointingIntoTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInYzPlaneWithXAxisPointingIntoTheScreen)
        return value

    @property
    def three_d_view_orientated_in_yz_plane_with_x_axis_pointing_out_of_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInYzPlaneWithXAxisPointingOutOfTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInYzPlaneWithXAxisPointingOutOfTheScreen)
        return value

    @property
    def three_d_view_orientated_in_xz_plane_with_y_axis_pointing_into_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInXzPlaneWithYAxisPointingIntoTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInXzPlaneWithYAxisPointingIntoTheScreen)
        return value

    @property
    def three_d_view_orientated_in_xz_plane_with_y_axis_pointing_out_of_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInXzPlaneWithYAxisPointingOutOfTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInXzPlaneWithYAxisPointingOutOfTheScreen)
        return value

    @property
    def three_d_isometric_view(self) -> 'Image':
        '''Image: 'ThreeDIsometricView' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDIsometricView)
        return value

    @property
    def three_d_view(self) -> 'Image':
        '''Image: 'ThreeDView' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDView)
        return value

    @property
    def drawing_number(self) -> 'str':
        '''str: 'DrawingNumber' is the original name of this property.'''

        return self.wrapped.DrawingNumber

    @drawing_number.setter
    def drawing_number(self, value: 'str'):
        self.wrapped.DrawingNumber = str(value) if value else ''

    @property
    def mass_properties_from_design(self) -> '_1317.MassProperties':
        '''MassProperties: 'MassPropertiesFromDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1317.MassProperties)(self.wrapped.MassPropertiesFromDesign) if self.wrapped.MassPropertiesFromDesign is not None else None

    @property
    def mass_properties_from_design_including_planetary_duplicates(self) -> '_1317.MassProperties':
        '''MassProperties: 'MassPropertiesFromDesignIncludingPlanetaryDuplicates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1317.MassProperties)(self.wrapped.MassPropertiesFromDesignIncludingPlanetaryDuplicates) if self.wrapped.MassPropertiesFromDesignIncludingPlanetaryDuplicates is not None else None

    @property
    def connections(self) -> 'List[_2014.Connection]':
        '''List[Connection]: 'Connections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Connections, constructor.new(_2014.Connection))
        return value

    @property
    def local_connections(self) -> 'List[_2014.Connection]':
        '''List[Connection]: 'LocalConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LocalConnections, constructor.new(_2014.Connection))
        return value

    def create_geometry_export_options(self) -> '_1983.GeometryExportOptions':
        ''' 'CreateGeometryExportOptions' is the original name of this method.

        Returns:
            mastapy.system_model.import_export.GeometryExportOptions
        '''

        method_result = self.wrapped.CreateGeometryExportOptions()
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def copy_to(self, container: '_2176.Assembly') -> 'Part':
        ''' 'CopyTo' is the original name of this method.

        Args:
            container (mastapy.system_model.part_model.Assembly)

        Returns:
            mastapy.system_model.part_model.Part
        '''

        method_result = self.wrapped.CopyTo(container.wrapped if container else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def connections_to(self, part: 'Part') -> 'List[_2014.Connection]':
        ''' 'ConnectionsTo' is the original name of this method.

        Args:
            part (mastapy.system_model.part_model.Part)

        Returns:
            List[mastapy.system_model.connections_and_sockets.Connection]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionsTo(part.wrapped if part else None), constructor.new(_2014.Connection))

    def delete_connections(self):
        ''' 'DeleteConnections' is the original name of this method.'''

        self.wrapped.DeleteConnections()
