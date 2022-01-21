'''_805.py

GearRootFilletStressResults
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.ltca import _799, _798
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_ROOT_FILLET_STRESS_RESULTS = python_net_import('SMT.MastaAPI.Gears.LTCA', 'GearRootFilletStressResults')


__docformat__ = 'restructuredtext en'
__all__ = ('GearRootFilletStressResults',)


class GearRootFilletStressResults(_0.APIBase):
    '''GearRootFilletStressResults

    This is a mastapy class.
    '''

    TYPE = _GEAR_ROOT_FILLET_STRESS_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearRootFilletStressResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def contact_line_index(self) -> 'int':
        '''int: 'ContactLineIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactLineIndex

    @property
    def rows(self) -> 'List[_799.GearFilletNodeStressResultsRow]':
        '''List[GearFilletNodeStressResultsRow]: 'Rows' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Rows, constructor.new(_799.GearFilletNodeStressResultsRow))
        return value

    @property
    def columns(self) -> 'List[_798.GearFilletNodeStressResultsColumn]':
        '''List[GearFilletNodeStressResultsColumn]: 'Columns' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Columns, constructor.new(_798.GearFilletNodeStressResultsColumn))
        return value
