'''_1484.py

RescaledMeasurement
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_RESCALED_MEASUREMENT = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'RescaledMeasurement')


__docformat__ = 'restructuredtext en'
__all__ = ('RescaledMeasurement',)


class RescaledMeasurement(_1398.MeasurementBase):
    '''RescaledMeasurement

    This is a mastapy class.
    '''

    TYPE = _RESCALED_MEASUREMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RescaledMeasurement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
