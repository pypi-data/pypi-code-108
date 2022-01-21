'''_1429.py

Force
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_FORCE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Force')


__docformat__ = 'restructuredtext en'
__all__ = ('Force',)


class Force(_1398.MeasurementBase):
    '''Force

    This is a mastapy class.
    '''

    TYPE = _FORCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Force.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
