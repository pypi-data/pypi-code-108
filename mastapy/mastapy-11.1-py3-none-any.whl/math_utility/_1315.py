'''_1315.py

HarmonicValue
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_HARMONIC_VALUE = python_net_import('SMT.MastaAPI.MathUtility', 'HarmonicValue')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicValue',)


class HarmonicValue(_0.APIBase):
    '''HarmonicValue

    This is a mastapy class.
    '''

    TYPE = _HARMONIC_VALUE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicValue.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def harmonic_index(self) -> 'int':
        '''int: 'HarmonicIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HarmonicIndex

    @property
    def amplitude(self) -> 'float':
        '''float: 'Amplitude' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Amplitude

    @property
    def phase(self) -> 'float':
        '''float: 'Phase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Phase
