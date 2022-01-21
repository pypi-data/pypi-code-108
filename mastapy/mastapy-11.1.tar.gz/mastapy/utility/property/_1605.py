'''_1605.py

DutyCyclePropertySummary
'''


from typing import Generic, TypeVar

from mastapy import _0
from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_DUTY_CYCLE_PROPERTY_SUMMARY = python_net_import('SMT.MastaAPI.Utility.Property', 'DutyCyclePropertySummary')


__docformat__ = 'restructuredtext en'
__all__ = ('DutyCyclePropertySummary',)


TMeasurement = TypeVar('TMeasurement', bound='_1398.MeasurementBase')
T = TypeVar('T')


class DutyCyclePropertySummary(_0.APIBase, Generic[TMeasurement, T]):
    '''DutyCyclePropertySummary

    This is a mastapy class.

    Generic Types:
        TMeasurement
        T
    '''

    TYPE = _DUTY_CYCLE_PROPERTY_SUMMARY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DutyCyclePropertySummary.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
