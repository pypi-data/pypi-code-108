'''_2538.py

ShaftSectionSystemDeflection
'''


from mastapy.system_model.analyses_and_results.system_deflections import _2537
from mastapy._internal import constructor
from mastapy.nodal_analysis.nodal_entities import _121
from mastapy._internal.python_net import python_net_import

_SHAFT_SECTION_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'ShaftSectionSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftSectionSystemDeflection',)


class ShaftSectionSystemDeflection(_121.Bar):
    '''ShaftSectionSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _SHAFT_SECTION_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftSectionSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def left_end(self) -> '_2537.ShaftSectionEndResultsSystemDeflection':
        '''ShaftSectionEndResultsSystemDeflection: 'LeftEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2537.ShaftSectionEndResultsSystemDeflection)(self.wrapped.LeftEnd) if self.wrapped.LeftEnd is not None else None

    @property
    def right_end(self) -> '_2537.ShaftSectionEndResultsSystemDeflection':
        '''ShaftSectionEndResultsSystemDeflection: 'RightEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2537.ShaftSectionEndResultsSystemDeflection)(self.wrapped.RightEnd) if self.wrapped.RightEnd is not None else None
