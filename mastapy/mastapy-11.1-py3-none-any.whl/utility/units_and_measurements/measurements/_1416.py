'''_1416.py

AreaSmall
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_AREA_SMALL = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'AreaSmall')


__docformat__ = 'restructuredtext en'
__all__ = ('AreaSmall',)


class AreaSmall(_1398.MeasurementBase):
    '''AreaSmall

    This is a mastapy class.
    '''

    TYPE = _AREA_SMALL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AreaSmall.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
