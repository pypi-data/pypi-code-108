'''_2482.py

CylindricalGearSystemDeflectionWithLTCAResults
'''


from mastapy.gears.ltca.cylindrical import _816
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.system_deflections import _2480
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SYSTEM_DEFLECTION_WITH_LTCA_RESULTS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'CylindricalGearSystemDeflectionWithLTCAResults')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSystemDeflectionWithLTCAResults',)


class CylindricalGearSystemDeflectionWithLTCAResults(_2480.CylindricalGearSystemDeflection):
    '''CylindricalGearSystemDeflectionWithLTCAResults

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SYSTEM_DEFLECTION_WITH_LTCA_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSystemDeflectionWithLTCAResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def cylindrical_gear_ltca_results(self) -> '_816.CylindricalGearLoadDistributionAnalysis':
        '''CylindricalGearLoadDistributionAnalysis: 'CylindricalGearLTCAResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_816.CylindricalGearLoadDistributionAnalysis)(self.wrapped.CylindricalGearLTCAResults) if self.wrapped.CylindricalGearLTCAResults is not None else None
