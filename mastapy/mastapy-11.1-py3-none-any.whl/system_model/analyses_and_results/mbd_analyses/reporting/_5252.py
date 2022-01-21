'''_5252.py

DynamicTorqueVector3DResult
'''


from mastapy.system_model.analyses_and_results.mbd_analyses.reporting import _5251
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DYNAMIC_TORQUE_VECTOR_3D_RESULT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Reporting', 'DynamicTorqueVector3DResult')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicTorqueVector3DResult',)


class DynamicTorqueVector3DResult(_0.APIBase):
    '''DynamicTorqueVector3DResult

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_TORQUE_VECTOR_3D_RESULT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicTorqueVector3DResult.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def x(self) -> '_5251.DynamicTorqueResultAtTime':
        '''DynamicTorqueResultAtTime: 'X' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5251.DynamicTorqueResultAtTime)(self.wrapped.X) if self.wrapped.X is not None else None

    @property
    def y(self) -> '_5251.DynamicTorqueResultAtTime':
        '''DynamicTorqueResultAtTime: 'Y' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5251.DynamicTorqueResultAtTime)(self.wrapped.Y) if self.wrapped.Y is not None else None

    @property
    def z(self) -> '_5251.DynamicTorqueResultAtTime':
        '''DynamicTorqueResultAtTime: 'Z' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5251.DynamicTorqueResultAtTime)(self.wrapped.Z) if self.wrapped.Z is not None else None

    @property
    def magnitude(self) -> '_5251.DynamicTorqueResultAtTime':
        '''DynamicTorqueResultAtTime: 'Magnitude' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5251.DynamicTorqueResultAtTime)(self.wrapped.Magnitude) if self.wrapped.Magnitude is not None else None

    @property
    def radial_magnitude(self) -> '_5251.DynamicTorqueResultAtTime':
        '''DynamicTorqueResultAtTime: 'RadialMagnitude' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5251.DynamicTorqueResultAtTime)(self.wrapped.RadialMagnitude) if self.wrapped.RadialMagnitude is not None else None
