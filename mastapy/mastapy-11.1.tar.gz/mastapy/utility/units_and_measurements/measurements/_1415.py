'''_1415.py

Area
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_AREA = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Area')


__docformat__ = 'restructuredtext en'
__all__ = ('Area',)


class Area(_1398.MeasurementBase):
    '''Area

    This is a mastapy class.
    '''

    TYPE = _AREA

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Area.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
