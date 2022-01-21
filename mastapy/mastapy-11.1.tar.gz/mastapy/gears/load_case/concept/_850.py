'''_850.py

ConceptMeshLoadCase
'''


from mastapy.gears.load_case import _835
from mastapy._internal.python_net import python_net_import

_CONCEPT_MESH_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Concept', 'ConceptMeshLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptMeshLoadCase',)


class ConceptMeshLoadCase(_835.MeshLoadCase):
    '''ConceptMeshLoadCase

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_MESH_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptMeshLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
