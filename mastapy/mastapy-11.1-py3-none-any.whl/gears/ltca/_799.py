'''_799.py

GearFilletNodeStressResultsRow
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.ltca import _797
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_FILLET_NODE_STRESS_RESULTS_ROW = python_net_import('SMT.MastaAPI.Gears.LTCA', 'GearFilletNodeStressResultsRow')


__docformat__ = 'restructuredtext en'
__all__ = ('GearFilletNodeStressResultsRow',)


class GearFilletNodeStressResultsRow(_0.APIBase):
    '''GearFilletNodeStressResultsRow

    This is a mastapy class.
    '''

    TYPE = _GEAR_FILLET_NODE_STRESS_RESULTS_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearFilletNodeStressResultsRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def fillet_row_index(self) -> 'int':
        '''int: 'FilletRowIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FilletRowIndex

    @property
    def node_results(self) -> 'List[_797.GearFilletNodeStressResults]':
        '''List[GearFilletNodeStressResults]: 'NodeResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.NodeResults, constructor.new(_797.GearFilletNodeStressResults))
        return value
