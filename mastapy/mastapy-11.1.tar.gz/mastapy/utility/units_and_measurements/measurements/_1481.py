'''_1481.py

Price
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_PRICE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Price')


__docformat__ = 'restructuredtext en'
__all__ = ('Price',)


class Price(_1398.MeasurementBase):
    '''Price

    This is a mastapy class.
    '''

    TYPE = _PRICE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Price.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
