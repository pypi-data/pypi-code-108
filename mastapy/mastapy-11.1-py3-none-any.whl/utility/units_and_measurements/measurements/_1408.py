'''_1408.py

AngleSmall
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ANGLE_SMALL = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'AngleSmall')


__docformat__ = 'restructuredtext en'
__all__ = ('AngleSmall',)


class AngleSmall(_1398.MeasurementBase):
    '''AngleSmall

    This is a mastapy class.
    '''

    TYPE = _ANGLE_SMALL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AngleSmall.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
