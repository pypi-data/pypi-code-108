'''_2322.py

ConceptCouplingHalf
'''


from mastapy.system_model.part_model.couplings import _2324
from mastapy._internal.python_net import python_net_import

_CONCEPT_COUPLING_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'ConceptCouplingHalf')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptCouplingHalf',)


class ConceptCouplingHalf(_2324.CouplingHalf):
    '''ConceptCouplingHalf

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_COUPLING_HALF

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptCouplingHalf.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
