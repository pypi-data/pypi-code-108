'''_6583.py

DatumLoadCase
'''


from mastapy.system_model.part_model import _2190
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6551
from mastapy._internal.python_net import python_net_import

_DATUM_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'DatumLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('DatumLoadCase',)


class DatumLoadCase(_6551.ComponentLoadCase):
    '''DatumLoadCase

    This is a mastapy class.
    '''

    TYPE = _DATUM_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DatumLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2190.Datum':
        '''Datum: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2190.Datum)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
