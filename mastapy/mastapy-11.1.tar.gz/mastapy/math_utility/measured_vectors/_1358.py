'''_1358.py

AbstractForceAndDisplacementResults
'''


from mastapy._internal import constructor, conversion
from mastapy._math.vector_3d import Vector3D
from mastapy.math_utility.measured_vectors import _1363
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ABSTRACT_FORCE_AND_DISPLACEMENT_RESULTS = python_net_import('SMT.MastaAPI.MathUtility.MeasuredVectors', 'AbstractForceAndDisplacementResults')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractForceAndDisplacementResults',)


class AbstractForceAndDisplacementResults(_0.APIBase):
    '''AbstractForceAndDisplacementResults

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_FORCE_AND_DISPLACEMENT_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractForceAndDisplacementResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def node(self) -> 'str':
        '''str: 'Node' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Node

    @property
    def location(self) -> 'Vector3D':
        '''Vector3D: 'Location' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.Location)
        return value

    @property
    def force(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'Force' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.Force) if self.wrapped.Force is not None else None
