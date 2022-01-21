'''_852.py

BevelMeshLoadCase
'''


from mastapy.gears.load_case.conical import _847
from mastapy._internal.python_net import python_net_import

_BEVEL_MESH_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Bevel', 'BevelMeshLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelMeshLoadCase',)


class BevelMeshLoadCase(_847.ConicalMeshLoadCase):
    '''BevelMeshLoadCase

    This is a mastapy class.
    '''

    TYPE = _BEVEL_MESH_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelMeshLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
