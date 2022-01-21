'''_2171.py

RollingRingConnectionFELink
'''


from mastapy.system_model.fe.links import _2164
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_CONNECTION_FE_LINK = python_net_import('SMT.MastaAPI.SystemModel.FE.Links', 'RollingRingConnectionFELink')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingConnectionFELink',)


class RollingRingConnectionFELink(_2164.MultiAngleConnectionFELink):
    '''RollingRingConnectionFELink

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_CONNECTION_FE_LINK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingConnectionFELink.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
