'''_1696.py

BearingStiffnessMatrixReporter
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.bearings.bearing_results import _1719
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_BEARING_STIFFNESS_MATRIX_REPORTER = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'BearingStiffnessMatrixReporter')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingStiffnessMatrixReporter',)


class BearingStiffnessMatrixReporter(_0.APIBase):
    '''BearingStiffnessMatrixReporter

    This is a mastapy class.
    '''

    TYPE = _BEARING_STIFFNESS_MATRIX_REPORTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingStiffnessMatrixReporter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_radial_stiffness(self) -> 'float':
        '''float: 'MaximumRadialStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumRadialStiffness

    @property
    def minimum_radial_stiffness(self) -> 'float':
        '''float: 'MinimumRadialStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumRadialStiffness

    @property
    def radial_stiffness_variation(self) -> 'float':
        '''float: 'RadialStiffnessVariation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadialStiffnessVariation

    @property
    def maximum_tilt_stiffness(self) -> 'float':
        '''float: 'MaximumTiltStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumTiltStiffness

    @property
    def minimum_tilt_stiffness(self) -> 'float':
        '''float: 'MinimumTiltStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumTiltStiffness

    @property
    def tilt_stiffness_variation(self) -> 'float':
        '''float: 'TiltStiffnessVariation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TiltStiffnessVariation

    @property
    def axial_stiffness(self) -> 'float':
        '''float: 'AxialStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialStiffness

    @property
    def torsional_stiffness(self) -> 'float':
        '''float: 'TorsionalStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorsionalStiffness

    @property
    def stiffness_xx(self) -> 'float':
        '''float: 'StiffnessXX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessXX

    @property
    def stiffness_xy(self) -> 'float':
        '''float: 'StiffnessXY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessXY

    @property
    def stiffness_xz(self) -> 'float':
        '''float: 'StiffnessXZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessXZ

    @property
    def stiffness_x_theta_x(self) -> 'float':
        '''float: 'StiffnessXThetaX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessXThetaX

    @property
    def stiffness_x_theta_y(self) -> 'float':
        '''float: 'StiffnessXThetaY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessXThetaY

    @property
    def stiffness_x_theta_z(self) -> 'float':
        '''float: 'StiffnessXThetaZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessXThetaZ

    @property
    def stiffness_yx(self) -> 'float':
        '''float: 'StiffnessYX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessYX

    @property
    def stiffness_yy(self) -> 'float':
        '''float: 'StiffnessYY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessYY

    @property
    def stiffness_yz(self) -> 'float':
        '''float: 'StiffnessYZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessYZ

    @property
    def stiffness_y_theta_x(self) -> 'float':
        '''float: 'StiffnessYThetaX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessYThetaX

    @property
    def stiffness_y_theta_y(self) -> 'float':
        '''float: 'StiffnessYThetaY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessYThetaY

    @property
    def stiffness_y_theta_z(self) -> 'float':
        '''float: 'StiffnessYThetaZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessYThetaZ

    @property
    def stiffness_zx(self) -> 'float':
        '''float: 'StiffnessZX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessZX

    @property
    def stiffness_zy(self) -> 'float':
        '''float: 'StiffnessZY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessZY

    @property
    def stiffness_zz(self) -> 'float':
        '''float: 'StiffnessZZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessZZ

    @property
    def stiffness_z_theta_x(self) -> 'float':
        '''float: 'StiffnessZThetaX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessZThetaX

    @property
    def stiffness_z_theta_y(self) -> 'float':
        '''float: 'StiffnessZThetaY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessZThetaY

    @property
    def stiffness_z_theta_z(self) -> 'float':
        '''float: 'StiffnessZThetaZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessZThetaZ

    @property
    def stiffness_theta_xx(self) -> 'float':
        '''float: 'StiffnessThetaXX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaXX

    @property
    def stiffness_theta_xy(self) -> 'float':
        '''float: 'StiffnessThetaXY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaXY

    @property
    def stiffness_theta_xz(self) -> 'float':
        '''float: 'StiffnessThetaXZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaXZ

    @property
    def stiffness_theta_x_theta_x(self) -> 'float':
        '''float: 'StiffnessThetaXThetaX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaXThetaX

    @property
    def stiffness_theta_x_theta_y(self) -> 'float':
        '''float: 'StiffnessThetaXThetaY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaXThetaY

    @property
    def stiffness_theta_x_theta_z(self) -> 'float':
        '''float: 'StiffnessThetaXThetaZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaXThetaZ

    @property
    def stiffness_theta_yx(self) -> 'float':
        '''float: 'StiffnessThetaYX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaYX

    @property
    def stiffness_theta_yy(self) -> 'float':
        '''float: 'StiffnessThetaYY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaYY

    @property
    def stiffness_theta_yz(self) -> 'float':
        '''float: 'StiffnessThetaYZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaYZ

    @property
    def stiffness_theta_y_theta_x(self) -> 'float':
        '''float: 'StiffnessThetaYThetaX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaYThetaX

    @property
    def stiffness_theta_y_theta_y(self) -> 'float':
        '''float: 'StiffnessThetaYThetaY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaYThetaY

    @property
    def stiffness_theta_y_theta_z(self) -> 'float':
        '''float: 'StiffnessThetaYThetaZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaYThetaZ

    @property
    def stiffness_theta_zx(self) -> 'float':
        '''float: 'StiffnessThetaZX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaZX

    @property
    def stiffness_theta_zy(self) -> 'float':
        '''float: 'StiffnessThetaZY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaZY

    @property
    def stiffness_theta_zz(self) -> 'float':
        '''float: 'StiffnessThetaZZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaZZ

    @property
    def stiffness_theta_z_theta_x(self) -> 'float':
        '''float: 'StiffnessThetaZThetaX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaZThetaX

    @property
    def stiffness_theta_z_theta_y(self) -> 'float':
        '''float: 'StiffnessThetaZThetaY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaZThetaY

    @property
    def stiffness_theta_z_theta_z(self) -> 'float':
        '''float: 'StiffnessThetaZThetaZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessThetaZThetaZ

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def rows(self) -> 'List[_1719.StiffnessRow]':
        '''List[StiffnessRow]: 'Rows' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Rows, constructor.new(_1719.StiffnessRow))
        return value
