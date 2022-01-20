from genie.conf.base import Device
from genie.libs.parser.utils import get_parser



class NoExecCli:
    """
    Replace cli object of Pyats to ensure that the command is not executed
    """
    def __init__(self):
        self.execute = None

def parse(cli_output, command, os, platform=None, model=None):
    """
    Parse and return structured cli output if PyATS support the command.
    Commands supported : https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers
    OS platform and model supported : https://developer.cisco.com/docs/unicon/
    It is inspired from : https://github.com/CiscoDevNet/ansible-pyats/blob/master/library/pyats_parse_command.py
    This function is a workaround to use PyATS parser library outside PyATS workflow which
    consist of declaring devices in a testbed and connect to device, execute command and parse output.
    :param cli_output: The raw cli output
    :param command: The command as it is entered on device ex "show interfaces"
    :param os: Mandatory ex : "ios", "iosxe", "iosxr"
    :param platform: Optionnal
    :param model: Optionnal (Warning no model without platform first)
    """

    order_tab = ["os"]
    if platform:
        order_tab.append("platform")
        if model:
            order_tab.append("model")

    fake_device = Device("fake", os=os, platform=platform, model=model)
    fake_device.custom.setdefault("abstraction", {})["order"] = order_tab
    fake_device.cli = NoExecCli()

    try:
        get_parser(command, fake_device)
    except Exception as e:
        raise Exception(
            f"Pyats parser unable to find an available parser for command '{command}' original exception : {e} ")

    try:
        structured_output = fake_device.parse(command, output=cli_output)
        return structured_output
    except Exception as e:
        raise Exception(f"Fail to parse command output {e}")