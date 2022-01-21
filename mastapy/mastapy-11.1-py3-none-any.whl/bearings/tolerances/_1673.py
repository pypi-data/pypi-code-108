'''_1673.py

RingTolerance
'''


from mastapy.bearings.tolerances import _1674, _1665
from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_RING_TOLERANCE = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'RingTolerance')


__docformat__ = 'restructuredtext en'
__all__ = ('RingTolerance',)


class RingTolerance(_1665.InterferenceTolerance):
    '''RingTolerance

    This is a mastapy class.
    '''

    TYPE = _RING_TOLERANCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingTolerance.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def roundness_specification(self) -> '_1674.RoundnessSpecification':
        '''RoundnessSpecification: 'RoundnessSpecification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1674.RoundnessSpecification)(self.wrapped.RoundnessSpecification) if self.wrapped.RoundnessSpecification is not None else None
