'''_1571.py

HarmonicOrderForTE
'''


from mastapy._internal import constructor
from mastapy.utility.modal_analysis.gears import _1573
from mastapy._internal.python_net import python_net_import

_HARMONIC_ORDER_FOR_TE = python_net_import('SMT.MastaAPI.Utility.ModalAnalysis.Gears', 'HarmonicOrderForTE')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicOrderForTE',)


class HarmonicOrderForTE(_1573.OrderForTE):
    '''HarmonicOrderForTE

    This is a mastapy class.
    '''

    TYPE = _HARMONIC_ORDER_FOR_TE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicOrderForTE.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def harmonic(self) -> 'int':
        '''int: 'Harmonic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Harmonic
