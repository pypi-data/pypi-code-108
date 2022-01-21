'''_155.py

ElementFaceGroup
'''


from mastapy.nodal_analysis.dev_tools_analyses import _157
from mastapy.fe_tools.vis_tools_global import _1177
from mastapy._internal.python_net import python_net_import

_ELEMENT_FACE_GROUP = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'ElementFaceGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('ElementFaceGroup',)


class ElementFaceGroup(_157.FEEntityGroup['_1177.ElementFace']):
    '''ElementFaceGroup

    This is a mastapy class.
    '''

    TYPE = _ELEMENT_FACE_GROUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElementFaceGroup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
