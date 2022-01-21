'''_1106.py

ConicalMeshedGearDesign
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs import _905
from mastapy._internal.python_net import python_net_import

_CONICAL_MESHED_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'ConicalMeshedGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalMeshedGearDesign',)


class ConicalMeshedGearDesign(_905.GearDesignComponent):
    '''ConicalMeshedGearDesign

    This is a mastapy class.
    '''

    TYPE = _CONICAL_MESHED_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalMeshedGearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gleason_axial_factor_concave(self) -> 'float':
        '''float: 'GleasonAxialFactorConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GleasonAxialFactorConcave

    @property
    def gleason_axial_factor_convex(self) -> 'float':
        '''float: 'GleasonAxialFactorConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GleasonAxialFactorConvex

    @property
    def axial_force_type(self) -> 'str':
        '''str: 'AxialForceType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialForceType

    @property
    def axial_force_type_convex(self) -> 'str':
        '''str: 'AxialForceTypeConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialForceTypeConvex

    @property
    def radial_force_type_convex(self) -> 'str':
        '''str: 'RadialForceTypeConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadialForceTypeConvex

    @property
    def radial_force_type_concave(self) -> 'str':
        '''str: 'RadialForceTypeConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadialForceTypeConcave

    @property
    def gleason_separating_factor_concave(self) -> 'float':
        '''float: 'GleasonSeparatingFactorConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GleasonSeparatingFactorConcave

    @property
    def gleason_separating_factor_convex(self) -> 'float':
        '''float: 'GleasonSeparatingFactorConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GleasonSeparatingFactorConvex

    @property
    def pitch_angle(self) -> 'float':
        '''float: 'PitchAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchAngle

    @property
    def module(self) -> 'float':
        '''float: 'Module' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Module

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''
