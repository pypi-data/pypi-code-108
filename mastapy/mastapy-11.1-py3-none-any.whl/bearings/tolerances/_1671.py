'''_1671.py

RaceRoundnessAtAngle
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RACE_ROUNDNESS_AT_ANGLE = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'RaceRoundnessAtAngle')


__docformat__ = 'restructuredtext en'
__all__ = ('RaceRoundnessAtAngle',)


class RaceRoundnessAtAngle(_0.APIBase):
    '''RaceRoundnessAtAngle

    This is a mastapy class.
    '''

    TYPE = _RACE_ROUNDNESS_AT_ANGLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RaceRoundnessAtAngle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def angle(self) -> 'float':
        '''float: 'Angle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Angle

    @property
    def deviation(self) -> 'float':
        '''float: 'Deviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Deviation
