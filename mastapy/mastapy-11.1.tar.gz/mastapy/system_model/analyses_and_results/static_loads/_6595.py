'''_6595.py

ElectricMachineHarmonicLoadImportOptionsBase
'''


from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ELECTRIC_MACHINE_HARMONIC_LOAD_IMPORT_OPTIONS_BASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'ElectricMachineHarmonicLoadImportOptionsBase')


__docformat__ = 'restructuredtext en'
__all__ = ('ElectricMachineHarmonicLoadImportOptionsBase',)


class ElectricMachineHarmonicLoadImportOptionsBase(_0.APIBase):
    '''ElectricMachineHarmonicLoadImportOptionsBase

    This is a mastapy class.
    '''

    TYPE = _ELECTRIC_MACHINE_HARMONIC_LOAD_IMPORT_OPTIONS_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElectricMachineHarmonicLoadImportOptionsBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
