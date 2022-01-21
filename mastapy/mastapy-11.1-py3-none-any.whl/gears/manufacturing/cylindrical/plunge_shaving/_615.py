'''_615.py

ShaverPointCalculationError
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical.plunge_shaving import _602
from mastapy._internal.python_net import python_net_import

_SHAVER_POINT_CALCULATION_ERROR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.PlungeShaving', 'ShaverPointCalculationError')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaverPointCalculationError',)


class ShaverPointCalculationError(_602.CalculationError):
    '''ShaverPointCalculationError

    This is a mastapy class.
    '''

    TYPE = _SHAVER_POINT_CALCULATION_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaverPointCalculationError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def shaver_z_plane(self) -> 'float':
        '''float: 'ShaverZPlane' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaverZPlane

    @property
    def shaver_radius(self) -> 'float':
        '''float: 'ShaverRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaverRadius

    @property
    def achieved_shaver_z_plane(self) -> 'float':
        '''float: 'AchievedShaverZPlane' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AchievedShaverZPlane

    @property
    def achieved_shaver_radius(self) -> 'float':
        '''float: 'AchievedShaverRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AchievedShaverRadius

    @property
    def total_error(self) -> 'float':
        '''float: 'TotalError' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalError
