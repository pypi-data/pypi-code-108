'''_131.py

GearMeshNodalComponent
'''


from mastapy.nodal_analysis.nodal_entities import _137
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_NODAL_COMPONENT = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'GearMeshNodalComponent')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshNodalComponent',)


class GearMeshNodalComponent(_137.NodalComposite):
    '''GearMeshNodalComponent

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_NODAL_COMPONENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshNodalComponent.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
