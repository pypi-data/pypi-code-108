import re
from dataclasses import dataclass
from datetime import datetime

from pyats_parser import parser

terminal_stderr_re_on_ios_device = [
    re.compile(r"% ?Error"),
    # re.compile(br"^% \w+", re.M),
    re.compile(r"% ?Bad secret"),
    re.compile(r"[\r\n%] Bad passwords"),
    re.compile(r"invalid input", re.I),
    re.compile(r"(?:incomplete|ambiguous) command", re.I),
    re.compile(r"connection timed out", re.I),
    re.compile(r"[^\r\n]+ not found"),
    re.compile(r"'[^']' +returned error code: ?\d+"),
    re.compile(r"Bad mask", re.I),
    re.compile(r"% ?(\S+) ?overlaps with ?(\S+)", re.I),
    re.compile(r"[%\S] ?Error: ?[\s]+", re.I),
    re.compile(r"[%\S] ?Informational: ?[\s]+", re.I),
    re.compile(r"Command authorization failed"),
]

terminal_stderr_re_on_iosxr_device = [
    re.compile(r"^\s*% ?Error"),
    re.compile(r"^\s*% ?Bad secret"),
    re.compile(r"^\s*% ?This command is not authorized"),
    re.compile(r"invalid input", re.I),
    re.compile(r"(?:incomplete|ambiguous) command", re.I),
    re.compile(r"^\s*% ?No such configuration item", re.I),
    re.compile(r"'[^']' +returned error code: ?\d+"),
    re.compile(r"Failed to commit", re.I),
]

terminal_stderr_re_on_nxos_device = [
    re.compile(r"% ?Error"),
    re.compile(r"^error:(.*)", re.I),
    re.compile(r"^% \w+", re.M),
    re.compile(r"% ?Bad secret"),
    re.compile(r"invalid input", re.I),
    re.compile(r"(?:incomplete|ambiguous) command", re.I),
    re.compile(r"connection timed out", re.I),
    re.compile(r"[^\r\n]+ not found", re.I),
    re.compile(r"'[^']' +returned error code: ?\d+"),
    re.compile(r"syntax error"),
    re.compile(r"unknown command"),
    re.compile(r"user not present"),
    re.compile(r"invalid (.+?)at '\^' marker", re.I),
    re.compile(r"[B|b]aud rate of console should be.* (\d*) to increase [a-z]* level", re.I),
]

terminal_stderr_re_on_alu_device = [re.compile(r"^Error:"), re.compile(r"^MINOR:")]

terminal_stderr_re_on_huawei_device = [
    re.compile(r"% ?Error: "),
    re.compile(r"^% \w+", re.M),
    re.compile(r"% ?Bad secret"),
    re.compile(r"invalid input", re.I),
    re.compile(r"(?:incomplete|ambiguous) command", re.I),
    re.compile(r"connection timed out", re.I),
    re.compile(r"[^\r\n]+ not found", re.I),
    re.compile(r"'[^']' +returned error code: ?\d+"),
    re.compile(r"syntax error"),
    re.compile(r"unknown command"),
    re.compile(r"Error\[\d+\]: ", re.I),
]

terminal_stderr_re_on_redback_device = [
    re.compile(r"^% ?Error: "),
    re.compile(r"^% \w+", re.M),
    re.compile(r"% ?Bad secret"),
    re.compile(r"invalid input", re.I),
    re.compile(r"(?:incomplete|ambiguous) command", re.I),
    re.compile(r"connection timed out", re.I),
    re.compile(r"[^\r\n]+ not found", re.I),
    re.compile(r"'[^']' +returned error code: ?\d+"),
    re.compile(r"syntax error"),
    re.compile(r"unknown command"),
    re.compile(r"^Error\[\d+\]: ", re.I),
    re.compile(r"^Error:", re.I),
]

terminal_stderr_re_generic_ctu_juniper_junos = [
    re.compile(r"unknown command"),
    re.compile(r"syntax error"),
    re.compile(r"[\r\n]error:"),
]


@dataclass()
class CommandContainer:
    type: str = "normal"
    command: str = None
    autoprompt: bool = False
    command_uuid: str = None


class DeviceSwissKnife(object):
    FAMILY_ALU_SR = "alu-sr"
    FAMILY_CISCO_IOS = "cisco-ios"
    FAMILY_CISCO_IOSXR = "cisco-iosxr"
    FAMILY_CISCO_NXOS = "cisco-nx"
    FAMILY_HUAWEI_VRP = "huawei-vrp"
    FAMILY_REDBACK_SE = "redback-se"
    FAMILY_JUNOS = "juniper-junos"
    FAMILY_GENERIC_CTU_JUNOS = "generic-ctu-juniper-junos"
    CREDENTIAL_ERROR = "credential_error"

    NSO_DEVICE_FAMILIES = [
        FAMILY_ALU_SR,
        FAMILY_CISCO_IOS,
        FAMILY_CISCO_IOSXR,
        FAMILY_CISCO_NXOS,
        FAMILY_HUAWEI_VRP,
        FAMILY_REDBACK_SE,
        FAMILY_JUNOS,
        FAMILY_GENERIC_CTU_JUNOS
    ]
    PYATS_DEVICE_FAMILIES = {
        FAMILY_ALU_SR: "sros",
        FAMILY_CISCO_IOS: "ios",
        FAMILY_CISCO_IOSXR: "iosxr",
        FAMILY_CISCO_NXOS: "nxos",
        FAMILY_HUAWEI_VRP: None,
        FAMILY_REDBACK_SE: None,
        FAMILY_JUNOS: None,
        FAMILY_GENERIC_CTU_JUNOS: "junos"
    }
    DEVICES_LIVE_STATUS_YANG_PREFIX = {
        FAMILY_ALU_SR: "alu-stats:exec",
        FAMILY_CISCO_IOS: "ios-stats:exec",
        FAMILY_CISCO_IOSXR: "cisco-ios-xr-stats:exec",
        FAMILY_CISCO_NXOS: "cisco-nx-stats:exec",
        FAMILY_HUAWEI_VRP: "vrp-stats:exec",
        FAMILY_REDBACK_SE: "redback-se-stats:exec"
    }

    DEVICES_EXIT_COMMAND = {
        FAMILY_ALU_SR: "logout",
        FAMILY_CISCO_IOS: "exit",
        FAMILY_CISCO_IOSXR: "exit",
        FAMILY_CISCO_NXOS: "exit",
        FAMILY_HUAWEI_VRP: "quit",
        FAMILY_REDBACK_SE: "exit",
        FAMILY_GENERIC_CTU_JUNOS: "exit"
    }
    DEVICES_ERROR_REGEX_PATTERNS = {
        FAMILY_ALU_SR: terminal_stderr_re_on_alu_device,
        FAMILY_CISCO_IOS: terminal_stderr_re_on_ios_device,
        FAMILY_CISCO_IOSXR: terminal_stderr_re_on_iosxr_device,
        FAMILY_CISCO_NXOS: terminal_stderr_re_on_nxos_device,
        FAMILY_HUAWEI_VRP: terminal_stderr_re_on_huawei_device,
        FAMILY_REDBACK_SE: terminal_stderr_re_on_redback_device,
        FAMILY_GENERIC_CTU_JUNOS: terminal_stderr_re_generic_ctu_juniper_junos
    }

    DEVICES_TIMESTAMP_COMMAND = {
        FAMILY_ALU_SR: "environment time-stamp",
        FAMILY_CISCO_IOS: "terminal exec prompt timestamp",
        FAMILY_CISCO_IOSXR: "terminal exec prompt timestamp",
        FAMILY_CISCO_NXOS: None,
        FAMILY_HUAWEI_VRP: "terminal command timestamp",
        FAMILY_REDBACK_SE: None,
        FAMILY_GENERIC_CTU_JUNOS: "set cli timestamp",
    }

    DEVICES_COMMENT_DELIMITER = {
        FAMILY_ALU_SR: "#",
        FAMILY_CISCO_IOS: "!",
        FAMILY_CISCO_IOSXR: "!",
        FAMILY_CISCO_NXOS: "!",
        FAMILY_HUAWEI_VRP: "#",
        FAMILY_REDBACK_SE: "!",
        FAMILY_JUNOS: "#",
        FAMILY_GENERIC_CTU_JUNOS: "#",
    }

    DEVICE_CONFIG_HOSTNAME_PATH = {
        FAMILY_ALU_SR: "alu__system",
        FAMILY_CISCO_IOS: "ios__hostname",
        FAMILY_CISCO_IOSXR: "cisco_ios_xr__hostname",
        FAMILY_CISCO_NXOS: "nx__hostname",
        FAMILY_HUAWEI_VRP: "vrp__sysname",
        FAMILY_REDBACK_SE: "redback_se__system",
    }

    DEVICES_PROMPTS = [
        r"[A|B]\:[\w\-\+\.:\/]+#\s?$",  # alu-sr
        r"RS?P[\w\-\+\.:\/]+#\s?$",  # cisco-ioxsr
        r"<[\w\-\+\.:\/]+>\s?$",  # huawei-vrp
        r"\[[\w\-\+\.:\/]+\][\w\-\+\.:\/]+#\s?$",  # redback-se
        r"[\w\-\+\.:\/]+#\s?$",  # cisco-ios
        r"[^<]*>\s?$",  # generic-ctu-juniper-junos
        r"\w*\s?([Pp]assword\s*:|[Ll]ogin\s*:|[Uu]sername\s*:)\s?$",  # incorrect username/password
    ]
    DEVICES_FAMILIES_BY_PROMPT_ORDER = [
        FAMILY_ALU_SR,
        FAMILY_CISCO_IOSXR,
        FAMILY_HUAWEI_VRP,
        FAMILY_REDBACK_SE,
        FAMILY_CISCO_IOS,
        FAMILY_GENERIC_CTU_JUNOS,
        CREDENTIAL_ERROR
    ]

    def __init__(self, root, device_name: str, partial=False):
        if not partial:
            self._normal_constructor(root, device_name)

    def _normal_constructor(self, root, device_name):
        self.device_name = device_name
        if hasattr(root.devices.device[device_name].device_type, 'cli'):
            ned_id = root.devices.device[device_name].device_type.cli.ned_id
            ned_regex = r"(?P<ned_family>[\w\-\d]+)-cli-(?P<ned_version>[\w\-\d\.]+)"
            match = re.match(ned_regex, ned_id)
            if match:
                self.device_family = match.groupdict().get('ned_family')
                if self.device_family == "generic-ctu":
                    device_family_suffix = \
                        root.devices.global_settings.ned_settings.generic_ctu_meta__generic_ctu.rpc_actions.device_mapping[
                            device_name].ned
                    self.device_family = self.device_family + "-" + device_family_suffix
            else:
                raise Exception("Device ned-id name don't match a cli ned name")
        else:
            raise Exception("Only support 'cli' device type")

        self.pyats_device_family = self.PYATS_DEVICE_FAMILIES.get(self.device_family, None)

    @classmethod
    def partial_init_from_prompt_index(cls, device_prompt_index: int):
        my_device_swiss_knife = cls("no_root", "no_name", partial=True)
        try:
            my_device_swiss_knife.device_family = DeviceSwissKnife.DEVICES_FAMILIES_BY_PROMPT_ORDER[device_prompt_index]
        except IndexError:
            raise Exception("Bad prompt index in partial init can't find device family ")
        my_device_swiss_knife.device_name = None
        my_device_swiss_knife.pyats_device_family = DeviceSwissKnife.PYATS_DEVICE_FAMILIES.get(
            my_device_swiss_knife.device_family, None)
        return my_device_swiss_knife

    @property
    def timestamp_command_str(self):  # prompt timestamp is optionnal if not implemented
        command = DeviceSwissKnife.DEVICES_TIMESTAMP_COMMAND.get(self.device_family, None)
        return command

    @property
    def timestamp_command(self):  # prompt timestamp is optionnal if not implemented
        return CommandContainer(command=self.timestamp_command_str)

    @property
    def error_regex_list(self):
        error_regex = DeviceSwissKnife.DEVICES_ERROR_REGEX_PATTERNS.get(self.device_family, None)
        if error_regex is None:
            raise Exception(
                f"No error regex command have been implemented for this device family: {self.device_family}")
        return error_regex

    @property
    def exit_command_str(self):
        exit_command = DeviceSwissKnife.DEVICES_EXIT_COMMAND.get(self.device_family, None)
        if exit_command is None:
            raise Exception(f"No exit command have been implemented for this device family: {self.device_family}")
        return exit_command

    @property
    def live_status_yang_prefix(self):
        yang_prefix = DeviceSwissKnife.DEVICES_LIVE_STATUS_YANG_PREFIX.get(self.device_family, None)
        if yang_prefix is None:
            raise Exception(f"No yang prefix have been implemented for this device family: {self.device_family}")
        return yang_prefix

    @property
    def comment_delimiter(self):
        comment_delimiter = DeviceSwissKnife.DEVICES_COMMENT_DELIMITER.get(self.device_family, None)
        if comment_delimiter is None:
            raise Exception(f"No comment delimiter have been implemented for this device family: {self.device_family}")
        return comment_delimiter

    @property
    def device_config_hostname_path(self):
        device_config_hostname_path = DeviceSwissKnife.DEVICE_CONFIG_HOSTNAME_PATH.get(self.device_family, None)
        if device_config_hostname_path is None:
            raise Exception(
                f"No device_config_hostname_path have been implemented for this device family: {self.device_family}")
        return device_config_hostname_path

    def prepare_command(self, cmd):
        command = cmd.command
        if self.device_family not in [DeviceSwissKnife.FAMILY_ALU_SR, DeviceSwissKnife.FAMILY_HUAWEI_VRP,
                                      DeviceSwissKnife.FAMILY_REDBACK_SE, DeviceSwissKnife.FAMILY_GENERIC_CTU_JUNOS]:
            if not cmd.autoprompt:
                command = cmd.command + " | noprompts"

        return command


def get_device_family(ned_id):
    for device_family in DeviceSwissKnife.NSO_DEVICE_FAMILIES:
        regex = fr"{device_family}-"
        match = re.search(regex, ned_id)
        if match:
            return device_family


def execute_command(root, device_swiss_knife: DeviceSwissKnife, cmd: CommandContainer):
    start_time = datetime.now()

    device_output_has_error = False
    device_output = None

    if not cmd.command.startswith(device_swiss_knife.comment_delimiter):

        if "generic-ctu" in device_swiss_knife.device_family:
            device = root.ncs__devices.device[device_swiss_knife.device_name]
            command_input = device.live_status.generic_ctu_stats__exec["nonconfig-actions"].get_input()
            command = device_swiss_knife.prepare_command(cmd)
            command_input.action.create(command)
            response = device.live_status.generic_ctu_stats__exec.nonconfig_actions(command_input)
        else:
            any_live_status_command = root.devices.device[device_swiss_knife.device_name].live_status.__getitem__(
                device_swiss_knife.live_status_yang_prefix).any
            command_input = any_live_status_command.get_input()
            if cmd.type == "admin":
                command_input.admin_mode
            command = device_swiss_knife.prepare_command(cmd)
            command_input.args = [command]
            response = any_live_status_command.request(command_input)

        end_time = datetime.now()
        execution_time = end_time - start_time
        execution_time = int(execution_time.total_seconds() * 1000)
        device_output = formatted_device_output(cmd.command, response.result)
        for regex in device_swiss_knife.error_regex_list:
            if regex.search(response.result):
                device_output_has_error = True

    else:
        end_time = datetime.now()
        execution_time = 0
        device_output = cmd.command
    return (
        device_output,
        device_output_has_error,
        start_time.isoformat(),
        end_time.isoformat(),
        execution_time,
        cmd.command_uuid
    )


# created for case 687472564 (IOSXR-843 / RT38894)
def formatted_device_output(command, device_output):
    device_output_lst = device_output.replace("\r", "").split("\n")
    iosxr_exam = re.search(
        r"(RS?P[\w\-\+\.:\/]+#\s?)$", device_output_lst[len(device_output_lst) - 1]
    )
    iosxr_exception = re.search(r"^RS?P", device_output_lst[len(device_output_lst) - 1])
    if iosxr_exam and not iosxr_exception:
        device_output_lst[len(device_output_lst) - 1] = re.sub(
            r"(RS?P[\w\-\+\.:\/]+#\s?)$",
            "",
            device_output_lst[len(device_output_lst) - 1],
        )
        device_output_lst.append(iosxr_exam.group(0))
    device_output_lst[0] = device_output_lst[len(device_output_lst) - 1] + command
    return "\n".join(device_output_lst)


@dataclass()
class CommandResult:
    has_error: bool = False
    raw_cli: str = ""
    structured_output: str = ""

    @property
    def has_structured_output(self):
        try:
            if len(self.structured_output) > 0:
                return True
            else:
                return False
        except TypeError:
            return False


def run_live_status(root, device_name, cli_command) -> CommandResult:
    """


    :param root: root = ncs.maagic.get_root(trans) in an NSO Action
    :param device_name:
    :param cli_command:
    :return: CommandResult
    """

    dsk = DeviceSwissKnife(root, device_name)
    command_ctn = CommandContainer(command=cli_command)
    device_output, device_output_has_error, start_time, end_time, execution_time, command_uuid = execute_command(root,
                                                                                                                 dsk,
                                                                                                                 command_ctn)
    command_result = CommandResult()
    command_result.raw_cli = device_output
    if device_output_has_error:
        command_result.has_error = True
        return command_result
    try:
        command_result.structured_output = parser.parse(device_output, command_ctn.command, dsk.pyats_device_family)

    except Exception:
        # if we can't find in ios let's try in iosxe
        if dsk.pyats_device_family == DeviceSwissKnife.PYATS_DEVICE_FAMILIES[DeviceSwissKnife.FAMILY_CISCO_IOS]:
            try:
                command_result.structured_output = parser.parse(device_output, command_ctn.command, "iosxe")
            except Exception:
                pass

    return command_result
