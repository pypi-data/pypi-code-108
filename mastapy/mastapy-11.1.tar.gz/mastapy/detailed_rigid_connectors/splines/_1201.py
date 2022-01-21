'''_1201.py

JISB1603SplineJointDesign
'''


from mastapy.detailed_rigid_connectors.splines import _1200
from mastapy._internal.python_net import python_net_import

_JISB1603_SPLINE_JOINT_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'JISB1603SplineJointDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('JISB1603SplineJointDesign',)


class JISB1603SplineJointDesign(_1200.ISO4156SplineJointDesign):
    '''JISB1603SplineJointDesign

    This is a mastapy class.
    '''

    TYPE = _JISB1603_SPLINE_JOINT_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'JISB1603SplineJointDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
