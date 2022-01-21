'''_1861.py

InterferenceComponents
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_INTERFERENCE_COMPONENTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.Fitting', 'InterferenceComponents')


__docformat__ = 'restructuredtext en'
__all__ = ('InterferenceComponents',)


class InterferenceComponents(_0.APIBase):
    '''InterferenceComponents

    This is a mastapy class.
    '''

    TYPE = _INTERFERENCE_COMPONENTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InterferenceComponents.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def nominal_interfacial_interference(self) -> 'float':
        '''float: 'NominalInterfacialInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalInterfacialInterference

    @property
    def reduction_in_interference_from_centrifugal_effects(self) -> 'float':
        '''float: 'ReductionInInterferenceFromCentrifugalEffects' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReductionInInterferenceFromCentrifugalEffects

    @property
    def total_interfacial_interference(self) -> 'float':
        '''float: 'TotalInterfacialInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalInterfacialInterference

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
