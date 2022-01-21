'''_1312.py

FourierSeries
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.math_utility import _1315
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FOURIER_SERIES = python_net_import('SMT.MastaAPI.MathUtility', 'FourierSeries')


__docformat__ = 'restructuredtext en'
__all__ = ('FourierSeries',)


class FourierSeries(_0.APIBase):
    '''FourierSeries

    This is a mastapy class.
    '''

    TYPE = _FOURIER_SERIES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FourierSeries.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''

    @property
    def unit(self) -> 'str':
        '''str: 'Unit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Unit

    @property
    def peakto_peak(self) -> 'float':
        '''float: 'PeaktoPeak' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PeaktoPeak

    @property
    def first_harmonic(self) -> '_1315.HarmonicValue':
        '''HarmonicValue: 'FirstHarmonic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1315.HarmonicValue)(self.wrapped.FirstHarmonic) if self.wrapped.FirstHarmonic is not None else None

    @property
    def second_harmonic(self) -> '_1315.HarmonicValue':
        '''HarmonicValue: 'SecondHarmonic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1315.HarmonicValue)(self.wrapped.SecondHarmonic) if self.wrapped.SecondHarmonic is not None else None

    @property
    def third_harmonic(self) -> '_1315.HarmonicValue':
        '''HarmonicValue: 'ThirdHarmonic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1315.HarmonicValue)(self.wrapped.ThirdHarmonic) if self.wrapped.ThirdHarmonic is not None else None

    @property
    def fourth_harmonic(self) -> '_1315.HarmonicValue':
        '''HarmonicValue: 'FourthHarmonic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1315.HarmonicValue)(self.wrapped.FourthHarmonic) if self.wrapped.FourthHarmonic is not None else None

    @property
    def fifth_harmonic(self) -> '_1315.HarmonicValue':
        '''HarmonicValue: 'FifthHarmonic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1315.HarmonicValue)(self.wrapped.FifthHarmonic) if self.wrapped.FifthHarmonic is not None else None

    @property
    def harmonics(self) -> 'List[_1315.HarmonicValue]':
        '''List[HarmonicValue]: 'Harmonics' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Harmonics, constructor.new(_1315.HarmonicValue))
        return value

    @property
    def harmonics_with_zeros_truncated(self) -> 'List[_1315.HarmonicValue]':
        '''List[HarmonicValue]: 'HarmonicsWithZerosTruncated' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HarmonicsWithZerosTruncated, constructor.new(_1315.HarmonicValue))
        return value

    @property
    def mean_value(self) -> 'float':
        '''float: 'MeanValue' is the original name of this property.'''

        return self.wrapped.MeanValue

    @mean_value.setter
    def mean_value(self, value: 'float'):
        self.wrapped.MeanValue = float(value) if value else 0.0

    @property
    def values(self) -> 'List[float]':
        '''List[float]: 'Values' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Values, float)
        return value

    def set_amplitude(self, harmonic: 'int', amplitude: 'float'):
        ''' 'SetAmplitude' is the original name of this method.

        Args:
            harmonic (int)
            amplitude (float)
        '''

        harmonic = int(harmonic)
        amplitude = float(amplitude)
        self.wrapped.SetAmplitude(harmonic if harmonic else 0, amplitude if amplitude else 0.0)

    def set_phase(self, harmonic: 'int', phase: 'float'):
        ''' 'SetPhase' is the original name of this method.

        Args:
            harmonic (int)
            phase (float)
        '''

        harmonic = int(harmonic)
        phase = float(phase)
        self.wrapped.SetPhase(harmonic if harmonic else 0, phase if phase else 0.0)
