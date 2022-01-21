'''_54.py

DiagonalNonlinearStiffness
'''


from mastapy.math_utility import _1333
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DIAGONAL_NONLINEAR_STIFFNESS = python_net_import('SMT.MastaAPI.NodalAnalysis', 'DiagonalNonlinearStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('DiagonalNonlinearStiffness',)


class DiagonalNonlinearStiffness(_0.APIBase):
    '''DiagonalNonlinearStiffness

    This is a mastapy class.
    '''

    TYPE = _DIAGONAL_NONLINEAR_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DiagonalNonlinearStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def x_stiffness(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'XStiffness' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.XStiffness) if self.wrapped.XStiffness is not None else None

    @x_stiffness.setter
    def x_stiffness(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.XStiffness = value

    @property
    def y_stiffness(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'YStiffness' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.YStiffness) if self.wrapped.YStiffness is not None else None

    @y_stiffness.setter
    def y_stiffness(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.YStiffness = value

    @property
    def z_stiffness(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'ZStiffness' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.ZStiffness) if self.wrapped.ZStiffness is not None else None

    @z_stiffness.setter
    def z_stiffness(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.ZStiffness = value

    @property
    def theta_x_stiffness(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'ThetaXStiffness' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.ThetaXStiffness) if self.wrapped.ThetaXStiffness is not None else None

    @theta_x_stiffness.setter
    def theta_x_stiffness(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.ThetaXStiffness = value

    @property
    def theta_y_stiffness(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'ThetaYStiffness' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.ThetaYStiffness) if self.wrapped.ThetaYStiffness is not None else None

    @theta_y_stiffness.setter
    def theta_y_stiffness(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.ThetaYStiffness = value

    @property
    def theta_z_stiffness(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'ThetaZStiffness' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.ThetaZStiffness) if self.wrapped.ThetaZStiffness is not None else None

    @theta_z_stiffness.setter
    def theta_z_stiffness(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.ThetaZStiffness = value
