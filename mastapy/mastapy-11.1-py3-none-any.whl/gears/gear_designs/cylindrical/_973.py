'''_973.py

CylindricalGearDesignConstraintSettings
'''


from mastapy._internal.python_net import python_net_import
from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical import _971
from mastapy.utility import _1387

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_CYLINDRICAL_GEAR_DESIGN_CONSTRAINT_SETTINGS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearDesignConstraintSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearDesignConstraintSettings',)


class CylindricalGearDesignConstraintSettings(_1387.PerMachineSettings):
    '''CylindricalGearDesignConstraintSettings

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_DESIGN_CONSTRAINT_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearDesignConstraintSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def cylindrical_gear_design_constraints_database(self) -> 'str':
        '''str: 'CylindricalGearDesignConstraintsDatabase' is the original name of this property.'''

        return self.wrapped.CylindricalGearDesignConstraintsDatabase.SelectedItemName

    @cylindrical_gear_design_constraints_database.setter
    def cylindrical_gear_design_constraints_database(self, value: 'str'):
        self.wrapped.CylindricalGearDesignConstraintsDatabase.SetSelectedItem(str(value) if value else '')

    @property
    def cylindrical_gear_design_constraints(self) -> '_971.CylindricalGearDesignConstraints':
        '''CylindricalGearDesignConstraints: 'CylindricalGearDesignConstraints' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_971.CylindricalGearDesignConstraints)(self.wrapped.CylindricalGearDesignConstraints) if self.wrapped.CylindricalGearDesignConstraints is not None else None
