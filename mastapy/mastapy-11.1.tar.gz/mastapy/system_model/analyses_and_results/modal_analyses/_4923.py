'''_4923.py

ShaftModalAnalysisMode
'''


from typing import List

from mastapy._math.vector_3d import Vector3D
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SHAFT_MODAL_ANALYSIS_MODE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'ShaftModalAnalysisMode')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftModalAnalysisMode',)


class ShaftModalAnalysisMode(_0.APIBase):
    '''ShaftModalAnalysisMode

    This is a mastapy class.
    '''

    TYPE = _SHAFT_MODAL_ANALYSIS_MODE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftModalAnalysisMode.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def angular_displacement(self) -> 'List[Vector3D]':
        '''List[Vector3D]: 'AngularDisplacement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AngularDisplacement, Vector3D)
        return value

    @property
    def linear_displacement(self) -> 'List[Vector3D]':
        '''List[Vector3D]: 'LinearDisplacement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LinearDisplacement, Vector3D)
        return value
