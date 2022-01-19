import argparse
import logging
import os
import struct
import subprocess
import tempfile
import uuid

from ._hardware import Boards
from ._hardware import board_tools_folder

DEBUG = False

log = logging.getLogger('params')
log.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

subprocess_run_kwargs = dict(shell=True, stderr=subprocess.STDOUT)
if not DEBUG:
    subprocess_run_kwargs['stdout'] = subprocess.DEVNULL


def serialize_to_file(ppn_path, rhn_path, access_key, param_path):
    with open(ppn_path, 'rb') as f:
        ppn = f.read()

    with open(rhn_path, 'rb') as f:
        rhn = f.read()

    with open(param_path, 'wb') as f:
        f.write(struct.pack('i', len(ppn)))
        f.write(struct.pack('i', len(rhn)))
        f.write(struct.pack('i', len(access_key)))
        f.write(ppn)
        f.write(rhn)
        f.write(access_key.encode())
        f.write(b'\0')

def _upload_param_imxrt1050(param_path, num_retries=3):
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

    for i in range(num_retries):
        magic_address = '0x63fe0000'
        args = (programmer_path, param_path, tools_folder, magic_address)
        command = \
            '%s --flash-load-exec %s -g --vendor NXP -p MIMXRT1052xxxxB --ConnectScript RT1050_connect.scp -x %s ' \
            '--load-base=%s -ProbeHandle=1 -CoreIndex=0 --flash-hashing' % args
        log.debug(command)

        if subprocess.run(command, **subprocess_run_kwargs).returncode == 0:
            return

    raise RuntimeError("Failed to upload the params to the board")


def _upload_param_stm32f469(param_path):
    tools_folder = board_tools_folder(Boards.STM32F469I_DISCO)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'stm32f469' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    magic_address = '0x081e0000'
    command = '%s --connect port=SWD ap=0 -w %s %s -hardRst' % (programmer_path, param_path, magic_address)
    log.debug(command)

    res = subprocess.run(command, **subprocess_run_kwargs).returncode
    if res != 0:
        raise RuntimeError("Failed to upload the params to the board")

def _upload_param_stm32h735(param_path):
    tools_folder = board_tools_folder(Boards.STM32H735G_DK)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'stm32h73x' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    magic_address = '0x080e0000'
    command = '%s --connect port=SWD ap=0 -w %s %s -hardRst' % (programmer_path, param_path, magic_address)
    log.debug(command)

    res = subprocess.run(command, **subprocess_run_kwargs).returncode
    if res != 0:
        raise RuntimeError("Failed to upload the params to the board")


def _upload_param_stm32f769(param_path):
    tools_folder = board_tools_folder(Boards.STM32F769I_DISCO)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'stm32f76x' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    magic_address = '0x081e0000'
    command = '%s --connect port=SWD ap=0 -w %s %s -hardRst' % (programmer_path, param_path, magic_address)
    log.debug(command)

    res = subprocess.run(command, **subprocess_run_kwargs).returncode
    if res != 0:
        raise RuntimeError("Failed to upload the params to the board")

def _upload_param_stm32f407(param_path):
    tools_folder = board_tools_folder(Boards.STM32F407G_DISCO)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'f407' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    magic_address = '0x080e0000'
    command = '%s --connect port=SWD ap=0 -w %s %s -hardRst' % (programmer_path, param_path, magic_address)
    log.debug(command)

    res = subprocess.run(command, **subprocess_run_kwargs).returncode
    if res != 0:
        raise RuntimeError("Failed to upload the params to the board")


def _upload_param_stm32f411(param_path):
    tools_folder = board_tools_folder(Boards.STM32F411E_DISCO)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'f411x' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    magic_address = '0x08060000'
    command = '%s --connect port=SWD ap=0 -w %s %s -hardRst' % (programmer_path, param_path, magic_address)
    log.debug(command)

    res = subprocess.run(command, **subprocess_run_kwargs).returncode
    if res != 0:
        raise RuntimeError("Failed to upload the params to the board")


def _upload_param_stm32h747(param_path):
    tools_folder = board_tools_folder(Boards.STM32H747I_DISCO)
    programmer_path = os.path.join(tools_folder, 'STM32_Programmer_CLI')

    command = '%s --connect port=SWD ap=0' % programmer_path
    log.debug(command)

    res = subprocess.Popen(
        command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    log.debug(res)
    if 'stm32h747' not in res.lower():
        raise RuntimeError("Failed to connect to the board")

    magic_address = '0x08160000'
    command = '%s --connect port=SWD ap=3 -w %s %s -hardRst' % (programmer_path, param_path, magic_address)
    log.debug(command)

    res = subprocess.run(command, **subprocess_run_kwargs).returncode
    if res != 0:
        raise RuntimeError("Failed to upload the params to the board")


def upload_params(ppn_path, rhn_path, access_key, board):
    param_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()) + '.bin')
    serialize_to_file(ppn_path=ppn_path, rhn_path=rhn_path, access_key=access_key, param_path=param_path)

    try:
        if board is Boards.IMXRT1050_EVKB:
            _upload_param_imxrt1050(param_path)
        elif board is Boards.STM32F407G_DISCO:
            _upload_param_stm32f407(param_path)
        elif board is Boards.STM32F411E_DISCO:
            _upload_param_stm32f411(param_path)
        elif board is Boards.STM32F469I_DISCO:
            _upload_param_stm32f469(param_path)
        elif board is Boards.STM32F769I_DISCO:
            _upload_param_stm32f769(param_path)
        elif board is Boards.STM32H747I_DISCO:
            _upload_param_stm32h747(param_path)
        elif board is Boards.STM32H735G_DK:
            _upload_param_stm32h735(param_path)
        else:
            raise ValueError("Unsupported board '%s'" % str(board))
    finally:
        os.remove(param_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ppn_path', required=True)
    parser.add_argument('--rhn_path', required=True)
    parser.add_argument('--access_key', required=True)
    parser.add_argument('--param_path', default=None)
    parser.add_argument('--board', choices=[x.value for x in Boards], default=None)
    args = parser.parse_args()

    if args.board is not None:
        upload_params(
            ppn_path=args.ppn_path,
            rhn_path=args.rhn_path,
            access_key=args.access_key,
            board=Boards(args.board)
        )
    elif args.param_path is not None:
        serialize_to_file(
            ppn_path=args.ppn_path,
            rhn_path=args.rhn_path,
            access_key=args.access_key,
            param_path=args.param_path
        )
    else:
        raise ValueError()


if __name__ == '__main__':
    main()
