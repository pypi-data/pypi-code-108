'''_180.py

ElementDetailsForFEModel
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ELEMENT_DETAILS_FOR_FE_MODEL = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses.FullFEReporting', 'ElementDetailsForFEModel')


__docformat__ = 'restructuredtext en'
__all__ = ('ElementDetailsForFEModel',)


class ElementDetailsForFEModel(_0.APIBase):
    '''ElementDetailsForFEModel

    This is a mastapy class.
    '''

    TYPE = _ELEMENT_DETAILS_FOR_FE_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElementDetailsForFEModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def external_ids(self) -> 'List[int]':
        '''List[int]: 'ExternalIDs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ExternalIDs, int)
        return value

    @property
    def node_ids_for_elements(self) -> 'List[List[int]]':
        '''List[List[int]]: 'NodeIDsForElements' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list_of_lists(self.wrapped.NodeIDsForElements, int)
        return value

    @property
    def element_ids_with_negative_size(self) -> 'List[int]':
        '''List[int]: 'ElementIdsWithNegativeSize' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ElementIdsWithNegativeSize, int)
        return value

    @property
    def element_ids_with_negative_jacobian(self) -> 'List[int]':
        '''List[int]: 'ElementIdsWithNegativeJacobian' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ElementIdsWithNegativeJacobian, int)
        return value

    @property
    def element_ids_with_no_material(self) -> 'List[int]':
        '''List[int]: 'ElementIdsWithNoMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ElementIdsWithNoMaterial, int)
        return value

    @property
    def element_areas(self) -> 'List[float]':
        '''List[float]: 'ElementAreas' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ElementAreas, float)
        return value

    @property
    def element_volumes(self) -> 'List[float]':
        '''List[float]: 'ElementVolumes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ElementVolumes, float)
        return value

    @property
    def total_element_area(self) -> 'float':
        '''float: 'TotalElementArea' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalElementArea

    @property
    def total_element_volume(self) -> 'float':
        '''float: 'TotalElementVolume' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalElementVolume
