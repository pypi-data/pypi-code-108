import argparse
import logging
import os
import subprocess
from enum import Enum


from ._hardware import Boards
from ._hardware import board_tools_folder


class Languages(Enum):
    English = 'en',
    German = 'de'


DEBUG = False

log = logging.getLogger('firmware')
log.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

subprocess_run_kwargs = dict(shell=True, stderr=subprocess.STDOUT)
if not DEBUG:
    subprocess_run_kwargs['stdout'] = subprocess.DEVNULL


def _upload_firmware_imxrt1050(language, num_retries=3):
    tools_folder = board_tools_folder(Boards.IMXRT1050_EVKB)
    programmer_path = os.path.join(tools_folder, 'crt_emu_cm_redlink')

    args = (programmer_path, tools_folder)
    command = '%s --connect -l -g --vendor NXP -p MIMXRT1052xxxxB --ConnectScript RT1050_connect.scp -x %s' % args
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'Chip Setup Complete' not in res:
        raise RuntimeError("Failed to connect to the board")

    for _ in range(num_retries):
        firmware_path = \
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'firmware/imxrt1050-evkb-demo-%s.axf' % language)
        args = (programmer_path, firmware_path, tools_folder)
        command = \
            '%s --flash-load-exec %s -g --vendor NXP -p MIMXRT1052xxxxB --ConnectScript RT1050_connect.scp -x %s ' \
            '-ProbeHandle=1 -CoreIndex=0 --flash-hashing' % args
        log.debug(command)

        if subprocess.run(command, **subprocess_run_kwargs).returncode == 0:
            return

    raise RuntimeError("Failed to upload the firmware to the board after %d retries" % num_retries)


def _upload_firmware_stm32f469(language):
    tools_folder = board_tools_folder(Boards.STM32F469I_DISCO)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'stm32f469' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    firmware_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'firmware/stm32f469i-disco-demo-%s.elf' % language)
    command = '%s --connect port=SWD ap=0 -w %s -hardRst' % (programmer_path, firmware_path)
    log.debug(command)

    if subprocess.run(command, **subprocess_run_kwargs).returncode != 0:
        raise RuntimeError("Failed to upload the firmware to the board")


def _upload_firmware_stm32f769(language):
    tools_folder = board_tools_folder(Boards.STM32F769I_DISCO)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'stm32f76x' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    firmware_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'firmware/stm32f769i-disco-demo-%s.elf' % language)
    command = '%s --connect port=SWD ap=0 -w %s -hardRst' % (programmer_path, firmware_path)
    log.debug(command)

    if subprocess.run(command, **subprocess_run_kwargs).returncode != 0:
        raise RuntimeError("Failed to upload the firmware to the board")


def _upload_firmware_stm32h735(language):
    tools_folder = board_tools_folder(Boards.STM32H735G_DK)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'stm32h73x' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    firmware_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'firmware/stm32h735g-dk-demo-%s.elf' % language)
    command = '%s --connect port=SWD ap=0 -w %s -hardRst' % (programmer_path, firmware_path)
    log.debug(command)

    if subprocess.run(command, **subprocess_run_kwargs).returncode != 0:
        raise RuntimeError("Failed to upload the firmware to the board")


def _upload_firmware_stm32f407(language):
    tools_folder = board_tools_folder(Boards.STM32F407G_DISCO)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'f407xx' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    firmware_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'firmware/stm32f407g-disc1-demo-%s.elf' % language)
    command = '%s --connect port=SWD ap=0 -w %s -hardRst' % (programmer_path, firmware_path)
    log.debug(command)

    if subprocess.run(command, **subprocess_run_kwargs).returncode != 0:
        raise RuntimeError("Failed to upload the firmware to the board")


def _upload_firmware_stm32f411(language):
    tools_folder = board_tools_folder(Boards.STM32F411E_DISCO)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'f411x' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    firmware_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'firmware/stm32f411e-disco-demo-%s.elf' % language)
    command = '%s --connect port=SWD ap=0 -w %s -hardRst' % (programmer_path, firmware_path)
    log.debug(command)

    if subprocess.run(command, **subprocess_run_kwargs).returncode != 0:
        raise RuntimeError("Failed to upload the firmware to the board")


def _upload_firmware_stm32h747(language):
    tools_folder = board_tools_folder(Boards.STM32H747I_DISCO)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    # NOTE: 0x818 is hard-coded in the linker script of demo project.
    command = '%s --connect port=SWD ap=3 -ob BOOT_CM4_ADD0=0x818' % programmer_path
    log.debug(command)

    if subprocess.run(command, **subprocess_run_kwargs).returncode != 0:
        raise RuntimeError("Failed to partition the board")

    command = '%s --connect port=SWD ap=0 --erase all' % programmer_path
    log.debug(command)

    if subprocess.run(command, **subprocess_run_kwargs).returncode != 0:
        raise RuntimeError("Failed to mass erase")

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'stm32h747' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    firmware_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'firmware/stm32h747i-disco-demo_CM7-%s.elf' % language)
    command = '%s --connect port=SWD ap=3 -w %s -hardRst' % (programmer_path, firmware_path)
    log.debug(command)

    if subprocess.run(command, **subprocess_run_kwargs).returncode != 0:
        raise RuntimeError("Failed to upload the firmware to the board")


def upload_firmware(board, language):
    if board is Boards.IMXRT1050_EVKB:
        _upload_firmware_imxrt1050(language)
    elif board is Boards.STM32F407G_DISCO:
        _upload_firmware_stm32f407(language)
    elif board is Boards.STM32F411E_DISCO:
        _upload_firmware_stm32f411(language)
    elif board is Boards.STM32F469I_DISCO:
        _upload_firmware_stm32f469(language)
    elif board is Boards.STM32F769I_DISCO:
        _upload_firmware_stm32f769(language)
    elif board is Boards.STM32H747I_DISCO:
        _upload_firmware_stm32h747(language)
    elif board is Boards.STM32H735G_DK:
        _upload_firmware_stm32h735(language)
    else:
        raise ValueError("Unsupported board '%s'" % str(board))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board', choices=[x.value for x in Boards], required=True)
    parser.add_argument('--language', choices=[x.value for x in Languages], required=True)
    args = parser.parse_args()

    upload_firmware(Boards(args.board), Languages(args.language))


if __name__ == '__main__':
    main()
