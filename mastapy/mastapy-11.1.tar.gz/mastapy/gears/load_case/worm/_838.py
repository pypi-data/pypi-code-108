'''_838.py

WormMeshLoadCase
'''


from mastapy.gears.load_case import _835
from mastapy._internal.python_net import python_net_import

_WORM_MESH_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Worm', 'WormMeshLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('WormMeshLoadCase',)


class WormMeshLoadCase(_835.MeshLoadCase):
    '''WormMeshLoadCase

    This is a mastapy class.
    '''

    TYPE = _WORM_MESH_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormMeshLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
