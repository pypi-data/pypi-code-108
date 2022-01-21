'''_3759.py

RotorDynamicsDrawStyle
'''


from mastapy._internal import constructor
from mastapy.system_model.drawing import _1987
from mastapy._internal.python_net import python_net_import

_ROTOR_DYNAMICS_DRAW_STYLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.RotorDynamics', 'RotorDynamicsDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('RotorDynamicsDrawStyle',)


class RotorDynamicsDrawStyle(_1987.ContourDrawStyle):
    '''RotorDynamicsDrawStyle

    This is a mastapy class.
    '''

    TYPE = _ROTOR_DYNAMICS_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RotorDynamicsDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def show_whirl_orbits(self) -> 'bool':
        '''bool: 'ShowWhirlOrbits' is the original name of this property.'''

        return self.wrapped.ShowWhirlOrbits

    @show_whirl_orbits.setter
    def show_whirl_orbits(self, value: 'bool'):
        self.wrapped.ShowWhirlOrbits = bool(value) if value else False
