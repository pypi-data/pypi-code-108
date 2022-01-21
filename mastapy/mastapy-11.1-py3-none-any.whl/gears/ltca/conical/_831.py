'''_831.py

ConicalMeshLoadDistributionAtRotation
'''


from mastapy.gears.ltca import _802
from mastapy._internal.python_net import python_net_import

_CONICAL_MESH_LOAD_DISTRIBUTION_AT_ROTATION = python_net_import('SMT.MastaAPI.Gears.LTCA.Conical', 'ConicalMeshLoadDistributionAtRotation')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalMeshLoadDistributionAtRotation',)


class ConicalMeshLoadDistributionAtRotation(_802.GearMeshLoadDistributionAtRotation):
    '''ConicalMeshLoadDistributionAtRotation

    This is a mastapy class.
    '''

    TYPE = _CONICAL_MESH_LOAD_DISTRIBUTION_AT_ROTATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalMeshLoadDistributionAtRotation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
