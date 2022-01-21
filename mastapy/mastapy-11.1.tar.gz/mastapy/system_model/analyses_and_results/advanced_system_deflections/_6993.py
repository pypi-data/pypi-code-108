'''_6993.py

AdvancedSystemDeflectionSubAnalysis
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.system_deflections import _2560
from mastapy._internal.python_net import python_net_import

_ADVANCED_SYSTEM_DEFLECTION_SUB_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'AdvancedSystemDeflectionSubAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AdvancedSystemDeflectionSubAnalysis',)


class AdvancedSystemDeflectionSubAnalysis(_2560.SystemDeflection):
    '''AdvancedSystemDeflectionSubAnalysis

    This is a mastapy class.
    '''

    TYPE = _ADVANCED_SYSTEM_DEFLECTION_SUB_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AdvancedSystemDeflectionSubAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def current_time(self) -> 'float':
        '''float: 'CurrentTime' is the original name of this property.'''

        return self.wrapped.CurrentTime

    @current_time.setter
    def current_time(self, value: 'float'):
        self.wrapped.CurrentTime = float(value) if value else 0.0
