'''_1461.py

LinearStiffness
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_LINEAR_STIFFNESS = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'LinearStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('LinearStiffness',)


class LinearStiffness(_1398.MeasurementBase):
    '''LinearStiffness

    This is a mastapy class.
    '''

    TYPE = _LINEAR_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LinearStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
