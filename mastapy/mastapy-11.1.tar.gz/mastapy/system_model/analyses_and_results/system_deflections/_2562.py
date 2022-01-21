'''_2562.py

SystemDeflectionOptions
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.analysis_cases import _7253
from mastapy.system_model.analyses_and_results.static_loads import _6519
from mastapy._internal.python_net import python_net_import

_SYSTEM_DEFLECTION_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'SystemDeflectionOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('SystemDeflectionOptions',)


class SystemDeflectionOptions(_7253.AbstractAnalysisOptions['_6519.StaticLoadCase']):
    '''SystemDeflectionOptions

    This is a mastapy class.
    '''

    TYPE = _SYSTEM_DEFLECTION_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SystemDeflectionOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_rigid_body_rotation_change_in_system_deflection(self) -> 'float':
        '''float: 'MaximumRigidBodyRotationChangeInSystemDeflection' is the original name of this property.'''

        return self.wrapped.MaximumRigidBodyRotationChangeInSystemDeflection

    @maximum_rigid_body_rotation_change_in_system_deflection.setter
    def maximum_rigid_body_rotation_change_in_system_deflection(self, value: 'float'):
        self.wrapped.MaximumRigidBodyRotationChangeInSystemDeflection = float(value) if value else 0.0

    @property
    def maximum_number_of_unstable_rigid_body_rotation_iterations(self) -> 'int':
        '''int: 'MaximumNumberOfUnstableRigidBodyRotationIterations' is the original name of this property.'''

        return self.wrapped.MaximumNumberOfUnstableRigidBodyRotationIterations

    @maximum_number_of_unstable_rigid_body_rotation_iterations.setter
    def maximum_number_of_unstable_rigid_body_rotation_iterations(self, value: 'int'):
        self.wrapped.MaximumNumberOfUnstableRigidBodyRotationIterations = int(value) if value else 0

    @property
    def ground_shaft_if_rigid_body_rotation_is_large(self) -> 'bool':
        '''bool: 'GroundShaftIfRigidBodyRotationIsLarge' is the original name of this property.'''

        return self.wrapped.GroundShaftIfRigidBodyRotationIsLarge

    @ground_shaft_if_rigid_body_rotation_is_large.setter
    def ground_shaft_if_rigid_body_rotation_is_large(self, value: 'bool'):
        self.wrapped.GroundShaftIfRigidBodyRotationIsLarge = bool(value) if value else False
