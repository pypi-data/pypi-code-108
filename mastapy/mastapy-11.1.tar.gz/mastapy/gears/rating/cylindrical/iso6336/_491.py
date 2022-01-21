'''_491.py

ToothFlankFractureAnalysisRowN1457
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.rating.cylindrical.iso6336 import _490, _488
from mastapy._internal.python_net import python_net_import

_TOOTH_FLANK_FRACTURE_ANALYSIS_ROW_N1457 = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ToothFlankFractureAnalysisRowN1457')


__docformat__ = 'restructuredtext en'
__all__ = ('ToothFlankFractureAnalysisRowN1457',)


class ToothFlankFractureAnalysisRowN1457(_488.ToothFlankFractureAnalysisContactPointN1457):
    '''ToothFlankFractureAnalysisRowN1457

    This is a mastapy class.
    '''

    TYPE = _TOOTH_FLANK_FRACTURE_ANALYSIS_ROW_N1457

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ToothFlankFractureAnalysisRowN1457.TYPE'):
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
    def analysis_point_with_maximum_fatigue_damage(self) -> '_490.ToothFlankFractureAnalysisPointN1457':
        '''ToothFlankFractureAnalysisPointN1457: 'AnalysisPointWithMaximumFatigueDamage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_490.ToothFlankFractureAnalysisPointN1457)(self.wrapped.AnalysisPointWithMaximumFatigueDamage) if self.wrapped.AnalysisPointWithMaximumFatigueDamage is not None else None

    @property
    def watch_points(self) -> 'List[_490.ToothFlankFractureAnalysisPointN1457]':
        '''List[ToothFlankFractureAnalysisPointN1457]: 'WatchPoints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WatchPoints, constructor.new(_490.ToothFlankFractureAnalysisPointN1457))
        return value
