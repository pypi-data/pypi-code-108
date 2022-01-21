'''_426.py

CylindricalGearScuffingResults
'''


from typing import List

from mastapy.gears.rating.cylindrical import _445
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SCUFFING_RESULTS = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'CylindricalGearScuffingResults')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearScuffingResults',)


class CylindricalGearScuffingResults(_0.APIBase):
    '''CylindricalGearScuffingResults

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SCUFFING_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearScuffingResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def scuffing_results_row(self) -> 'List[_445.ScuffingResultsRow]':
        '''List[ScuffingResultsRow]: 'ScuffingResultsRow' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ScuffingResultsRow, constructor.new(_445.ScuffingResultsRow))
        return value
