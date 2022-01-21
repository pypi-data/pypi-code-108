'''_156.py

ElementGroup
'''


from mastapy.nodal_analysis.dev_tools_analyses import _158
from mastapy._internal.python_net import python_net_import

_ELEMENT_GROUP = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'ElementGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('ElementGroup',)


class ElementGroup(_158.FEEntityGroupInt):
    '''ElementGroup

    This is a mastapy class.
    '''

    TYPE = _ELEMENT_GROUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElementGroup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
