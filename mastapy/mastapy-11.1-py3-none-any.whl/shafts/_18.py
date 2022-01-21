'''_18.py

ShaftAxialTorsionalComponentValues
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SHAFT_AXIAL_TORSIONAL_COMPONENT_VALUES = python_net_import('SMT.MastaAPI.Shafts', 'ShaftAxialTorsionalComponentValues')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftAxialTorsionalComponentValues',)


class ShaftAxialTorsionalComponentValues(_0.APIBase):
    '''ShaftAxialTorsionalComponentValues

    This is a mastapy class.
    '''

    TYPE = _SHAFT_AXIAL_TORSIONAL_COMPONENT_VALUES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftAxialTorsionalComponentValues.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def axial(self) -> 'float':
        '''float: 'Axial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Axial

    @property
    def torsional(self) -> 'float':
        '''float: 'Torsional' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Torsional
