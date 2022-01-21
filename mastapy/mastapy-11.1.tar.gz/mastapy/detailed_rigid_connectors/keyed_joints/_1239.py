'''_1239.py

KeywayJointHalfDesign
'''


from mastapy._internal import constructor
from mastapy.detailed_rigid_connectors.interference_fits import _1246
from mastapy._internal.python_net import python_net_import

_KEYWAY_JOINT_HALF_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.KeyedJoints', 'KeywayJointHalfDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('KeywayJointHalfDesign',)


class KeywayJointHalfDesign(_1246.InterferenceFitHalfDesign):
    '''KeywayJointHalfDesign

    This is a mastapy class.
    '''

    TYPE = _KEYWAY_JOINT_HALF_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KeywayJointHalfDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def keyway_chamfer_depth(self) -> 'float':
        '''float: 'KeywayChamferDepth' is the original name of this property.'''

        return self.wrapped.KeywayChamferDepth

    @keyway_chamfer_depth.setter
    def keyway_chamfer_depth(self, value: 'float'):
        self.wrapped.KeywayChamferDepth = float(value) if value else 0.0

    @property
    def effective_keyway_depth(self) -> 'float':
        '''float: 'EffectiveKeywayDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveKeywayDepth

    @property
    def support_factor(self) -> 'float':
        '''float: 'SupportFactor' is the original name of this property.'''

        return self.wrapped.SupportFactor

    @support_factor.setter
    def support_factor(self, value: 'float'):
        self.wrapped.SupportFactor = float(value) if value else 0.0

    @property
    def is_case_hardened(self) -> 'bool':
        '''bool: 'IsCaseHardened' is the original name of this property.'''

        return self.wrapped.IsCaseHardened

    @is_case_hardened.setter
    def is_case_hardened(self, value: 'bool'):
        self.wrapped.IsCaseHardened = bool(value) if value else False

    @property
    def hardness_factor(self) -> 'float':
        '''float: 'HardnessFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HardnessFactor

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
