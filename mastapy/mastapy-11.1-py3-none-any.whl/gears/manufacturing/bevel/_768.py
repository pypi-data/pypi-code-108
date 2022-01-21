'''_768.py

PinionHypoidGeneratingTiltMachineSettings
'''


from mastapy.gears.manufacturing.bevel import _766
from mastapy._internal.python_net import python_net_import

_PINION_HYPOID_GENERATING_TILT_MACHINE_SETTINGS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'PinionHypoidGeneratingTiltMachineSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('PinionHypoidGeneratingTiltMachineSettings',)


class PinionHypoidGeneratingTiltMachineSettings(_766.PinionFinishMachineSettings):
    '''PinionHypoidGeneratingTiltMachineSettings

    This is a mastapy class.
    '''

    TYPE = _PINION_HYPOID_GENERATING_TILT_MACHINE_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PinionHypoidGeneratingTiltMachineSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
