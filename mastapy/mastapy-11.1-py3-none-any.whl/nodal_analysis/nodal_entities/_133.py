'''_133.py

GearMeshPointOnFlankContact
'''


from mastapy.nodal_analysis.nodal_entities import _145
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_POINT_ON_FLANK_CONTACT = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'GearMeshPointOnFlankContact')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshPointOnFlankContact',)


class GearMeshPointOnFlankContact(_145.TwoBodyConnectionNodalComponent):
    '''GearMeshPointOnFlankContact

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_POINT_ON_FLANK_CONTACT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshPointOnFlankContact.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
