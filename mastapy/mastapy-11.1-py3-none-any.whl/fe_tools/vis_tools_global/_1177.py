'''_1177.py

ElementFace
'''


from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ELEMENT_FACE = python_net_import('SMT.MastaAPI.FETools.VisToolsGlobal', 'ElementFace')


__docformat__ = 'restructuredtext en'
__all__ = ('ElementFace',)


class ElementFace(_0.APIBase):
    '''ElementFace

    This is a mastapy class.
    '''

    TYPE = _ELEMENT_FACE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElementFace.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
