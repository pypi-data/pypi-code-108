# -*- coding: utf-8 -*-

import os
from shutil import which
from subprocess import call 

SCP_OPERATION_UPLOAD = "upload"
SCP_OPERATION_DOWNLOAD = "download"

def is_ssh_installed():
    return which("ssh") is not None

def is_scp_installed():
    return which("scp") is not None

def run(connection):
    if (is_ssh_installed()):
        cmd = connection.get_ssh_command()
        call(cmd)
    else:
        print('SSH is not available.')

def scp(connection):
    if (is_scp_installed()):
        cmd = connection.get_scp_command()
        call(cmd)
    else:
        print('SCP is not available.')
