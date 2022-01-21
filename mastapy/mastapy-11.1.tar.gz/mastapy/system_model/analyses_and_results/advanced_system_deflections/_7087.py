'''_7087.py

RootAssemblyAdvancedSystemDeflection
'''


from mastapy.system_model.part_model import _2215
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _6991, _6997
from mastapy._internal.python_net import python_net_import

_ROOT_ASSEMBLY_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'RootAssemblyAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('RootAssemblyAdvancedSystemDeflection',)


class RootAssemblyAdvancedSystemDeflection(_6997.AssemblyAdvancedSystemDeflection):
    '''RootAssemblyAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _ROOT_ASSEMBLY_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RootAssemblyAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2215.RootAssembly':
        '''RootAssembly: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2215.RootAssembly)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def advanced_system_deflection_inputs(self) -> '_6991.AdvancedSystemDeflection':
        '''AdvancedSystemDeflection: 'AdvancedSystemDeflectionInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6991.AdvancedSystemDeflection)(self.wrapped.AdvancedSystemDeflectionInputs) if self.wrapped.AdvancedSystemDeflectionInputs is not None else None
