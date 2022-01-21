'''_2352.py

ActiveFESubstructureSelectionGroup
'''


from mastapy.system_model.part_model.configurations import _2357, _2351
from mastapy.system_model.part_model import _2194
from mastapy.system_model.fe import _2124
from mastapy._internal.python_net import python_net_import

_ACTIVE_FE_SUBSTRUCTURE_SELECTION_GROUP = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Configurations', 'ActiveFESubstructureSelectionGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('ActiveFESubstructureSelectionGroup',)


class ActiveFESubstructureSelectionGroup(_2357.PartDetailConfiguration['_2351.ActiveFESubstructureSelection', '_2194.FEPart', '_2124.FESubstructure']):
    '''ActiveFESubstructureSelectionGroup

    This is a mastapy class.
    '''

    TYPE = _ACTIVE_FE_SUBSTRUCTURE_SELECTION_GROUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ActiveFESubstructureSelectionGroup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
