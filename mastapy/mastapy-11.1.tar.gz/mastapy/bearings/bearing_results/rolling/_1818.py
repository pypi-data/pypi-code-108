'''_1818.py

RingForceAndDisplacement
'''


from mastapy._internal import constructor
from mastapy.math_utility.measured_vectors import _1363
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RING_FORCE_AND_DISPLACEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'RingForceAndDisplacement')


__docformat__ = 'restructuredtext en'
__all__ = ('RingForceAndDisplacement',)


class RingForceAndDisplacement(_0.APIBase):
    '''RingForceAndDisplacement

    This is a mastapy class.
    '''

    TYPE = _RING_FORCE_AND_DISPLACEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingForceAndDisplacement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def magnitude_of_misalignment_normal_to_load_direction(self) -> 'float':
        '''float: 'MagnitudeOfMisalignmentNormalToLoadDirection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MagnitudeOfMisalignmentNormalToLoadDirection

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def displacement(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'Displacement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.Displacement) if self.wrapped.Displacement is not None else None

    @property
    def force(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'Force' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.Force) if self.wrapped.Force is not None else None
