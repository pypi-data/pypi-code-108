'''_798.py

GearFilletNodeStressResultsColumn
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.ltca import _797
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_FILLET_NODE_STRESS_RESULTS_COLUMN = python_net_import('SMT.MastaAPI.Gears.LTCA', 'GearFilletNodeStressResultsColumn')


__docformat__ = 'restructuredtext en'
__all__ = ('GearFilletNodeStressResultsColumn',)


class GearFilletNodeStressResultsColumn(_0.APIBase):
    '''GearFilletNodeStressResultsColumn

    This is a mastapy class.
    '''

    TYPE = _GEAR_FILLET_NODE_STRESS_RESULTS_COLUMN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearFilletNodeStressResultsColumn.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def fillet_column_index(self) -> 'int':
        '''int: 'FilletColumnIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FilletColumnIndex

    @property
    def node_results(self) -> 'List[_797.GearFilletNodeStressResults]':
        '''List[GearFilletNodeStressResults]: 'NodeResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.NodeResults, constructor.new(_797.GearFilletNodeStressResults))
        return value
