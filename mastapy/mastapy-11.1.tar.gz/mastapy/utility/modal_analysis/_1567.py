'''_1567.py

DesignEntityExcitationDescription
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DESIGN_ENTITY_EXCITATION_DESCRIPTION = python_net_import('SMT.MastaAPI.Utility.ModalAnalysis', 'DesignEntityExcitationDescription')


__docformat__ = 'restructuredtext en'
__all__ = ('DesignEntityExcitationDescription',)


class DesignEntityExcitationDescription(_0.APIBase):
    '''DesignEntityExcitationDescription

    This is a mastapy class.
    '''

    TYPE = _DESIGN_ENTITY_EXCITATION_DESCRIPTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DesignEntityExcitationDescription.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def harmonic_index(self) -> 'int':
        '''int: 'HarmonicIndex' is the original name of this property.'''

        return self.wrapped.HarmonicIndex

    @harmonic_index.setter
    def harmonic_index(self, value: 'int'):
        self.wrapped.HarmonicIndex = int(value) if value else 0

    @property
    def order(self) -> 'float':
        '''float: 'Order' is the original name of this property.'''

        return self.wrapped.Order

    @order.setter
    def order(self, value: 'float'):
        self.wrapped.Order = float(value) if value else 0.0

    @property
    def excitation_frequency(self) -> 'float':
        '''float: 'ExcitationFrequency' is the original name of this property.'''

        return self.wrapped.ExcitationFrequency

    @excitation_frequency.setter
    def excitation_frequency(self, value: 'float'):
        self.wrapped.ExcitationFrequency = float(value) if value else 0.0
