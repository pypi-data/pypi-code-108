'''_1124.py

ConceptGearMeshDesign
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.concept import _1125, _1123
from mastapy.gears.gear_designs import _906
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_MESH_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Concept', 'ConceptGearMeshDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearMeshDesign',)


class ConceptGearMeshDesign(_906.GearMeshDesign):
    '''ConceptGearMeshDesign

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_MESH_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearMeshDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def shaft_angle(self) -> 'float':
        '''float: 'ShaftAngle' is the original name of this property.'''

        return self.wrapped.ShaftAngle

    @shaft_angle.setter
    def shaft_angle(self, value: 'float'):
        self.wrapped.ShaftAngle = float(value) if value else 0.0

    @property
    def offset(self) -> 'float':
        '''float: 'Offset' is the original name of this property.'''

        return self.wrapped.Offset

    @offset.setter
    def offset(self, value: 'float'):
        self.wrapped.Offset = float(value) if value else 0.0

    @property
    def concept_gear_set(self) -> '_1125.ConceptGearSetDesign':
        '''ConceptGearSetDesign: 'ConceptGearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1125.ConceptGearSetDesign)(self.wrapped.ConceptGearSet) if self.wrapped.ConceptGearSet is not None else None

    @property
    def concept_gears(self) -> 'List[_1123.ConceptGearDesign]':
        '''List[ConceptGearDesign]: 'ConceptGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptGears, constructor.new(_1123.ConceptGearDesign))
        return value
