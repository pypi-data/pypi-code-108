'''_939.py

KlingelnbergConicalGearMeshDesign
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.gear_designs.conical import _1102
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CONICAL_GEAR_MESH_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.KlingelnbergConical', 'KlingelnbergConicalGearMeshDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergConicalGearMeshDesign',)


class KlingelnbergConicalGearMeshDesign(_1102.ConicalGearMeshDesign):
    '''KlingelnbergConicalGearMeshDesign

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CONICAL_GEAR_MESH_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergConicalGearMeshDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def effective_face_width(self) -> 'float':
        '''float: 'EffectiveFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveFaceWidth

    @property
    def application_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ApplicationFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ApplicationFactor) if self.wrapped.ApplicationFactor is not None else None

    @application_factor.setter
    def application_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ApplicationFactor = value

    @property
    def net_face_width(self) -> 'float':
        '''float: 'NetFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NetFaceWidth

    @property
    def load_distribution_factor_longitudinal(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'LoadDistributionFactorLongitudinal' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.LoadDistributionFactorLongitudinal) if self.wrapped.LoadDistributionFactorLongitudinal is not None else None

    @load_distribution_factor_longitudinal.setter
    def load_distribution_factor_longitudinal(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.LoadDistributionFactorLongitudinal = value
