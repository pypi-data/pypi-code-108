'''_6647.py

PartToPartShearCouplingConnectionLoadCase
'''


from mastapy.system_model.connections_and_sockets.couplings import _2090
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6565
from mastapy._internal.python_net import python_net_import

_PART_TO_PART_SHEAR_COUPLING_CONNECTION_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'PartToPartShearCouplingConnectionLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('PartToPartShearCouplingConnectionLoadCase',)


class PartToPartShearCouplingConnectionLoadCase(_6565.CouplingConnectionLoadCase):
    '''PartToPartShearCouplingConnectionLoadCase

    This is a mastapy class.
    '''

    TYPE = _PART_TO_PART_SHEAR_COUPLING_CONNECTION_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartToPartShearCouplingConnectionLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2090.PartToPartShearCouplingConnection':
        '''PartToPartShearCouplingConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2090.PartToPartShearCouplingConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None
