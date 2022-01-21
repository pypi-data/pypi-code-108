'''_1259.py

NamedDiscPhase
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_NAMED_DISC_PHASE = python_net_import('SMT.MastaAPI.Cycloidal', 'NamedDiscPhase')


__docformat__ = 'restructuredtext en'
__all__ = ('NamedDiscPhase',)


class NamedDiscPhase(_0.APIBase):
    '''NamedDiscPhase

    This is a mastapy class.
    '''

    TYPE = _NAMED_DISC_PHASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NamedDiscPhase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def disc_phase_angle(self) -> 'float':
        '''float: 'DiscPhaseAngle' is the original name of this property.'''

        return self.wrapped.DiscPhaseAngle

    @disc_phase_angle.setter
    def disc_phase_angle(self, value: 'float'):
        self.wrapped.DiscPhaseAngle = float(value) if value else 0.0
