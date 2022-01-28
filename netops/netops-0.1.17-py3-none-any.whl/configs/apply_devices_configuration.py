import json
import os

from nornir.core.exceptions import ConnectionNotOpen, NornirExecutionError
from nornir_pyez.plugins.tasks import pyez_config, pyez_diff, pyez_commit
from nornir_utils.plugins.functions import print_result
from contextlib import redirect_stdout
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import LockError
from jnpr.junos.exception import RpcError
from jnpr.junos.exception import CommitError
from jnpr.junos.exception import UnlockError

from ..utils.utils import print_json, remove_empty_lines
from ..api.netbox.netbox_manager import NetboxManager
from ..api.netbox.util import get_sot_filter_parameters


EXECUTION_STATUS = {
    'FAILED': 'failed',
    'INITIAL': 'no-changes',
    'ROLLBACK': 'rollback',
    'SUCCESSFULL': 'successfull',
}

def try_apply_config(config_file_path, retries=3, check_params=None, commit=False):
    """
	TODO: write docstrings
	"""

    diff_file = '/tmp/show_compare.txt'
    ntry = 1 # number of exec try
    while ntry <= int(retries):
        # Necessario que as funcoes raise_on_error estejam funcionais para a checagem de tentativas funcionarem
        exec_status = apply_config(config_file_path, diff_file=diff_file, check_params=check_params, commit=commit)
        if exec_status == EXECUTION_STATUS['SUCCESSFULL'] or exec_status == EXECUTION_STATUS['ROLLBACK']:
            break
        ntry += 1
    
    if commit:
        dev_config = json.load(fp=open(config_file_path, "r"))
        for sequencial_task in dev_config["sequential"]:
            for config in sequencial_task["configuration"]:
                if config["metadata"]["commited"] == "nok":
                    print(f"Error configuring devices after {retries} retries")
                    exit(1)

    if exec_status == EXECUTION_STATUS['FAILED']:
        print("Configuration apply has FAILED!")
        exit(1)
    elif exec_status == EXECUTION_STATUS['ROLLBACK']:
        print("Configuration databases has been ROLLBACKED! Please, check what happened in previous tests!")
        exit(1)
 
    return


def apply_config(config_file_path, diff_file, check_params, commit):
    """
	TODO: write docstrings
	"""

    # exec_status represents the execution status
    try:
        filter_params = get_sot_filter_parameters()
        netbox_manager = NetboxManager(filter_params=filter_params)

        dev_config = json.load(fp=open(config_file_path, "r"))
        
        stc = 0 #sequential task counter
        for sequencial_task in dev_config["sequential"]:
            device_name = sequencial_task["device_name"]
            host = netbox_manager.get_nornir().filter(name=device_name)
            
            cc = 0 # configuration counter
            for config in sequencial_task["configuration"]:
                dev_config["sequential"][stc]["configuration"][cc]
                if config["metadata"]["commited"] == "nok":
                    if config["type"] == "procedural":
                        payload = None
                        for statement in config["content"]:
                            if payload:
                                payload = payload + os.linesep + str(statement)
                            else:
                                payload = str(statement)
                        if 'rollback ' in payload:
                            print("----------------- ROLLING BACK... -----------------")
                            junos_rollback(host, device_name)
                            # Somente e executado se nao for gerado erro de configuracao
                            dev_config["sequential"][stc]["configuration"][cc]["metadata"]["commited"] = "ok"
                            # A cada iteracao o estado do dev_config e gravado para que em erros subsequentes o estado seja armazenado
                            print_json(dev_config, config_file_path)
                            print("################################# Printando dev_config apos commit... #############################")
                            print_json(dev_config)
                            exec_status = EXECUTION_STATUS['ROLLBACK']
                            break

                        config_response = host.run(
                            task=pyez_config, payload=payload, data_format="set")
                        print_result(config_response)
                        config_response.raise_on_error()
                        diff_response = host.run(task=pyez_diff)
                        diff_response.raise_on_error()
                        #print_result(diff_response)
                        with open(diff_file, 'w') as file:  # Use file to refer to the file object
                            with redirect_stdout(file):
                                print_result(diff_response)
                        remove_empty_lines(diff_file)
                        check_config(diff_file, check_params)
                        exec_status = EXECUTION_STATUS['SUCCESSFULL']

                        # COMMIT----------------------------
                        if commit:
                            #print_result(diff_response)
                            print("----------------- COMMITING CHANGES... -----------------")
                            commit_response = host.run(task=pyez_commit)
                            commit_response.raise_on_error()
                            # Somente e executado se nao for gerado erro de configuracao
                            dev_config["sequential"][stc]["configuration"][cc]["metadata"]["commited"] = "ok"
                            # A cada iteracao o estado do dev_config e gravado para que em erros subsequentes o estado seja armazenado
                            print_json(dev_config, config_file_path)
                            print("################################# Printando dev_config apos commit... #############################")
                            print_json(dev_config)
                            exec_status = EXECUTION_STATUS['SUCCESSFULL']
                        # ------------------------------------

                    if config["type"] == "json-rpc":
                        host = netbox_manager.get_nornir().filter(name=device_name)
                        payload = str(config["content"])
                        config_response = host.run(
                            task=pyez_config, payload=payload, data_format="text")
                        print_result(config_response)
                        #config_response.raise_on_error()
                        diff_response = host.run(task=pyez_diff)
                        #diff_response.raise_on_error()
                        print_result(diff_response)
                        # COMMIT----------------------------
                        if commit:
                            print("----------------- COMMITING CHANGES... -----------------")
                            commit_response = host.run(task=pyez_commit)
                            #commit_response.raise_on_error()
                            # Somente e executado se nao for gerado erro de configuracao
                            dev_config["sequential"][stc]["configuration"][cc]["metadata"]["commited"] = "ok"
                            # A cada iteracao o estado do dev_config e gravado para que em erros subsequentes o estado seja armazenado
                            print_json(dev_config, config_file_path)
                            print("################################# Printando dev_config apos commit... #############################")
                            print_json(dev_config)
                        # ------------------------------------
                cc += 1
            host.close_connections()
            stc += 1
        
        print_json(dev_config, config_file_path)

    except NornirExecutionError as e:
        exec_status = EXECUTION_STATUS['FAILED']
        print("Error NornirExecutionError !", str(e))
        try:
            host.close_connections()
        except ConnectionNotOpen as e:
            print("Error ConnectionNotOpen !", str(e))
        #Nao utilizado quando realizando multiplas tentativas de execucao
        #exit(1)
    except Exception as e:
        exec_status = EXECUTION_STATUS['FAILED']
        print("Error!", str(e))

    return exec_status


def check_config(diff_file, check_params):
    """
	TODO: write docstrings
	"""

    with open(diff_file, 'r') as file:  # Use file to refer to the file object
        lines = file.readlines()
        for line in lines:
            print(line.strip('\n'))
            if check_params:
                for param in check_params:
                    if param in line:
                        print("")
                        print("ERRO! Parametro indevido encontrado no DIFF result. Favor verificar.")
                        exit(1)
    
    return


def junos_rollback(host, device_name, rb_id=1):
    """
	TODO: write docstrings
	"""
    
    dev = Device(
        host=host.inventory.hosts[device_name].hostname, 
        user=host.inventory.hosts[device_name].username, 
        passwd=host.inventory.hosts[device_name].password,
        port=host.inventory.hosts[device_name].port
    )
    # open a connection with the device and start a NETCONF session
    try:
        dev.open()
    except ConnectError as err:
        print ("Cannot connect to device: {0}".format(err))
        return

    # Set up config object
    cu = Config(dev)

    # Lock the configuration
    print ("Locking the configuration")
    try:
        cu.lock()
    except LockError as err:
        print ("Unable to lock configuration: {0}".format(err))
        dev.close()
        return
    try:
        print ("Rolling back the configuration")
        cu.rollback(rb_id=rb_id)
        print ("Committing the configuration")
        cu.commit()
    except CommitError as err:
        print ("Error: Unable to commit configuration: {0}".format(err))
    except RpcError as err:
        print ("Unable to roll back configuration changes: {0}".format(err))

    finally:
        print ("Unlocking the configuration")
        try:
            cu.unlock()
        except UnlockError as err:
            print ("Unable to unlock configuration: {0}".format(err))
        dev.close()
        return