'''_876.py

MicroGeometryDesignSpaceSearch
'''


from typing import List

from mastapy._internal.implicit import list_with_selected_item
from mastapy.gears.ltca.cylindrical import (
    _817, _816, _820, _822
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1057
from mastapy.gears.gear_set_pareto_optimiser import _866, _877
from mastapy._internal.python_net import python_net_import

_MICRO_GEOMETRY_DESIGN_SPACE_SEARCH = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'MicroGeometryDesignSpaceSearch')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryDesignSpaceSearch',)


class MicroGeometryDesignSpaceSearch(_866.DesignSpaceSearchBase['_820.CylindricalGearSetLoadDistributionAnalysis', '_877.MicroGeometryDesignSpaceSearchCandidate']):
    '''MicroGeometryDesignSpaceSearch

    This is a mastapy class.
    '''

    TYPE = _MICRO_GEOMETRY_DESIGN_SPACE_SEARCH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MicroGeometryDesignSpaceSearch.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def select_mesh(self) -> 'list_with_selected_item.ListWithSelectedItem_CylindricalGearMeshLoadDistributionAnalysis':
        '''list_with_selected_item.ListWithSelectedItem_CylindricalGearMeshLoadDistributionAnalysis: 'SelectMesh' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_CylindricalGearMeshLoadDistributionAnalysis)(self.wrapped.SelectMesh) if self.wrapped.SelectMesh is not None else None

    @select_mesh.setter
    def select_mesh(self, value: 'list_with_selected_item.ListWithSelectedItem_CylindricalGearMeshLoadDistributionAnalysis.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_CylindricalGearMeshLoadDistributionAnalysis.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_CylindricalGearMeshLoadDistributionAnalysis.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.SelectMesh = value

    @property
    def select_gear(self) -> 'list_with_selected_item.ListWithSelectedItem_CylindricalGearLoadDistributionAnalysis':
        '''list_with_selected_item.ListWithSelectedItem_CylindricalGearLoadDistributionAnalysis: 'SelectGear' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_CylindricalGearLoadDistributionAnalysis)(self.wrapped.SelectGear) if self.wrapped.SelectGear is not None else None

    @select_gear.setter
    def select_gear(self, value: 'list_with_selected_item.ListWithSelectedItem_CylindricalGearLoadDistributionAnalysis.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_CylindricalGearLoadDistributionAnalysis.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_CylindricalGearLoadDistributionAnalysis.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.SelectGear = value

    @property
    def run_all_planetary_meshes(self) -> 'bool':
        '''bool: 'RunAllPlanetaryMeshes' is the original name of this property.'''

        return self.wrapped.RunAllPlanetaryMeshes

    @run_all_planetary_meshes.setter
    def run_all_planetary_meshes(self, value: 'bool'):
        self.wrapped.RunAllPlanetaryMeshes = bool(value) if value else False

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def load_case_duty_cycle(self) -> '_820.CylindricalGearSetLoadDistributionAnalysis':
        '''CylindricalGearSetLoadDistributionAnalysis: 'LoadCaseDutyCycle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _820.CylindricalGearSetLoadDistributionAnalysis.TYPE not in self.wrapped.LoadCaseDutyCycle.__class__.__mro__:
            raise CastException('Failed to cast load_case_duty_cycle to CylindricalGearSetLoadDistributionAnalysis. Expected: {}.'.format(self.wrapped.LoadCaseDutyCycle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LoadCaseDutyCycle.__class__)(self.wrapped.LoadCaseDutyCycle) if self.wrapped.LoadCaseDutyCycle is not None else None

    @property
    def selected_candidate_micro_geometry(self) -> '_1057.CylindricalGearSetMicroGeometry':
        '''CylindricalGearSetMicroGeometry: 'SelectedCandidateMicroGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1057.CylindricalGearSetMicroGeometry)(self.wrapped.SelectedCandidateMicroGeometry) if self.wrapped.SelectedCandidateMicroGeometry is not None else None

    @property
    def candidate_gear_sets(self) -> 'List[_1057.CylindricalGearSetMicroGeometry]':
        '''List[CylindricalGearSetMicroGeometry]: 'CandidateGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CandidateGearSets, constructor.new(_1057.CylindricalGearSetMicroGeometry))
        return value

    @property
    def all_candidate_gear_sets(self) -> 'List[_1057.CylindricalGearSetMicroGeometry]':
        '''List[CylindricalGearSetMicroGeometry]: 'AllCandidateGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AllCandidateGearSets, constructor.new(_1057.CylindricalGearSetMicroGeometry))
        return value

    def reset_charts(self):
        ''' 'ResetCharts' is the original name of this method.'''

        self.wrapped.ResetCharts()

    def add_chart(self):
        ''' 'AddChart' is the original name of this method.'''

        self.wrapped.AddChart()
