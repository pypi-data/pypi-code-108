'''_686.py

CylindricalGearGrindingWorm
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical.cutters.tangibles import _706, _708, _703
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.cylindrical.cutters import _690
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_GRINDING_WORM = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters', 'CylindricalGearGrindingWorm')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearGrindingWorm',)


class CylindricalGearGrindingWorm(_690.CylindricalGearRackDesign):
    '''CylindricalGearGrindingWorm

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_GRINDING_WORM

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearGrindingWorm.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def flat_tip_width(self) -> 'float':
        '''float: 'FlatTipWidth' is the original name of this property.'''

        return self.wrapped.FlatTipWidth

    @flat_tip_width.setter
    def flat_tip_width(self, value: 'float'):
        self.wrapped.FlatTipWidth = float(value) if value else 0.0

    @property
    def edge_height(self) -> 'float':
        '''float: 'EdgeHeight' is the original name of this property.'''

        return self.wrapped.EdgeHeight

    @edge_height.setter
    def edge_height(self, value: 'float'):
        self.wrapped.EdgeHeight = float(value) if value else 0.0

    @property
    def has_tolerances(self) -> 'bool':
        '''bool: 'HasTolerances' is the original name of this property.'''

        return self.wrapped.HasTolerances

    @has_tolerances.setter
    def has_tolerances(self, value: 'bool'):
        self.wrapped.HasTolerances = bool(value) if value else False

    @property
    def nominal_worm_grinder_shape(self) -> '_706.CylindricalGearWormGrinderShape':
        '''CylindricalGearWormGrinderShape: 'NominalWormGrinderShape' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_706.CylindricalGearWormGrinderShape)(self.wrapped.NominalWormGrinderShape) if self.wrapped.NominalWormGrinderShape is not None else None

    @property
    def nominal_rack_shape(self) -> '_708.RackShape':
        '''RackShape: 'NominalRackShape' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _708.RackShape.TYPE not in self.wrapped.NominalRackShape.__class__.__mro__:
            raise CastException('Failed to cast nominal_rack_shape to RackShape. Expected: {}.'.format(self.wrapped.NominalRackShape.__class__.__qualname__))

        return constructor.new_override(self.wrapped.NominalRackShape.__class__)(self.wrapped.NominalRackShape) if self.wrapped.NominalRackShape is not None else None

    @property
    def nominal_rack_shape_of_type_cylindrical_gear_hob_shape(self) -> '_703.CylindricalGearHobShape':
        '''CylindricalGearHobShape: 'NominalRackShape' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _703.CylindricalGearHobShape.TYPE not in self.wrapped.NominalRackShape.__class__.__mro__:
            raise CastException('Failed to cast nominal_rack_shape to CylindricalGearHobShape. Expected: {}.'.format(self.wrapped.NominalRackShape.__class__.__qualname__))

        return constructor.new_override(self.wrapped.NominalRackShape.__class__)(self.wrapped.NominalRackShape) if self.wrapped.NominalRackShape is not None else None

    @property
    def nominal_rack_shape_of_type_cylindrical_gear_worm_grinder_shape(self) -> '_706.CylindricalGearWormGrinderShape':
        '''CylindricalGearWormGrinderShape: 'NominalRackShape' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _706.CylindricalGearWormGrinderShape.TYPE not in self.wrapped.NominalRackShape.__class__.__mro__:
            raise CastException('Failed to cast nominal_rack_shape to CylindricalGearWormGrinderShape. Expected: {}.'.format(self.wrapped.NominalRackShape.__class__.__qualname__))

        return constructor.new_override(self.wrapped.NominalRackShape.__class__)(self.wrapped.NominalRackShape) if self.wrapped.NominalRackShape is not None else None
