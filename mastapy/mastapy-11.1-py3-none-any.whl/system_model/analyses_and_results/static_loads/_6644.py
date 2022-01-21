'''_6644.py

OilSealLoadCase
'''


from mastapy.system_model.part_model import _2207
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6564
from mastapy._internal.python_net import python_net_import

_OIL_SEAL_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'OilSealLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('OilSealLoadCase',)


class OilSealLoadCase(_6564.ConnectorLoadCase):
    '''OilSealLoadCase

    This is a mastapy class.
    '''

    TYPE = _OIL_SEAL_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OilSealLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2207.OilSeal':
        '''OilSeal: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2207.OilSeal)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
