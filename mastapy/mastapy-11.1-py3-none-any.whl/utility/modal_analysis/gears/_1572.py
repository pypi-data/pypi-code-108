'''_1572.py

LabelOnlyOrder
'''


from mastapy.utility.modal_analysis.gears import _1573
from mastapy._internal.python_net import python_net_import

_LABEL_ONLY_ORDER = python_net_import('SMT.MastaAPI.Utility.ModalAnalysis.Gears', 'LabelOnlyOrder')


__docformat__ = 'restructuredtext en'
__all__ = ('LabelOnlyOrder',)


class LabelOnlyOrder(_1573.OrderForTE):
    '''LabelOnlyOrder

    This is a mastapy class.
    '''

    TYPE = _LABEL_ONLY_ORDER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LabelOnlyOrder.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
