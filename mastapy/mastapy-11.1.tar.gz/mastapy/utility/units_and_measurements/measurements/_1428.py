'''_1428.py

FlowRate
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_FLOW_RATE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'FlowRate')


__docformat__ = 'restructuredtext en'
__all__ = ('FlowRate',)


class FlowRate(_1398.MeasurementBase):
    '''FlowRate

    This is a mastapy class.
    '''

    TYPE = _FLOW_RATE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FlowRate.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
