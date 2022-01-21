'''_1200.py

ISO4156SplineJointDesign
'''


from mastapy._internal import constructor
from mastapy.detailed_rigid_connectors.splines import _1220
from mastapy._internal.python_net import python_net_import

_ISO4156_SPLINE_JOINT_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'ISO4156SplineJointDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO4156SplineJointDesign',)


class ISO4156SplineJointDesign(_1220.StandardSplineJointDesign):
    '''ISO4156SplineJointDesign

    This is a mastapy class.
    '''

    TYPE = _ISO4156_SPLINE_JOINT_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO4156SplineJointDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def form_clearance(self) -> 'float':
        '''float: 'FormClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FormClearance

    @property
    def maximum_effective_clearance(self) -> 'float':
        '''float: 'MaximumEffectiveClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumEffectiveClearance

    @property
    def minimum_effective_clearance(self) -> 'float':
        '''float: 'MinimumEffectiveClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumEffectiveClearance
