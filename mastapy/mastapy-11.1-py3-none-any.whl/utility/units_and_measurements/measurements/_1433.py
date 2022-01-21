'''_1433.py

FractionMeasurementBase
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_FRACTION_MEASUREMENT_BASE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'FractionMeasurementBase')


__docformat__ = 'restructuredtext en'
__all__ = ('FractionMeasurementBase',)


class FractionMeasurementBase(_1398.MeasurementBase):
    '''FractionMeasurementBase

    This is a mastapy class.
    '''

    TYPE = _FRACTION_MEASUREMENT_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FractionMeasurementBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
