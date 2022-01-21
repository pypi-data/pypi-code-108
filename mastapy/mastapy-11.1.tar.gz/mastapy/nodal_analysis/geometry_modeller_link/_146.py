'''_146.py

GeometryModellerDimensions
'''


from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEOMETRY_MODELLER_DIMENSIONS = python_net_import('SMT.MastaAPI.NodalAnalysis.GeometryModellerLink', 'GeometryModellerDimensions')


__docformat__ = 'restructuredtext en'
__all__ = ('GeometryModellerDimensions',)


class GeometryModellerDimensions(_0.APIBase):
    '''GeometryModellerDimensions

    This is a mastapy class.
    '''

    TYPE = _GEOMETRY_MODELLER_DIMENSIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GeometryModellerDimensions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
