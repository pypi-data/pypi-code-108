'''_193.py

RigidElementNodeDegreesOfFreedom
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.nodal_analysis.dev_tools_analyses.full_fe_reporting import _178
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RIGID_ELEMENT_NODE_DEGREES_OF_FREEDOM = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses.FullFEReporting', 'RigidElementNodeDegreesOfFreedom')


__docformat__ = 'restructuredtext en'
__all__ = ('RigidElementNodeDegreesOfFreedom',)


class RigidElementNodeDegreesOfFreedom(_0.APIBase):
    '''RigidElementNodeDegreesOfFreedom

    This is a mastapy class.
    '''

    TYPE = _RIGID_ELEMENT_NODE_DEGREES_OF_FREEDOM

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RigidElementNodeDegreesOfFreedom.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def index(self) -> 'int':
        '''int: 'Index' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Index

    @property
    def type_(self) -> '_178.DegreeOfFreedomType':
        '''DegreeOfFreedomType: 'Type' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.Type)
        return constructor.new(_178.DegreeOfFreedomType)(value) if value is not None else None

    @property
    def x(self) -> 'bool':
        '''bool: 'X' is the original name of this property.'''

        return self.wrapped.X

    @x.setter
    def x(self, value: 'bool'):
        self.wrapped.X = bool(value) if value else False

    @property
    def y(self) -> 'bool':
        '''bool: 'Y' is the original name of this property.'''

        return self.wrapped.Y

    @y.setter
    def y(self, value: 'bool'):
        self.wrapped.Y = bool(value) if value else False

    @property
    def z(self) -> 'bool':
        '''bool: 'Z' is the original name of this property.'''

        return self.wrapped.Z

    @z.setter
    def z(self, value: 'bool'):
        self.wrapped.Z = bool(value) if value else False

    @property
    def theta_x(self) -> 'bool':
        '''bool: 'ThetaX' is the original name of this property.'''

        return self.wrapped.ThetaX

    @theta_x.setter
    def theta_x(self, value: 'bool'):
        self.wrapped.ThetaX = bool(value) if value else False

    @property
    def theta_y(self) -> 'bool':
        '''bool: 'ThetaY' is the original name of this property.'''

        return self.wrapped.ThetaY

    @theta_y.setter
    def theta_y(self, value: 'bool'):
        self.wrapped.ThetaY = bool(value) if value else False

    @property
    def theta_z(self) -> 'bool':
        '''bool: 'ThetaZ' is the original name of this property.'''

        return self.wrapped.ThetaZ

    @theta_z.setter
    def theta_z(self, value: 'bool'):
        self.wrapped.ThetaZ = bool(value) if value else False
