""" This module provide ssh and bash funcionallity"""
import paramiko
import logging
import os

_log = logging.getLogger('automation_tools.bash_utils')


def ssh_to_machine(host_name, user_name, password, port=22):
    """ This method create ssh connection to host """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host_name, port, user_name, password)
    except Exception as e:
        _log.error(f'Connection to {host_name} failed with error {str(e)}')
        return None
    # stdin, stdout, stderr = ssh.exec_command('service postgresql status')
    # lines = stdout.readlines()

    return ssh


def execute_command(ssh_conn, command):
    stdin, stdout, stderr = ssh_conn.exec_command(command)
    return stdin, stdout, stderr


def listen_to_port(host,port):
    res= os.system(f'nc -vz {host} {port}')
    if res==0:
        _log.info(f'success listen to kafka port:{host}:{port}')
        return True
    else:
        _log.error(f'Not success listen to kafka port:{host}:{port}')
        return False