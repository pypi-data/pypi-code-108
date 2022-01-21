'''_761.py

PinionBevelGeneratingModifiedRollMachineSettings
'''


from mastapy.gears.manufacturing.bevel import _766
from mastapy._internal.python_net import python_net_import

_PINION_BEVEL_GENERATING_MODIFIED_ROLL_MACHINE_SETTINGS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'PinionBevelGeneratingModifiedRollMachineSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('PinionBevelGeneratingModifiedRollMachineSettings',)


class PinionBevelGeneratingModifiedRollMachineSettings(_766.PinionFinishMachineSettings):
    '''PinionBevelGeneratingModifiedRollMachineSettings

    This is a mastapy class.
    '''

    TYPE = _PINION_BEVEL_GENERATING_MODIFIED_ROLL_MACHINE_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PinionBevelGeneratingModifiedRollMachineSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
