'''_27.py

ShaftPointStressCycle
'''


from mastapy.shafts import _26, _41
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SHAFT_POINT_STRESS_CYCLE = python_net_import('SMT.MastaAPI.Shafts', 'ShaftPointStressCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftPointStressCycle',)


class ShaftPointStressCycle(_0.APIBase):
    '''ShaftPointStressCycle

    This is a mastapy class.
    '''

    TYPE = _SHAFT_POINT_STRESS_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftPointStressCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def stress_mean(self) -> '_26.ShaftPointStress':
        '''ShaftPointStress: 'StressMean' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_26.ShaftPointStress)(self.wrapped.StressMean) if self.wrapped.StressMean is not None else None

    @property
    def stress_amplitude(self) -> '_26.ShaftPointStress':
        '''ShaftPointStress: 'StressAmplitude' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_26.ShaftPointStress)(self.wrapped.StressAmplitude) if self.wrapped.StressAmplitude is not None else None

    @property
    def stress_total(self) -> '_26.ShaftPointStress':
        '''ShaftPointStress: 'StressTotal' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_26.ShaftPointStress)(self.wrapped.StressTotal) if self.wrapped.StressTotal is not None else None

    @property
    def din743201212_comparative_mean_stress(self) -> '_41.StressMeasurementShaftAxialBendingTorsionalComponentValues':
        '''StressMeasurementShaftAxialBendingTorsionalComponentValues: 'DIN743201212ComparativeMeanStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_41.StressMeasurementShaftAxialBendingTorsionalComponentValues)(self.wrapped.DIN743201212ComparativeMeanStress) if self.wrapped.DIN743201212ComparativeMeanStress is not None else None
