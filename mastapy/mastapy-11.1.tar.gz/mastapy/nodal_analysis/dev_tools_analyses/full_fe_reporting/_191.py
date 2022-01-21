'''_191.py

NodeDetailsForFEModel
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._math.vector_3d import Vector3D
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_NODE_DETAILS_FOR_FE_MODEL = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses.FullFEReporting', 'NodeDetailsForFEModel')


__docformat__ = 'restructuredtext en'
__all__ = ('NodeDetailsForFEModel',)


class NodeDetailsForFEModel(_0.APIBase):
    '''NodeDetailsForFEModel

    This is a mastapy class.
    '''

    TYPE = _NODE_DETAILS_FOR_FE_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NodeDetailsForFEModel.TYPE'):
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
    def node_positions(self) -> 'List[Vector3D]':
        '''List[Vector3D]: 'NodePositions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.NodePositions, Vector3D)
        return value
