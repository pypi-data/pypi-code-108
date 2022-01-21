'''_2585.py

SplineFlankContactReporting
'''


from mastapy._internal import constructor, conversion
from mastapy._math.vector_3d import Vector3D
from mastapy.math_utility.measured_vectors import _1363
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SPLINE_FLANK_CONTACT_REPORTING = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Reporting', 'SplineFlankContactReporting')


__docformat__ = 'restructuredtext en'
__all__ = ('SplineFlankContactReporting',)


class SplineFlankContactReporting(_0.APIBase):
    '''SplineFlankContactReporting

    This is a mastapy class.
    '''

    TYPE = _SPLINE_FLANK_CONTACT_REPORTING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SplineFlankContactReporting.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def entity_name(self) -> 'str':
        '''str: 'EntityName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EntityName

    @property
    def angle(self) -> 'float':
        '''float: 'Angle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Angle

    @property
    def relative_deflection_misalignment(self) -> 'float':
        '''float: 'RelativeDeflectionMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeDeflectionMisalignment

    @property
    def normal_deflection(self) -> 'float':
        '''float: 'NormalDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalDeflection

    @property
    def tangential_deflection(self) -> 'float':
        '''float: 'TangentialDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialDeflection

    @property
    def normal_stiffness(self) -> 'float':
        '''float: 'NormalStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalStiffness

    @property
    def tangential_stiffness(self) -> 'float':
        '''float: 'TangentialStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialStiffness

    @property
    def normal_force(self) -> 'float':
        '''float: 'NormalForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalForce

    @property
    def tangential_force(self) -> 'float':
        '''float: 'TangentialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialForce

    @property
    def surface_penetration(self) -> 'float':
        '''float: 'SurfacePenetration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePenetration

    @property
    def tilt_moment(self) -> 'float':
        '''float: 'TiltMoment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TiltMoment

    @property
    def contact_position_wcs(self) -> 'Vector3D':
        '''Vector3D: 'ContactPositionWCS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.ContactPositionWCS)
        return value

    @property
    def contact_position_lcs(self) -> 'Vector3D':
        '''Vector3D: 'ContactPositionLCS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.ContactPositionLCS)
        return value

    @property
    def normal_direction_wcs(self) -> 'Vector3D':
        '''Vector3D: 'NormalDirectionWCS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.NormalDirectionWCS)
        return value

    @property
    def normal_direction_lcs(self) -> 'Vector3D':
        '''Vector3D: 'NormalDirectionLCS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.NormalDirectionLCS)
        return value

    @property
    def relative_deflection_wcs(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'RelativeDeflectionWCS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.RelativeDeflectionWCS) if self.wrapped.RelativeDeflectionWCS is not None else None

    @property
    def relative_deflection_lcs(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'RelativeDeflectionLCS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.RelativeDeflectionLCS) if self.wrapped.RelativeDeflectionLCS is not None else None

    @property
    def force_on_inner_wcs(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'ForceOnInnerWCS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.ForceOnInnerWCS) if self.wrapped.ForceOnInnerWCS is not None else None

    @property
    def force_on_inner_contact_coordinate_system(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'ForceOnInnerContactCoordinateSystem' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.ForceOnInnerContactCoordinateSystem) if self.wrapped.ForceOnInnerContactCoordinateSystem is not None else None
