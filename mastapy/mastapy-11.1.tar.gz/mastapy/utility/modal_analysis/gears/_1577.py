'''_1577.py

ShaftOrderForTE
'''


from mastapy.utility.modal_analysis.gears import _1573
from mastapy._internal.python_net import python_net_import

_SHAFT_ORDER_FOR_TE = python_net_import('SMT.MastaAPI.Utility.ModalAnalysis.Gears', 'ShaftOrderForTE')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftOrderForTE',)


class ShaftOrderForTE(_1573.OrderForTE):
    '''ShaftOrderForTE

    This is a mastapy class.
    '''

    TYPE = _SHAFT_ORDER_FOR_TE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftOrderForTE.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
