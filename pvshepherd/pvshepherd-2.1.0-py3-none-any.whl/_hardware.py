import os
import platform
from enum import Enum


class Microcontrollers(Enum):
    IMXRT = 'IMXRT'
    STM32 = 'STM32'


class Boards(Enum):
    IMXRT1050_EVKB = 'IMXRT1050-EVKB'
    STM32F407G_DISCO = 'STM32F407G-DISCO'
    STM32F411E_DISCO = 'STM32F411E-DISCO'
    STM32F469I_DISCO = 'STM32F469I-DISCO'
    STM32F769I_DISCO = 'STM32F769I-DISCO'
    STM32H735G_DK = 'STM32H735G-DK'
    STM32H747I_DISCO = 'STM32H747I-DISCO'


_BOARD_TO_MCU = {
    Boards.IMXRT1050_EVKB: Microcontrollers.IMXRT,
    Boards.STM32F407G_DISCO: Microcontrollers.STM32,
    Boards.STM32F411E_DISCO: Microcontrollers.STM32,
    Boards.STM32F469I_DISCO: Microcontrollers.STM32,
    Boards.STM32F769I_DISCO: Microcontrollers.STM32,
    Boards.STM32H735G_DK: Microcontrollers.STM32,
    Boards.STM32H747I_DISCO: Microcontrollers.STM32,
}


assert len(_BOARD_TO_MCU) == len(Boards)


def board_tools_folder(board):
    mcu = _BOARD_TO_MCU[board]

    if mcu is Microcontrollers.IMXRT:
        if platform.system() == 'Linux':
            return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'thirdparty/nxp/linux/binaries')
        elif platform.system() == 'Darwin':
            return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'thirdparty/nxp/mac/binaries')
        elif platform.system() == 'Windows':
            return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'thirdparty/nxp/win/binaries')
        else:
            raise ValueError("Unsupported host platform '%s'" % platform.system())
    elif mcu is Microcontrollers.STM32:
        if platform.system() == 'Linux':
            return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'thirdparty/st/linux/bin')
        elif platform.system() == 'Darwin':
            return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'thirdparty/st/mac/bin')
        elif platform.system() == 'Windows':
            return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'thirdparty/st/win/bin')
        else:
            raise ValueError("Unsupported host platform '%s'" % platform.system())

    else:
        raise ValueError("Unsupported microcontroller '%s'", str(mcu))
