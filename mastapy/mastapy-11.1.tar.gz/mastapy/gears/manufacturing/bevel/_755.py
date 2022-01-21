'''_755.py

EaseOffBasedTCA
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.bevel import _732
from mastapy._internal.python_net import python_net_import

_EASE_OFF_BASED_TCA = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'EaseOffBasedTCA')


__docformat__ = 'restructuredtext en'
__all__ = ('EaseOffBasedTCA',)


class EaseOffBasedTCA(_732.AbstractTCA):
    '''EaseOffBasedTCA

    This is a mastapy class.
    '''

    TYPE = _EASE_OFF_BASED_TCA

    __hash__ = None

    def __init__(self, instance_to_wrap: 'EaseOffBasedTCA.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def current_ease_off_optimisation_wheel_u(self) -> 'float':
        '''float: 'CurrentEaseOffOptimisationWheelU' is the original name of this property.'''

        return self.wrapped.CurrentEaseOffOptimisationWheelU

    @current_ease_off_optimisation_wheel_u.setter
    def current_ease_off_optimisation_wheel_u(self, value: 'float'):
        self.wrapped.CurrentEaseOffOptimisationWheelU = float(value) if value else 0.0

    @property
    def current_ease_off_optimisation_wheel_v(self) -> 'float':
        '''float: 'CurrentEaseOffOptimisationWheelV' is the original name of this property.'''

        return self.wrapped.CurrentEaseOffOptimisationWheelV

    @current_ease_off_optimisation_wheel_v.setter
    def current_ease_off_optimisation_wheel_v(self, value: 'float'):
        self.wrapped.CurrentEaseOffOptimisationWheelV = float(value) if value else 0.0
