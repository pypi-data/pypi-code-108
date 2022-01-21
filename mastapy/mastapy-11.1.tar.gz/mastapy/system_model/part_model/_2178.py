'''_2178.py

AbstractShaft
'''


from mastapy.system_model.part_model import _2179
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'AbstractShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaft',)


class AbstractShaft(_2179.AbstractShaftOrHousing):
    '''AbstractShaft

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
