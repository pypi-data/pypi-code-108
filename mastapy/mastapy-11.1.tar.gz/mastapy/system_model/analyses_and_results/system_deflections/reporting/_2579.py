'''_2579.py

GearInMeshDeflectionResults
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_IN_MESH_DEFLECTION_RESULTS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Reporting', 'GearInMeshDeflectionResults')


__docformat__ = 'restructuredtext en'
__all__ = ('GearInMeshDeflectionResults',)


class GearInMeshDeflectionResults(_0.APIBase):
    '''GearInMeshDeflectionResults

    This is a mastapy class.
    '''

    TYPE = _GEAR_IN_MESH_DEFLECTION_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearInMeshDeflectionResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def transverse_deflection(self) -> 'float':
        '''float: 'TransverseDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseDeflection

    @property
    def microgeometry(self) -> 'float':
        '''float: 'Microgeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Microgeometry

    @property
    def transverse_deflection_with_microgeometry(self) -> 'float':
        '''float: 'TransverseDeflectionWithMicrogeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseDeflectionWithMicrogeometry
