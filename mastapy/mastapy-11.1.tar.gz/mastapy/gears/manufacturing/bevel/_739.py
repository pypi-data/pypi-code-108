'''_739.py

ConicalMeshedGearManufacturingAnalysis
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CONICAL_MESHED_GEAR_MANUFACTURING_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'ConicalMeshedGearManufacturingAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalMeshedGearManufacturingAnalysis',)


class ConicalMeshedGearManufacturingAnalysis(_0.APIBase):
    '''ConicalMeshedGearManufacturingAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_MESHED_GEAR_MANUFACTURING_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalMeshedGearManufacturingAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def torque(self) -> 'float':
        '''float: 'Torque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Torque
