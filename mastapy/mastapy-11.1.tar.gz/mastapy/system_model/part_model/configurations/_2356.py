'''_2356.py

BearingDetailSelection
'''


from typing import List

from mastapy.bearings.bearing_results import _1714
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.system_model.part_model import _2183, _2182
from mastapy.system_model.part_model.configurations import _2358
from mastapy.bearings.bearing_designs import _1879
from mastapy._internal.python_net import python_net_import

_BEARING_DETAIL_SELECTION = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Configurations', 'BearingDetailSelection')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingDetailSelection',)


class BearingDetailSelection(_2358.PartDetailSelection['_2182.Bearing', '_1879.BearingDesign']):
    '''BearingDetailSelection

    This is a mastapy class.
    '''

    TYPE = _BEARING_DETAIL_SELECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingDetailSelection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def orientation(self) -> '_1714.Orientations':
        '''Orientations: 'Orientation' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.Orientation)
        return constructor.new(_1714.Orientations)(value) if value is not None else None

    @orientation.setter
    def orientation(self, value: '_1714.Orientations'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.Orientation = value

    @property
    def mounting(self) -> 'List[_2183.BearingRaceMountingOptions]':
        '''List[BearingRaceMountingOptions]: 'Mounting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Mounting, constructor.new(_2183.BearingRaceMountingOptions))
        return value
