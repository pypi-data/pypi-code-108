'''_17.py

ShaftAxialBendingXBendingYTorsionalComponentValues
'''


from mastapy._internal import constructor
from mastapy.shafts import _18
from mastapy._internal.python_net import python_net_import

_SHAFT_AXIAL_BENDING_X_BENDING_Y_TORSIONAL_COMPONENT_VALUES = python_net_import('SMT.MastaAPI.Shafts', 'ShaftAxialBendingXBendingYTorsionalComponentValues')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftAxialBendingXBendingYTorsionalComponentValues',)


class ShaftAxialBendingXBendingYTorsionalComponentValues(_18.ShaftAxialTorsionalComponentValues):
    '''ShaftAxialBendingXBendingYTorsionalComponentValues

    This is a mastapy class.
    '''

    TYPE = _SHAFT_AXIAL_BENDING_X_BENDING_Y_TORSIONAL_COMPONENT_VALUES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftAxialBendingXBendingYTorsionalComponentValues.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def bending_x(self) -> 'float':
        '''float: 'BendingX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingX

    @property
    def bending_y(self) -> 'float':
        '''float: 'BendingY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingY
