'''_2501.py

InformationForContactAtPointAlongFaceWidth
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_INFORMATION_FOR_CONTACT_AT_POINT_ALONG_FACE_WIDTH = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'InformationForContactAtPointAlongFaceWidth')


__docformat__ = 'restructuredtext en'
__all__ = ('InformationForContactAtPointAlongFaceWidth',)


class InformationForContactAtPointAlongFaceWidth(_0.APIBase):
    '''InformationForContactAtPointAlongFaceWidth

    This is a mastapy class.
    '''

    TYPE = _INFORMATION_FOR_CONTACT_AT_POINT_ALONG_FACE_WIDTH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InformationForContactAtPointAlongFaceWidth.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidth

    @property
    def surface_penetration(self) -> 'float':
        '''float: 'SurfacePenetration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePenetration

    @property
    def force_per_unit_length(self) -> 'float':
        '''float: 'ForcePerUnitLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ForcePerUnitLength

    @property
    def stiffness_per_unit_length(self) -> 'float':
        '''float: 'StiffnessPerUnitLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessPerUnitLength

    @property
    def maximum_contact_stress(self) -> 'float':
        '''float: 'MaximumContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactStress
