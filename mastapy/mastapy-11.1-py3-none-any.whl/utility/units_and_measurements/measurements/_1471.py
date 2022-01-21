'''_1471.py

PowerPerSmallArea
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_POWER_PER_SMALL_AREA = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'PowerPerSmallArea')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerPerSmallArea',)


class PowerPerSmallArea(_1398.MeasurementBase):
    '''PowerPerSmallArea

    This is a mastapy class.
    '''

    TYPE = _POWER_PER_SMALL_AREA

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerPerSmallArea.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
