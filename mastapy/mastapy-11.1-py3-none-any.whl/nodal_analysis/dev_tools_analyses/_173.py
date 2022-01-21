'''_173.py

NodeGroup
'''


from mastapy.nodal_analysis.dev_tools_analyses import _158
from mastapy._internal.python_net import python_net_import

_NODE_GROUP = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'NodeGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('NodeGroup',)


class NodeGroup(_158.FEEntityGroupInt):
    '''NodeGroup

    This is a mastapy class.
    '''

    TYPE = _NODE_GROUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NodeGroup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
