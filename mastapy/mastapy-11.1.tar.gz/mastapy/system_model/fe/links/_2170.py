'''_2170.py

PointLoadFELink
'''


from mastapy.system_model.fe.links import _2166
from mastapy._internal.python_net import python_net_import

_POINT_LOAD_FE_LINK = python_net_import('SMT.MastaAPI.SystemModel.FE.Links', 'PointLoadFELink')


__docformat__ = 'restructuredtext en'
__all__ = ('PointLoadFELink',)


class PointLoadFELink(_2166.MultiNodeFELink):
    '''PointLoadFELink

    This is a mastapy class.
    '''

    TYPE = _POINT_LOAD_FE_LINK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PointLoadFELink.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
