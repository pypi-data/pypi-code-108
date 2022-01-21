'''_198.py

CMSElementFaceGroupOfAllFreeFaces
'''


from mastapy.nodal_analysis.component_mode_synthesis import _197
from mastapy._internal.python_net import python_net_import

_CMS_ELEMENT_FACE_GROUP_OF_ALL_FREE_FACES = python_net_import('SMT.MastaAPI.NodalAnalysis.ComponentModeSynthesis', 'CMSElementFaceGroupOfAllFreeFaces')


__docformat__ = 'restructuredtext en'
__all__ = ('CMSElementFaceGroupOfAllFreeFaces',)


class CMSElementFaceGroupOfAllFreeFaces(_197.CMSElementFaceGroup):
    '''CMSElementFaceGroupOfAllFreeFaces

    This is a mastapy class.
    '''

    TYPE = _CMS_ELEMENT_FACE_GROUP_OF_ALL_FREE_FACES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CMSElementFaceGroupOfAllFreeFaces.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
