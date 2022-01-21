'''_2138.py

LinkComponentAxialPositionErrorReporter
'''


from mastapy._math.vector_3d import Vector3D
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_LINK_COMPONENT_AXIAL_POSITION_ERROR_REPORTER = python_net_import('SMT.MastaAPI.SystemModel.FE', 'LinkComponentAxialPositionErrorReporter')


__docformat__ = 'restructuredtext en'
__all__ = ('LinkComponentAxialPositionErrorReporter',)


class LinkComponentAxialPositionErrorReporter(_0.APIBase):
    '''LinkComponentAxialPositionErrorReporter

    This is a mastapy class.
    '''

    TYPE = _LINK_COMPONENT_AXIAL_POSITION_ERROR_REPORTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LinkComponentAxialPositionErrorReporter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def location_on_component_axis_from_fe_nodes(self) -> 'Vector3D':
        '''Vector3D: 'LocationOnComponentAxisFromFENodes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.LocationOnComponentAxisFromFENodes)
        return value

    @property
    def expected_location_on_component_axis(self) -> 'Vector3D':
        '''Vector3D: 'ExpectedLocationOnComponentAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.ExpectedLocationOnComponentAxis)
        return value

    @property
    def error_in_location_on_axis(self) -> 'Vector3D':
        '''Vector3D: 'ErrorInLocationOnAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.ErrorInLocationOnAxis)
        return value
