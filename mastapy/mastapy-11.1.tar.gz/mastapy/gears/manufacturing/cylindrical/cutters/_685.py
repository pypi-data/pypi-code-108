'''_685.py

CylindricalGearFormGrindingWheel
'''


from mastapy._internal import constructor
from mastapy.math_utility import _1333
from mastapy.gears.manufacturing.cylindrical.cutters import _691
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_FORM_GRINDING_WHEEL = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters', 'CylindricalGearFormGrindingWheel')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearFormGrindingWheel',)


class CylindricalGearFormGrindingWheel(_691.CylindricalGearRealCutterDesign):
    '''CylindricalGearFormGrindingWheel

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_FORM_GRINDING_WHEEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearFormGrindingWheel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radius(self) -> 'float':
        '''float: 'Radius' is the original name of this property.'''

        return self.wrapped.Radius

    @radius.setter
    def radius(self, value: 'float'):
        self.wrapped.Radius = float(value) if value else 0.0

    @property
    def has_tolerances(self) -> 'bool':
        '''bool: 'HasTolerances' is the original name of this property.'''

        return self.wrapped.HasTolerances

    @has_tolerances.setter
    def has_tolerances(self, value: 'bool'):
        self.wrapped.HasTolerances = bool(value) if value else False

    @property
    def right_hand_cutting_edge_shape(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'RightHandCuttingEdgeShape' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.RightHandCuttingEdgeShape) if self.wrapped.RightHandCuttingEdgeShape is not None else None

    @right_hand_cutting_edge_shape.setter
    def right_hand_cutting_edge_shape(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.RightHandCuttingEdgeShape = value
