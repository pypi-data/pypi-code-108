'''_595.py

MicroGeometryInputsProfile
'''


from mastapy._internal import constructor
from mastapy.math_utility import _1287
from mastapy.math_utility.measured_ranges import _1364
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.cylindrical import _593, _597
from mastapy._internal.python_net import python_net_import

_MICRO_GEOMETRY_INPUTS_PROFILE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical', 'MicroGeometryInputsProfile')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryInputsProfile',)


class MicroGeometryInputsProfile(_593.MicroGeometryInputs['_597.ProfileModificationSegment']):
    '''MicroGeometryInputsProfile

    This is a mastapy class.
    '''

    TYPE = _MICRO_GEOMETRY_INPUTS_PROFILE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MicroGeometryInputsProfile.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def z_plane(self) -> 'float':
        '''float: 'ZPlane' is the original name of this property.'''

        return self.wrapped.ZPlane

    @z_plane.setter
    def z_plane(self, value: 'float'):
        self.wrapped.ZPlane = float(value) if value else 0.0

    @property
    def profile_micro_geometry_range(self) -> '_1287.Range':
        '''Range: 'ProfileMicroGeometryRange' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1287.Range.TYPE not in self.wrapped.ProfileMicroGeometryRange.__class__.__mro__:
            raise CastException('Failed to cast profile_micro_geometry_range to Range. Expected: {}.'.format(self.wrapped.ProfileMicroGeometryRange.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ProfileMicroGeometryRange.__class__)(self.wrapped.ProfileMicroGeometryRange) if self.wrapped.ProfileMicroGeometryRange is not None else None

    @property
    def number_of_profile_segments(self) -> 'int':
        '''int: 'NumberOfProfileSegments' is the original name of this property.'''

        return self.wrapped.NumberOfProfileSegments

    @number_of_profile_segments.setter
    def number_of_profile_segments(self, value: 'int'):
        self.wrapped.NumberOfProfileSegments = int(value) if value else 0
