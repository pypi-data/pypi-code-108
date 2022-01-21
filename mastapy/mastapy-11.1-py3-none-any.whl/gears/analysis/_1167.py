'''_1167.py

GearMeshImplementationAnalysis
'''


from mastapy.gears.analysis import _1166
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_IMPLEMENTATION_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.Analysis', 'GearMeshImplementationAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshImplementationAnalysis',)


class GearMeshImplementationAnalysis(_1166.GearMeshDesignAnalysis):
    '''GearMeshImplementationAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_IMPLEMENTATION_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshImplementationAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
