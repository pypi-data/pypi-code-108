'''_1196.py

GBT3478SplineHalfDesign
'''


from mastapy.detailed_rigid_connectors.splines import _1199
from mastapy._internal.python_net import python_net_import

_GBT3478_SPLINE_HALF_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'GBT3478SplineHalfDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('GBT3478SplineHalfDesign',)


class GBT3478SplineHalfDesign(_1199.ISO4156SplineHalfDesign):
    '''GBT3478SplineHalfDesign

    This is a mastapy class.
    '''

    TYPE = _GBT3478_SPLINE_HALF_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GBT3478SplineHalfDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
