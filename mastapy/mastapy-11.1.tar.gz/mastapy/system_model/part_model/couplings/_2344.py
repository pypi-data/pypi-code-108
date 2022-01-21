'''_2344.py

SynchroniserHalf
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model.couplings import _2343, _2345
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'SynchroniserHalf')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserHalf',)


class SynchroniserHalf(_2345.SynchroniserPart):
    '''SynchroniserHalf

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_HALF

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserHalf.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def cone_side(self) -> 'str':
        '''str: 'ConeSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ConeSide

    @property
    def blocker_chamfer_angle(self) -> 'float':
        '''float: 'BlockerChamferAngle' is the original name of this property.'''

        return self.wrapped.BlockerChamferAngle

    @blocker_chamfer_angle.setter
    def blocker_chamfer_angle(self, value: 'float'):
        self.wrapped.BlockerChamferAngle = float(value) if value else 0.0

    @property
    def blocker_chamfer_pcd(self) -> 'float':
        '''float: 'BlockerChamferPCD' is the original name of this property.'''

        return self.wrapped.BlockerChamferPCD

    @blocker_chamfer_pcd.setter
    def blocker_chamfer_pcd(self, value: 'float'):
        self.wrapped.BlockerChamferPCD = float(value) if value else 0.0

    @property
    def blocker_chamfer_coefficient_of_friction(self) -> 'float':
        '''float: 'BlockerChamferCoefficientOfFriction' is the original name of this property.'''

        return self.wrapped.BlockerChamferCoefficientOfFriction

    @blocker_chamfer_coefficient_of_friction.setter
    def blocker_chamfer_coefficient_of_friction(self, value: 'float'):
        self.wrapped.BlockerChamferCoefficientOfFriction = float(value) if value else 0.0

    @property
    def diameter(self) -> 'float':
        '''float: 'Diameter' is the original name of this property.'''

        return self.wrapped.Diameter

    @diameter.setter
    def diameter(self, value: 'float'):
        self.wrapped.Diameter = float(value) if value else 0.0

    @property
    def total_area_of_cones(self) -> 'float':
        '''float: 'TotalAreaOfCones' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalAreaOfCones

    @property
    def area_of_cone_with_minimum_area(self) -> 'float':
        '''float: 'AreaOfConeWithMinimumArea' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AreaOfConeWithMinimumArea

    @property
    def number_of_surfaces(self) -> 'int':
        '''int: 'NumberOfSurfaces' is the original name of this property.'''

        return self.wrapped.NumberOfSurfaces

    @number_of_surfaces.setter
    def number_of_surfaces(self, value: 'int'):
        self.wrapped.NumberOfSurfaces = int(value) if value else 0

    @property
    def bore(self) -> 'float':
        '''float: 'Bore' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Bore

    @property
    def cones(self) -> 'List[_2343.SynchroniserCone]':
        '''List[SynchroniserCone]: 'Cones' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Cones, constructor.new(_2343.SynchroniserCone))
        return value
