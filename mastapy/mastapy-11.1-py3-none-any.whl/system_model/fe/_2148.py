'''_2148.py

RaceBearingFESystemDeflection
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RACE_BEARING_FE_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.FE', 'RaceBearingFESystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('RaceBearingFESystemDeflection',)


class RaceBearingFESystemDeflection(_0.APIBase):
    '''RaceBearingFESystemDeflection

    This is a mastapy class.
    '''

    TYPE = _RACE_BEARING_FE_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RaceBearingFESystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
