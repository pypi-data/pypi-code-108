'''_2179.py

AbstractShaftOrHousing
'''


from mastapy.system_model.part_model import _2186
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_OR_HOUSING = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'AbstractShaftOrHousing')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftOrHousing',)


class AbstractShaftOrHousing(_2186.Component):
    '''AbstractShaftOrHousing

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_OR_HOUSING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftOrHousing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
