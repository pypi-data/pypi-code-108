'''_188.py

ElementPropertiesSpringDashpot
'''


from mastapy._internal import constructor, conversion
from mastapy._math.vector_3d import Vector3D
from mastapy.nodal_analysis.dev_tools_analyses.full_fe_reporting import _181
from mastapy._internal.python_net import python_net_import

_ELEMENT_PROPERTIES_SPRING_DASHPOT = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses.FullFEReporting', 'ElementPropertiesSpringDashpot')


__docformat__ = 'restructuredtext en'
__all__ = ('ElementPropertiesSpringDashpot',)


class ElementPropertiesSpringDashpot(_181.ElementPropertiesBase):
    '''ElementPropertiesSpringDashpot

    This is a mastapy class.
    '''

    TYPE = _ELEMENT_PROPERTIES_SPRING_DASHPOT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElementPropertiesSpringDashpot.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def stiffness_matrix_lower_triangle(self) -> 'str':
        '''str: 'StiffnessMatrixLowerTriangle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessMatrixLowerTriangle

    @property
    def stiffness(self) -> 'float':
        '''float: 'Stiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Stiffness

    @property
    def degree_of_freedom_1(self) -> 'int':
        '''int: 'DegreeOfFreedom1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DegreeOfFreedom1

    @property
    def degree_of_freedom_2(self) -> 'int':
        '''int: 'DegreeOfFreedom2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DegreeOfFreedom2

    @property
    def stiffness_translation(self) -> 'Vector3D':
        '''Vector3D: 'StiffnessTranslation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.StiffnessTranslation)
        return value

    @property
    def stiffness_rotation(self) -> 'Vector3D':
        '''Vector3D: 'StiffnessRotation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.StiffnessRotation)
        return value
