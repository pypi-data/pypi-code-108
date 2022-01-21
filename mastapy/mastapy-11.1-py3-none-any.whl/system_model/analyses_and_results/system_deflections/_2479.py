'''_2479.py

CylindricalGearSetSystemDeflectionWithLTCAResults
'''


from mastapy.gears.ltca.cylindrical import _820, _822
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.system_deflections import _2477
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_SYSTEM_DEFLECTION_WITH_LTCA_RESULTS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'CylindricalGearSetSystemDeflectionWithLTCAResults')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetSystemDeflectionWithLTCAResults',)


class CylindricalGearSetSystemDeflectionWithLTCAResults(_2477.CylindricalGearSetSystemDeflection):
    '''CylindricalGearSetSystemDeflectionWithLTCAResults

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_SYSTEM_DEFLECTION_WITH_LTCA_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetSystemDeflectionWithLTCAResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def basic_ltca_results(self) -> '_820.CylindricalGearSetLoadDistributionAnalysis':
        '''CylindricalGearSetLoadDistributionAnalysis: 'BasicLTCAResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _820.CylindricalGearSetLoadDistributionAnalysis.TYPE not in self.wrapped.BasicLTCAResults.__class__.__mro__:
            raise CastException('Failed to cast basic_ltca_results to CylindricalGearSetLoadDistributionAnalysis. Expected: {}.'.format(self.wrapped.BasicLTCAResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BasicLTCAResults.__class__)(self.wrapped.BasicLTCAResults) if self.wrapped.BasicLTCAResults is not None else None

    @property
    def basic_ltca_results_only_first_planetary_mesh(self) -> '_820.CylindricalGearSetLoadDistributionAnalysis':
        '''CylindricalGearSetLoadDistributionAnalysis: 'BasicLTCAResultsOnlyFirstPlanetaryMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _820.CylindricalGearSetLoadDistributionAnalysis.TYPE not in self.wrapped.BasicLTCAResultsOnlyFirstPlanetaryMesh.__class__.__mro__:
            raise CastException('Failed to cast basic_ltca_results_only_first_planetary_mesh to CylindricalGearSetLoadDistributionAnalysis. Expected: {}.'.format(self.wrapped.BasicLTCAResultsOnlyFirstPlanetaryMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BasicLTCAResultsOnlyFirstPlanetaryMesh.__class__)(self.wrapped.BasicLTCAResultsOnlyFirstPlanetaryMesh) if self.wrapped.BasicLTCAResultsOnlyFirstPlanetaryMesh is not None else None

    @property
    def advanced_ltca_results(self) -> '_820.CylindricalGearSetLoadDistributionAnalysis':
        '''CylindricalGearSetLoadDistributionAnalysis: 'AdvancedLTCAResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _820.CylindricalGearSetLoadDistributionAnalysis.TYPE not in self.wrapped.AdvancedLTCAResults.__class__.__mro__:
            raise CastException('Failed to cast advanced_ltca_results to CylindricalGearSetLoadDistributionAnalysis. Expected: {}.'.format(self.wrapped.AdvancedLTCAResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AdvancedLTCAResults.__class__)(self.wrapped.AdvancedLTCAResults) if self.wrapped.AdvancedLTCAResults is not None else None

    @property
    def advanced_ltca_results_only_first_planetary_mesh(self) -> '_820.CylindricalGearSetLoadDistributionAnalysis':
        '''CylindricalGearSetLoadDistributionAnalysis: 'AdvancedLTCAResultsOnlyFirstPlanetaryMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _820.CylindricalGearSetLoadDistributionAnalysis.TYPE not in self.wrapped.AdvancedLTCAResultsOnlyFirstPlanetaryMesh.__class__.__mro__:
            raise CastException('Failed to cast advanced_ltca_results_only_first_planetary_mesh to CylindricalGearSetLoadDistributionAnalysis. Expected: {}.'.format(self.wrapped.AdvancedLTCAResultsOnlyFirstPlanetaryMesh.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AdvancedLTCAResultsOnlyFirstPlanetaryMesh.__class__)(self.wrapped.AdvancedLTCAResultsOnlyFirstPlanetaryMesh) if self.wrapped.AdvancedLTCAResultsOnlyFirstPlanetaryMesh is not None else None
