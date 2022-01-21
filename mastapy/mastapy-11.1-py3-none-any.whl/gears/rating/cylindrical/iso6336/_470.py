'''_470.py

CylindricalGearToothFatigueFractureResultsN1457
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.utility_gui.charts import _1624
from mastapy.gears.rating.cylindrical.iso6336 import _491, _488
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_TOOTH_FATIGUE_FRACTURE_RESULTS_N1457 = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'CylindricalGearToothFatigueFractureResultsN1457')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearToothFatigueFractureResultsN1457',)


class CylindricalGearToothFatigueFractureResultsN1457(_0.APIBase):
    '''CylindricalGearToothFatigueFractureResultsN1457

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_TOOTH_FATIGUE_FRACTURE_RESULTS_N1457

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearToothFatigueFractureResultsN1457.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_fatigue_damage(self) -> 'float':
        '''float: 'MaximumFatigueDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumFatigueDamage

    @property
    def fatigue_damage_chart(self) -> '_1624.ThreeDChartDefinition':
        '''ThreeDChartDefinition: 'FatigueDamageChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1624.ThreeDChartDefinition)(self.wrapped.FatigueDamageChart) if self.wrapped.FatigueDamageChart is not None else None

    @property
    def critical_section(self) -> '_491.ToothFlankFractureAnalysisRowN1457':
        '''ToothFlankFractureAnalysisRowN1457: 'CriticalSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_491.ToothFlankFractureAnalysisRowN1457)(self.wrapped.CriticalSection) if self.wrapped.CriticalSection is not None else None

    @property
    def analysis_rows(self) -> 'List[_491.ToothFlankFractureAnalysisRowN1457]':
        '''List[ToothFlankFractureAnalysisRowN1457]: 'AnalysisRows' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AnalysisRows, constructor.new(_491.ToothFlankFractureAnalysisRowN1457))
        return value

    @property
    def contact_points(self) -> 'List[_488.ToothFlankFractureAnalysisContactPointN1457]':
        '''List[ToothFlankFractureAnalysisContactPointN1457]: 'ContactPoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ContactPoints, constructor.new(_488.ToothFlankFractureAnalysisContactPointN1457))
        return value
