'''_16.py

ShaftAxialBendingTorsionalComponentValues
'''


from mastapy._internal import constructor
from mastapy.shafts import _18
from mastapy._internal.python_net import python_net_import

_SHAFT_AXIAL_BENDING_TORSIONAL_COMPONENT_VALUES = python_net_import('SMT.MastaAPI.Shafts', 'ShaftAxialBendingTorsionalComponentValues')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftAxialBendingTorsionalComponentValues',)


class ShaftAxialBendingTorsionalComponentValues(_18.ShaftAxialTorsionalComponentValues):
    '''ShaftAxialBendingTorsionalComponentValues

    This is a mastapy class.
    '''

    TYPE = _SHAFT_AXIAL_BENDING_TORSIONAL_COMPONENT_VALUES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftAxialBendingTorsionalComponentValues.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def bending(self) -> 'float':
        '''float: 'Bending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Bending
