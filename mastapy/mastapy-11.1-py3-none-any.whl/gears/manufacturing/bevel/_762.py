'''_762.py

PinionBevelGeneratingTiltMachineSettings
'''


from mastapy.gears.manufacturing.bevel import _766
from mastapy._internal.python_net import python_net_import

_PINION_BEVEL_GENERATING_TILT_MACHINE_SETTINGS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'PinionBevelGeneratingTiltMachineSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('PinionBevelGeneratingTiltMachineSettings',)


class PinionBevelGeneratingTiltMachineSettings(_766.PinionFinishMachineSettings):
    '''PinionBevelGeneratingTiltMachineSettings

    This is a mastapy class.
    '''

    TYPE = _PINION_BEVEL_GENERATING_TILT_MACHINE_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PinionBevelGeneratingTiltMachineSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
