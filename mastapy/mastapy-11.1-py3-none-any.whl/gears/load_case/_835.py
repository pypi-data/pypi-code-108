'''_835.py

MeshLoadCase
'''


from mastapy._internal import constructor
from mastapy.gears.analysis import _1166
from mastapy._internal.python_net import python_net_import

_MESH_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase', 'MeshLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('MeshLoadCase',)


class MeshLoadCase(_1166.GearMeshDesignAnalysis):
    '''MeshLoadCase

    This is a mastapy class.
    '''

    TYPE = _MESH_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MeshLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_b_torque(self) -> 'float':
        '''float: 'GearBTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearBTorque

    @property
    def gear_a_torque(self) -> 'float':
        '''float: 'GearATorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearATorque
