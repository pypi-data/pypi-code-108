'''_2142.py

NodeGroupWithSelection
'''


from mastapy.system_model.fe import _2119
from mastapy.nodal_analysis.component_mode_synthesis import _200
from mastapy._internal.python_net import python_net_import

_NODE_GROUP_WITH_SELECTION = python_net_import('SMT.MastaAPI.SystemModel.FE', 'NodeGroupWithSelection')


__docformat__ = 'restructuredtext en'
__all__ = ('NodeGroupWithSelection',)


class NodeGroupWithSelection(_2119.FEEntityGroupWithSelection['_200.CMSNodeGroup', 'int']):
    '''NodeGroupWithSelection

    This is a mastapy class.
    '''

    TYPE = _NODE_GROUP_WITH_SELECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NodeGroupWithSelection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
