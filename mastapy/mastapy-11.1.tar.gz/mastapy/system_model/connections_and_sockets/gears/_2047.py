'''_2047.py

ConceptGearMesh
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.concept import _1124
from mastapy.system_model.connections_and_sockets.gears import _2055
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_MESH = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears', 'ConceptGearMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearMesh',)


class ConceptGearMesh(_2055.GearMesh):
    '''ConceptGearMesh

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pinion_drop_angle(self) -> 'float':
        '''float: 'PinionDropAngle' is the original name of this property.'''

        return self.wrapped.PinionDropAngle

    @pinion_drop_angle.setter
    def pinion_drop_angle(self, value: 'float'):
        self.wrapped.PinionDropAngle = float(value) if value else 0.0

    @property
    def wheel_drop_angle(self) -> 'float':
        '''float: 'WheelDropAngle' is the original name of this property.'''

        return self.wrapped.WheelDropAngle

    @wheel_drop_angle.setter
    def wheel_drop_angle(self, value: 'float'):
        self.wrapped.WheelDropAngle = float(value) if value else 0.0

    @property
    def concept_gear_mesh_design(self) -> '_1124.ConceptGearMeshDesign':
        '''ConceptGearMeshDesign: 'ConceptGearMeshDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1124.ConceptGearMeshDesign)(self.wrapped.ConceptGearMeshDesign) if self.wrapped.ConceptGearMeshDesign is not None else None
