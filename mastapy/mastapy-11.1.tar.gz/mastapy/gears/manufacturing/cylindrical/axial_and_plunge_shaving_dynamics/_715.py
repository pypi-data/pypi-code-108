'''_715.py

PlungeShaverDynamics
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical.axial_and_plunge_shaving_dynamics import _725
from mastapy._internal.python_net import python_net_import

_PLUNGE_SHAVER_DYNAMICS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.AxialAndPlungeShavingDynamics', 'PlungeShaverDynamics')


__docformat__ = 'restructuredtext en'
__all__ = ('PlungeShaverDynamics',)


class PlungeShaverDynamics(_725.ShavingDynamics):
    '''PlungeShaverDynamics

    This is a mastapy class.
    '''

    TYPE = _PLUNGE_SHAVER_DYNAMICS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlungeShaverDynamics.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_gear_teeth_passed_per_flank(self) -> 'float':
        '''float: 'NumberOfGearTeethPassedPerFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfGearTeethPassedPerFlank
