'''_1479.py

PressureVelocityProduct
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_PRESSURE_VELOCITY_PRODUCT = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'PressureVelocityProduct')


__docformat__ = 'restructuredtext en'
__all__ = ('PressureVelocityProduct',)


class PressureVelocityProduct(_1398.MeasurementBase):
    '''PressureVelocityProduct

    This is a mastapy class.
    '''

    TYPE = _PRESSURE_VELOCITY_PRODUCT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PressureVelocityProduct.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
