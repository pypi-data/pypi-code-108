'''_5720.py

ElectricMachineRotorYMomentPeriodicExcitationDetail
'''


from mastapy.system_model.analyses_and_results.harmonic_analyses import _5716
from mastapy._internal.python_net import python_net_import

_ELECTRIC_MACHINE_ROTOR_Y_MOMENT_PERIODIC_EXCITATION_DETAIL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'ElectricMachineRotorYMomentPeriodicExcitationDetail')


__docformat__ = 'restructuredtext en'
__all__ = ('ElectricMachineRotorYMomentPeriodicExcitationDetail',)


class ElectricMachineRotorYMomentPeriodicExcitationDetail(_5716.ElectricMachinePeriodicExcitationDetail):
    '''ElectricMachineRotorYMomentPeriodicExcitationDetail

    This is a mastapy class.
    '''

    TYPE = _ELECTRIC_MACHINE_ROTOR_Y_MOMENT_PERIODIC_EXCITATION_DETAIL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElectricMachineRotorYMomentPeriodicExcitationDetail.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
