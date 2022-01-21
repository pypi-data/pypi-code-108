'''_6589.py

ElectricMachineHarmonicLoadDataFromFlux
'''


from mastapy.system_model.analyses_and_results.static_loads import _6592, _6594
from mastapy._internal.python_net import python_net_import

_ELECTRIC_MACHINE_HARMONIC_LOAD_DATA_FROM_FLUX = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'ElectricMachineHarmonicLoadDataFromFlux')


__docformat__ = 'restructuredtext en'
__all__ = ('ElectricMachineHarmonicLoadDataFromFlux',)


class ElectricMachineHarmonicLoadDataFromFlux(_6592.ElectricMachineHarmonicLoadDataFromMotorPackages['_6594.ElectricMachineHarmonicLoadFluxImportOptions']):
    '''ElectricMachineHarmonicLoadDataFromFlux

    This is a mastapy class.
    '''

    TYPE = _ELECTRIC_MACHINE_HARMONIC_LOAD_DATA_FROM_FLUX

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElectricMachineHarmonicLoadDataFromFlux.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
