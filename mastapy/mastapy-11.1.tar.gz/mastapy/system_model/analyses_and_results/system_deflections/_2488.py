'''_2488.py

FaceGearMeshMisalignmentsWithRespectToCrossPointCalculator
'''


from mastapy.gears.gear_designs.conical import _1107
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_MESH_MISALIGNMENTS_WITH_RESPECT_TO_CROSS_POINT_CALCULATOR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'FaceGearMeshMisalignmentsWithRespectToCrossPointCalculator')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearMeshMisalignmentsWithRespectToCrossPointCalculator',)


class FaceGearMeshMisalignmentsWithRespectToCrossPointCalculator(_0.APIBase):
    '''FaceGearMeshMisalignmentsWithRespectToCrossPointCalculator

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_MESH_MISALIGNMENTS_WITH_RESPECT_TO_CROSS_POINT_CALCULATOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearMeshMisalignmentsWithRespectToCrossPointCalculator.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def misalignments_total(self) -> '_1107.ConicalMeshMisalignments':
        '''ConicalMeshMisalignments: 'MisalignmentsTotal' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1107.ConicalMeshMisalignments)(self.wrapped.MisalignmentsTotal) if self.wrapped.MisalignmentsTotal is not None else None

    @property
    def misalignments_pinion(self) -> '_1107.ConicalMeshMisalignments':
        '''ConicalMeshMisalignments: 'MisalignmentsPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1107.ConicalMeshMisalignments)(self.wrapped.MisalignmentsPinion) if self.wrapped.MisalignmentsPinion is not None else None

    @property
    def misalignments_wheel(self) -> '_1107.ConicalMeshMisalignments':
        '''ConicalMeshMisalignments: 'MisalignmentsWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1107.ConicalMeshMisalignments)(self.wrapped.MisalignmentsWheel) if self.wrapped.MisalignmentsWheel is not None else None
