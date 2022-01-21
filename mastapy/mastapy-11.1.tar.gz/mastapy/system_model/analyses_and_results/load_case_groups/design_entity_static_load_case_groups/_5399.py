'''_5399.py

ConnectionStaticLoadCaseGroup
'''


from typing import List, Generic, TypeVar

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups import _5400
from mastapy.system_model.connections_and_sockets import _2014
from mastapy.system_model.analyses_and_results.static_loads import _6563
from mastapy._internal.python_net import python_net_import

_CONNECTION_STATIC_LOAD_CASE_GROUP = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.LoadCaseGroups.DesignEntityStaticLoadCaseGroups', 'ConnectionStaticLoadCaseGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectionStaticLoadCaseGroup',)


TConnection = TypeVar('TConnection', bound='_2014.Connection')
TConnectionStaticLoad = TypeVar('TConnectionStaticLoad', bound='_6563.ConnectionLoadCase')


class ConnectionStaticLoadCaseGroup(_5400.DesignEntityStaticLoadCaseGroup, Generic[TConnection, TConnectionStaticLoad]):
    '''ConnectionStaticLoadCaseGroup

    This is a mastapy class.

    Generic Types:
        TConnection
        TConnectionStaticLoad
    '''

    TYPE = _CONNECTION_STATIC_LOAD_CASE_GROUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectionStaticLoadCaseGroup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection(self) -> 'TConnection':
        '''TConnection: 'Connection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Connection

    @property
    def connection_load_cases(self) -> 'List[TConnectionStaticLoad]':
        '''List[TConnectionStaticLoad]: 'ConnectionLoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionLoadCases)
        return value
