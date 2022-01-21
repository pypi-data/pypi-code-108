'''_1902.py

GeometricConstants
'''


from mastapy.bearings.bearing_designs.rolling import _1903, _1904
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEOMETRIC_CONSTANTS = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'GeometricConstants')


__docformat__ = 'restructuredtext en'
__all__ = ('GeometricConstants',)


class GeometricConstants(_0.APIBase):
    '''GeometricConstants

    This is a mastapy class.
    '''

    TYPE = _GEOMETRIC_CONSTANTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GeometricConstants.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def geometric_constants_for_rolling_frictional_moments(self) -> '_1903.GeometricConstantsForRollingFrictionalMoments':
        '''GeometricConstantsForRollingFrictionalMoments: 'GeometricConstantsForRollingFrictionalMoments' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1903.GeometricConstantsForRollingFrictionalMoments)(self.wrapped.GeometricConstantsForRollingFrictionalMoments) if self.wrapped.GeometricConstantsForRollingFrictionalMoments is not None else None

    @property
    def geometric_constants_for_sliding_frictional_moments(self) -> '_1904.GeometricConstantsForSlidingFrictionalMoments':
        '''GeometricConstantsForSlidingFrictionalMoments: 'GeometricConstantsForSlidingFrictionalMoments' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1904.GeometricConstantsForSlidingFrictionalMoments)(self.wrapped.GeometricConstantsForSlidingFrictionalMoments) if self.wrapped.GeometricConstantsForSlidingFrictionalMoments is not None else None
