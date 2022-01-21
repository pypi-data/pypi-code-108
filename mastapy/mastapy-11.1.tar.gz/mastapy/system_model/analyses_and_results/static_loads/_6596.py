'''_6596.py

ElectricMachineHarmonicLoadJMAGImportOptions
'''


from mastapy.system_model.analyses_and_results.static_loads import _6595
from mastapy._internal.python_net import python_net_import

_ELECTRIC_MACHINE_HARMONIC_LOAD_JMAG_IMPORT_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'ElectricMachineHarmonicLoadJMAGImportOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('ElectricMachineHarmonicLoadJMAGImportOptions',)


class ElectricMachineHarmonicLoadJMAGImportOptions(_6595.ElectricMachineHarmonicLoadImportOptionsBase):
    '''ElectricMachineHarmonicLoadJMAGImportOptions

    This is a mastapy class.
    '''

    TYPE = _ELECTRIC_MACHINE_HARMONIC_LOAD_JMAG_IMPORT_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElectricMachineHarmonicLoadJMAGImportOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
