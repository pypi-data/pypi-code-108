'''_2186.py

Component
'''


from typing import List, Optional

from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._math.vector_3d import Vector3D
from mastapy.math_utility import _1297, _1298
from mastapy.system_model.connections_and_sockets import (
    _2012, _2033, _2014, _2038
)
from mastapy.system_model.part_model import _2187, _2209
from mastapy._internal.python_net import python_net_import

_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'Socket')
_COMPONENT = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Component')


__docformat__ = 'restructuredtext en'
__all__ = ('Component',)


class Component(_2209.Part):
    '''Component

    This is a mastapy class.
    '''

    TYPE = _COMPONENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Component.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def length(self) -> 'float':
        '''float: 'Length' is the original name of this property.'''

        return self.wrapped.Length

    @length.setter
    def length(self, value: 'float'):
        self.wrapped.Length = float(value) if value else 0.0

    @property
    def polar_inertia_for_synchroniser_sizing_only(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PolarInertiaForSynchroniserSizingOnly' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PolarInertiaForSynchroniserSizingOnly) if self.wrapped.PolarInertiaForSynchroniserSizingOnly is not None else None

    @polar_inertia_for_synchroniser_sizing_only.setter
    def polar_inertia_for_synchroniser_sizing_only(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PolarInertiaForSynchroniserSizingOnly = value

    @property
    def polar_inertia(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PolarInertia' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PolarInertia) if self.wrapped.PolarInertia is not None else None

    @polar_inertia.setter
    def polar_inertia(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PolarInertia = value

    @property
    def transverse_inertia(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TransverseInertia' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TransverseInertia) if self.wrapped.TransverseInertia is not None else None

    @transverse_inertia.setter
    def transverse_inertia(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.TransverseInertia = value

    @property
    def x_axis(self) -> 'str':
        '''str: 'XAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.XAxis

    @property
    def y_axis(self) -> 'str':
        '''str: 'YAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.YAxis

    @property
    def z_axis(self) -> 'str':
        '''str: 'ZAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ZAxis

    @property
    def translation(self) -> 'str':
        '''str: 'Translation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Translation

    @property
    def reason_mass_properties_are_unknown(self) -> 'str':
        '''str: 'ReasonMassPropertiesAreUnknown' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReasonMassPropertiesAreUnknown

    @property
    def reason_mass_properties_are_zero(self) -> 'str':
        '''str: 'ReasonMassPropertiesAreZero' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReasonMassPropertiesAreZero

    @property
    def additional_modal_damping_ratio(self) -> 'float':
        '''float: 'AdditionalModalDampingRatio' is the original name of this property.'''

        return self.wrapped.AdditionalModalDampingRatio

    @additional_modal_damping_ratio.setter
    def additional_modal_damping_ratio(self, value: 'float'):
        self.wrapped.AdditionalModalDampingRatio = float(value) if value else 0.0

    @property
    def two_d_drawing_full_model(self) -> 'Image':
        '''Image: 'TwoDDrawingFullModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.TwoDDrawingFullModel)
        return value

    @property
    def coordinate_system_euler_angles(self) -> 'Vector3D':
        '''Vector3D: 'CoordinateSystemEulerAngles' is the original name of this property.'''

        value = conversion.pn_to_mp_vector3d(self.wrapped.CoordinateSystemEulerAngles)
        return value

    @coordinate_system_euler_angles.setter
    def coordinate_system_euler_angles(self, value: 'Vector3D'):
        value = value if value else None
        value = conversion.mp_to_pn_vector3d(value)
        self.wrapped.CoordinateSystemEulerAngles = value

    @property
    def position(self) -> 'Vector3D':
        '''Vector3D: 'Position' is the original name of this property.'''

        value = conversion.pn_to_mp_vector3d(self.wrapped.Position)
        return value

    @position.setter
    def position(self, value: 'Vector3D'):
        value = value if value else None
        value = conversion.mp_to_pn_vector3d(value)
        self.wrapped.Position = value

    @property
    def local_coordinate_system(self) -> '_1297.CoordinateSystem3D':
        '''CoordinateSystem3D: 'LocalCoordinateSystem' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1297.CoordinateSystem3D)(self.wrapped.LocalCoordinateSystem) if self.wrapped.LocalCoordinateSystem is not None else None

    @property
    def component_connections(self) -> 'List[_2012.ComponentConnection]':
        '''List[ComponentConnection]: 'ComponentConnections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentConnections, constructor.new(_2012.ComponentConnection))
        return value

    @property
    def translation_vector(self) -> 'Vector3D':
        '''Vector3D: 'TranslationVector' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.TranslationVector)
        return value

    @property
    def centre_offset(self) -> 'float':
        '''float: 'CentreOffset' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CentreOffset

    @property
    def available_socket_offsets(self) -> 'List[str]':
        '''List[str]: 'AvailableSocketOffsets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AvailableSocketOffsets, str)
        return value

    @property
    def x_axis_vector(self) -> 'Vector3D':
        '''Vector3D: 'XAxisVector' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.XAxisVector)
        return value

    @property
    def y_axis_vector(self) -> 'Vector3D':
        '''Vector3D: 'YAxisVector' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.YAxisVector)
        return value

    @property
    def z_axis_vector(self) -> 'Vector3D':
        '''Vector3D: 'ZAxisVector' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.ZAxisVector)
        return value

    def move_along_axis(self, delta: 'float'):
        ''' 'MoveAlongAxis' is the original name of this method.

        Args:
            delta (float)
        '''

        delta = float(delta)
        self.wrapped.MoveAlongAxis(delta if delta else 0.0)

    def set_position_and_axis_of_component_and_connected_components(self, origin: 'Vector3D', z_axis: 'Vector3D') -> '_2033.RealignmentResult':
        ''' 'SetPositionAndAxisOfComponentAndConnectedComponents' is the original name of this method.

        Args:
            origin (Vector3D)
            z_axis (Vector3D)

        Returns:
            mastapy.system_model.connections_and_sockets.RealignmentResult
        '''

        origin = conversion.mp_to_pn_vector3d(origin)
        z_axis = conversion.mp_to_pn_vector3d(z_axis)
        method_result = self.wrapped.SetPositionAndAxisOfComponentAndConnectedComponents(origin, z_axis)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def set_position_and_rotation_of_component_and_connected_components(self, new_coordinate_system: '_1297.CoordinateSystem3D') -> '_2033.RealignmentResult':
        ''' 'SetPositionAndRotationOfComponentAndConnectedComponents' is the original name of this method.

        Args:
            new_coordinate_system (mastapy.math_utility.CoordinateSystem3D)

        Returns:
            mastapy.system_model.connections_and_sockets.RealignmentResult
        '''

        method_result = self.wrapped.SetPositionAndRotationOfComponentAndConnectedComponents(new_coordinate_system.wrapped if new_coordinate_system else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def set_position_of_component_and_connected_components(self, position: 'Vector3D') -> '_2033.RealignmentResult':
        ''' 'SetPositionOfComponentAndConnectedComponents' is the original name of this method.

        Args:
            position (Vector3D)

        Returns:
            mastapy.system_model.connections_and_sockets.RealignmentResult
        '''

        position = conversion.mp_to_pn_vector3d(position)
        method_result = self.wrapped.SetPositionOfComponentAndConnectedComponents(position)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def create_coordinate_system_editor(self) -> '_1298.CoordinateSystemEditor':
        ''' 'CreateCoordinateSystemEditor' is the original name of this method.

        Returns:
            mastapy.math_utility.CoordinateSystemEditor
        '''

        method_result = self.wrapped.CreateCoordinateSystemEditor()
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def can_delete_connection(self, connection: '_2014.Connection') -> 'bool':
        ''' 'CanDeleteConnection' is the original name of this method.

        Args:
            connection (mastapy.system_model.connections_and_sockets.Connection)

        Returns:
            bool
        '''

        method_result = self.wrapped.CanDeleteConnection(connection.wrapped if connection else None)
        return method_result

    def socket_named(self, socket_name: 'str') -> '_2038.Socket':
        ''' 'SocketNamed' is the original name of this method.

        Args:
            socket_name (str)

        Returns:
            mastapy.system_model.connections_and_sockets.Socket
        '''

        socket_name = str(socket_name)
        method_result = self.wrapped.SocketNamed(socket_name if socket_name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def move_all_concentric_parts_radially(self, delta_x: 'float', delta_y: 'float') -> 'bool':
        ''' 'MoveAllConcentricPartsRadially' is the original name of this method.

        Args:
            delta_x (float)
            delta_y (float)

        Returns:
            bool
        '''

        delta_x = float(delta_x)
        delta_y = float(delta_y)
        method_result = self.wrapped.MoveAllConcentricPartsRadially(delta_x if delta_x else 0.0, delta_y if delta_y else 0.0)
        return method_result

    def move_with_concentric_parts_to_new_origin(self, target_origin: 'Vector3D') -> 'bool':
        ''' 'MoveWithConcentricPartsToNewOrigin' is the original name of this method.

        Args:
            target_origin (Vector3D)

        Returns:
            bool
        '''

        target_origin = conversion.mp_to_pn_vector3d(target_origin)
        method_result = self.wrapped.MoveWithConcentricPartsToNewOrigin(target_origin)
        return method_result

    def diameter_at_middle_of_connection(self, connection: '_2014.Connection') -> 'float':
        ''' 'DiameterAtMiddleOfConnection' is the original name of this method.

        Args:
            connection (mastapy.system_model.connections_and_sockets.Connection)

        Returns:
            float
        '''

        method_result = self.wrapped.DiameterAtMiddleOfConnection(connection.wrapped if connection else None)
        return method_result

    def diameter_of_socket_for(self, connection: '_2014.Connection') -> 'float':
        ''' 'DiameterOfSocketFor' is the original name of this method.

        Args:
            connection (mastapy.system_model.connections_and_sockets.Connection)

        Returns:
            float
        '''

        method_result = self.wrapped.DiameterOfSocketFor(connection.wrapped if connection else None)
        return method_result

    def is_directly_connected_to(self, component: 'Component') -> 'bool':
        ''' 'IsDirectlyConnectedTo' is the original name of this method.

        Args:
            component (mastapy.system_model.part_model.Component)

        Returns:
            bool
        '''

        method_result = self.wrapped.IsDirectlyConnectedTo(component.wrapped if component else None)
        return method_result

    def is_directly_or_indirectly_connected_to(self, component: 'Component') -> 'bool':
        ''' 'IsDirectlyOrIndirectlyConnectedTo' is the original name of this method.

        Args:
            component (mastapy.system_model.part_model.Component)

        Returns:
            bool
        '''

        method_result = self.wrapped.IsDirectlyOrIndirectlyConnectedTo(component.wrapped if component else None)
        return method_result

    def is_coaxially_connected_to(self, component: 'Component') -> 'bool':
        ''' 'IsCoaxiallyConnectedTo' is the original name of this method.

        Args:
            component (mastapy.system_model.part_model.Component)

        Returns:
            bool
        '''

        method_result = self.wrapped.IsCoaxiallyConnectedTo(component.wrapped if component else None)
        return method_result

    def can_connect_to(self, component: 'Component') -> 'bool':
        ''' 'CanConnectTo' is the original name of this method.

        Args:
            component (mastapy.system_model.part_model.Component)

        Returns:
            bool
        '''

        method_result = self.wrapped.CanConnectTo(component.wrapped if component else None)
        return method_result

    def possible_sockets_to_connect_with(self, socket: '_2038.Socket') -> 'List[_2038.Socket]':
        ''' 'PossibleSocketsToConnectWith' is the original name of this method.

        Args:
            socket (mastapy.system_model.connections_and_sockets.Socket)

        Returns:
            List[mastapy.system_model.connections_and_sockets.Socket]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.PossibleSocketsToConnectWith.Overloads[_SOCKET](socket.wrapped if socket else None), constructor.new(_2038.Socket))

    def connect_to_socket(self, socket: '_2038.Socket') -> '_2187.ComponentsConnectedResult':
        ''' 'ConnectTo' is the original name of this method.

        Args:
            socket (mastapy.system_model.connections_and_sockets.Socket)

        Returns:
            mastapy.system_model.part_model.ComponentsConnectedResult
        '''

        method_result = self.wrapped.ConnectTo.Overloads[_SOCKET](socket.wrapped if socket else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def possible_sockets_to_connect_with_component(self, component: 'Component') -> 'List[_2038.Socket]':
        ''' 'PossibleSocketsToConnectWith' is the original name of this method.

        Args:
            component (mastapy.system_model.part_model.Component)

        Returns:
            List[mastapy.system_model.connections_and_sockets.Socket]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.PossibleSocketsToConnectWith.Overloads[_COMPONENT](component.wrapped if component else None), constructor.new(_2038.Socket))

    def try_connect_to(self, component: 'Component', hint_offset: Optional['float'] = float('nan')) -> '_2187.ComponentsConnectedResult':
        ''' 'TryConnectTo' is the original name of this method.

        Args:
            component (mastapy.system_model.part_model.Component)
            hint_offset (float, optional)

        Returns:
            mastapy.system_model.part_model.ComponentsConnectedResult
        '''

        hint_offset = float(hint_offset)
        method_result = self.wrapped.TryConnectTo(component.wrapped if component else None, hint_offset if hint_offset else 0.0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def connect_to(self, component: 'Component') -> '_2187.ComponentsConnectedResult':
        ''' 'ConnectTo' is the original name of this method.

        Args:
            component (mastapy.system_model.part_model.Component)

        Returns:
            mastapy.system_model.part_model.ComponentsConnectedResult
        '''

        method_result = self.wrapped.ConnectTo.Overloads[_COMPONENT](component.wrapped if component else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
