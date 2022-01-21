'''_1723.py

ForceAtLaminaGroupReportable
'''


from typing import List

from mastapy.bearings.bearing_results.rolling import _1724
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FORCE_AT_LAMINA_GROUP_REPORTABLE = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'ForceAtLaminaGroupReportable')


__docformat__ = 'restructuredtext en'
__all__ = ('ForceAtLaminaGroupReportable',)


class ForceAtLaminaGroupReportable(_0.APIBase):
    '''ForceAtLaminaGroupReportable

    This is a mastapy class.
    '''

    TYPE = _FORCE_AT_LAMINA_GROUP_REPORTABLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ForceAtLaminaGroupReportable.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def forces_at_laminae(self) -> 'List[_1724.ForceAtLaminaReportable]':
        '''List[ForceAtLaminaReportable]: 'ForcesAtLaminae' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ForcesAtLaminae, constructor.new(_1724.ForceAtLaminaReportable))
        return value
