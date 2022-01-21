'''_2162.py

GearMeshFELink
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.fe import _2126
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.fe.links import _2164
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_FE_LINK = python_net_import('SMT.MastaAPI.SystemModel.FE.Links', 'GearMeshFELink')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshFELink',)


class GearMeshFELink(_2164.MultiAngleConnectionFELink):
    '''GearMeshFELink

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_FE_LINK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshFELink.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_active_mesh_node_for_reference_fe_substructure_node_for_misalignments(self) -> 'bool':
        '''bool: 'UseActiveMeshNodeForReferenceFESubstructureNodeForMisalignments' is the original name of this property.'''

        return self.wrapped.UseActiveMeshNodeForReferenceFESubstructureNodeForMisalignments

    @use_active_mesh_node_for_reference_fe_substructure_node_for_misalignments.setter
    def use_active_mesh_node_for_reference_fe_substructure_node_for_misalignments(self, value: 'bool'):
        self.wrapped.UseActiveMeshNodeForReferenceFESubstructureNodeForMisalignments = bool(value) if value else False

    @property
    def reference_fe_substructure_node_for_misalignments(self) -> 'list_with_selected_item.ListWithSelectedItem_FESubstructureNode':
        '''list_with_selected_item.ListWithSelectedItem_FESubstructureNode: 'ReferenceFESubstructureNodeForMisalignments' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_FESubstructureNode)(self.wrapped.ReferenceFESubstructureNodeForMisalignments) if self.wrapped.ReferenceFESubstructureNodeForMisalignments is not None else None

    @reference_fe_substructure_node_for_misalignments.setter
    def reference_fe_substructure_node_for_misalignments(self, value: 'list_with_selected_item.ListWithSelectedItem_FESubstructureNode.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_FESubstructureNode.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_FESubstructureNode.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.ReferenceFESubstructureNodeForMisalignments = value
