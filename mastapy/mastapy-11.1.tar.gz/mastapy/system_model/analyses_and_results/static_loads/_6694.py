'''_6694.py

TorqueConverterTurbineLoadCase
'''


from mastapy.system_model.part_model.couplings import _2350
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6566
from mastapy._internal.python_net import python_net_import

_TORQUE_CONVERTER_TURBINE_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'TorqueConverterTurbineLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueConverterTurbineLoadCase',)


class TorqueConverterTurbineLoadCase(_6566.CouplingHalfLoadCase):
    '''TorqueConverterTurbineLoadCase

    This is a mastapy class.
    '''

    TYPE = _TORQUE_CONVERTER_TURBINE_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorqueConverterTurbineLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2350.TorqueConverterTurbine':
        '''TorqueConverterTurbine: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2350.TorqueConverterTurbine)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
