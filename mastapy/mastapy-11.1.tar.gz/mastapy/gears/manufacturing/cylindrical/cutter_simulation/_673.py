'''_673.py

ManufacturingOperationConstraints
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_MANUFACTURING_OPERATION_CONSTRAINTS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.CutterSimulation', 'ManufacturingOperationConstraints')


__docformat__ = 'restructuredtext en'
__all__ = ('ManufacturingOperationConstraints',)


class ManufacturingOperationConstraints(_0.APIBase):
    '''ManufacturingOperationConstraints

    This is a mastapy class.
    '''

    TYPE = _MANUFACTURING_OPERATION_CONSTRAINTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ManufacturingOperationConstraints.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_tip_clearance_factor(self) -> 'float':
        '''float: 'GearTipClearanceFactor' is the original name of this property.'''

        return self.wrapped.GearTipClearanceFactor

    @gear_tip_clearance_factor.setter
    def gear_tip_clearance_factor(self, value: 'float'):
        self.wrapped.GearTipClearanceFactor = float(value) if value else 0.0

    @property
    def gear_root_clearance_factor(self) -> 'float':
        '''float: 'GearRootClearanceFactor' is the original name of this property.'''

        return self.wrapped.GearRootClearanceFactor

    @gear_root_clearance_factor.setter
    def gear_root_clearance_factor(self, value: 'float'):
        self.wrapped.GearRootClearanceFactor = float(value) if value else 0.0
