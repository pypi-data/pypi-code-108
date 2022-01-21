'''_7031.py

CVTAdvancedSystemDeflection
'''


from mastapy.system_model.part_model.couplings import _2326
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7000
from mastapy._internal.python_net import python_net_import

_CVT_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'CVTAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTAdvancedSystemDeflection',)


class CVTAdvancedSystemDeflection(_7000.BeltDriveAdvancedSystemDeflection):
    '''CVTAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CVT_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2326.CVT':
        '''CVT: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2326.CVT)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None
