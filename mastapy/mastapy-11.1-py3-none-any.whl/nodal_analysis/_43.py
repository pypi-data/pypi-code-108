'''_43.py

AbstractLinearConnectionProperties
'''


from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ABSTRACT_LINEAR_CONNECTION_PROPERTIES = python_net_import('SMT.MastaAPI.NodalAnalysis', 'AbstractLinearConnectionProperties')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractLinearConnectionProperties',)


class AbstractLinearConnectionProperties(_0.APIBase):
    '''AbstractLinearConnectionProperties

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_LINEAR_CONNECTION_PROPERTIES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractLinearConnectionProperties.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
