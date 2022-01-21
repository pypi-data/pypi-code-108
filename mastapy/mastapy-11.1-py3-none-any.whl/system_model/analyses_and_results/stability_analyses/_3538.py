'''_3538.py

CriticalSpeed
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CRITICAL_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'CriticalSpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('CriticalSpeed',)


class CriticalSpeed(_0.APIBase):
    '''CriticalSpeed

    This is a mastapy class.
    '''

    TYPE = _CRITICAL_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CriticalSpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mode_index(self) -> 'int':
        '''int: 'ModeIndex' is the original name of this property.'''

        return self.wrapped.ModeIndex

    @mode_index.setter
    def mode_index(self, value: 'int'):
        self.wrapped.ModeIndex = int(value) if value else 0

    @property
    def shaft_harmonic_index(self) -> 'int':
        '''int: 'ShaftHarmonicIndex' is the original name of this property.'''

        return self.wrapped.ShaftHarmonicIndex

    @shaft_harmonic_index.setter
    def shaft_harmonic_index(self, value: 'int'):
        self.wrapped.ShaftHarmonicIndex = int(value) if value else 0

    @property
    def critical_speed_as_frequency(self) -> 'float':
        '''float: 'CriticalSpeedAsFrequency' is the original name of this property.'''

        return self.wrapped.CriticalSpeedAsFrequency

    @critical_speed_as_frequency.setter
    def critical_speed_as_frequency(self, value: 'float'):
        self.wrapped.CriticalSpeedAsFrequency = float(value) if value else 0.0

    @property
    def critical_speed_as_shaft_speed(self) -> 'float':
        '''float: 'CriticalSpeedAsShaftSpeed' is the original name of this property.'''

        return self.wrapped.CriticalSpeedAsShaftSpeed

    @critical_speed_as_shaft_speed.setter
    def critical_speed_as_shaft_speed(self, value: 'float'):
        self.wrapped.CriticalSpeedAsShaftSpeed = float(value) if value else 0.0
