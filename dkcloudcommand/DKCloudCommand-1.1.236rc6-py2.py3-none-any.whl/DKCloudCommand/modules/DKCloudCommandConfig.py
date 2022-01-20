import click
import json
import os
import requests
import shutil

from typing import Union, List, Optional

from DKCloudCommand.modules.DKFileHelper import DKFileHelper
from DKCloudCommand.modules.DKIgnore import DKIgnore
from DKCommon.typing import JSONData


class DKCloudCommandConfig(object):
    _config_dict = dict()
    _config_attributes = None
    CONTEXT_FILE = ".context"
    JWT_FILE_NAME = ".dk-credentials"
    GENERAL_CONFIG_FILE_NAME = "general-config.json"
    CONFIG_FILE_NAME = "config.json"
    DK_CLOUD_PORT = "dk-cloud-port"
    DK_CLOUD_IP = "dk-cloud-ip"
    DK_CLOUD_USERNAME = "dk-cloud-username"
    DK_CLOUD_PASSWORD = "dk-cloud-password"
    DK_CLOUD_JWT = "dk-cloud-jwt"
    DK_CLOUD_MERGE_TOOL = "dk-cloud-merge-tool"
    DK_CLOUD_DIFF_TOOL = "dk-cloud-diff-tool"
    DK_CHECK_WORKING_PATH = "dk-check-working-path"
    DK_SKIP_RECIPE_CHECKER = "dk-skip-recipe-checker"
    DK_HIDE_CONTEXT_LEGEND = "dk-hide-context-legend"
    MERGE_DIR = "merges"
    DIFF_DIR = "diffs"

    def __init__(self) -> None:
        self._dk_temp_folder = None
        self.dk_customer_temp_folder = None
        self.context = None
        self._config_dict = None
        self._ignore = None

        if self._config_dict is None:
            self._config_dict = dict()
        self._required_config_attributes = [
            DKCloudCommandConfig.DK_CLOUD_PORT,
            DKCloudCommandConfig.DK_CLOUD_IP,
            DKCloudCommandConfig.DK_CLOUD_USERNAME,
            DKCloudCommandConfig.DK_CLOUD_PASSWORD,
        ]

    def to_str(self, hide_password: bool) -> str:
        password = self._config_dict.get(DKCloudCommandConfig.DK_CLOUD_PASSWORD, "")
        if hide_password:
            password = "*" * (len(password) or 10)

        return f"""\
        Context:\t\t\t{self.get_current_context()}
        Config Location:\t\t{self.get_config_file_location()}
        General Config Location:\t{self.get_general_config_file_location()}
        Username:\t\t\t{self._config_dict.get(DKCloudCommandConfig.DK_CLOUD_USERNAME, "")}
        Password:\t\t\t{password}
        Cloud IP:\t\t\t{self._config_dict.get(DKCloudCommandConfig.DK_CLOUD_IP, "")}
        Cloud Port:\t\t\t{self._config_dict.get(DKCloudCommandConfig.DK_CLOUD_PORT, "")}
        Merge Tool:\t\t\t{self._config_dict.get(DKCloudCommandConfig.DK_CLOUD_MERGE_TOOL, "")}
        Diff Tool:\t\t\t{self._config_dict.get(DKCloudCommandConfig.DK_CLOUD_DIFF_TOOL, "")}
        Check Working Path:\t\t{self._config_dict.get(DKCloudCommandConfig.DK_CHECK_WORKING_PATH, "")}
        Hide Context Legend:\t\t{self.get_hide_context_legend()}
        Skip Recipe Checker:\t\t{self.get_skip_recipe_checker()}
        """

    def __str__(self) -> str:
        return self.to_str(hide_password=False)

    def is_skip_version_check_present(self) -> bool:
        return "DKCLI_SKIP_VERSION_CHECK" in os.environ

    def check_working_path(self) -> None:
        if DKCloudCommandConfig.DK_CHECK_WORKING_PATH not in self._config_dict:
            return
        do_check = str(self._config_dict[DKCloudCommandConfig.DK_CHECK_WORKING_PATH])
        if do_check.lower() != "true":
            return

        aux_context_list = self.context_list()
        aux_context_list.remove(self.get_current_context())

        cwd = os.getcwd().lower()
        for context in aux_context_list:
            if context.lower() in cwd:
                message = f'Warning: context name "{context}" shows up in your current working path,\n'
                message += f'but your current context is "{self.get_current_context()}".'
                click.secho(message, fg="red")

    def is_general_config_file_configured(self) -> bool:
        general_config_path = os.path.join(self._dk_temp_folder, DKCloudCommandConfig.GENERAL_CONFIG_FILE_NAME)
        return os.path.exists(general_config_path)

    def configure_general_file(
        self,
        merge_tool: str,
        diff_tool: str,
        check_working_path: bool,
        hide_context_legend: bool,
        skip_recipe_checker: bool,
    ) -> None:
        data = {
            DKCloudCommandConfig.DK_CLOUD_DIFF_TOOL: diff_tool,
            DKCloudCommandConfig.DK_CLOUD_MERGE_TOOL: merge_tool,
            DKCloudCommandConfig.DK_CHECK_WORKING_PATH: check_working_path,
            DKCloudCommandConfig.DK_SKIP_RECIPE_CHECKER: skip_recipe_checker,
            DKCloudCommandConfig.DK_HIDE_CONTEXT_LEGEND: hide_context_legend,
        }

        general_config_path = os.path.join(self._dk_temp_folder, DKCloudCommandConfig.GENERAL_CONFIG_FILE_NAME)
        with open(general_config_path, "w+") as f:
            json.dump(data, f, indent=4)

    def context_list(self) -> List[str]:
        ret = []
        directories = next(os.walk(self._dk_temp_folder))[1]
        for directory in directories:
            ret.append(directory)
        return sorted(ret)

    def set_context(self, context: str) -> None:
        self.context = context

    def get_current_context(self) -> str:
        return self.context

    def init_ignore_file(self, dk_temp_folder: str) -> None:
        self._ignore = DKIgnore(dk_temp_folder)

    def get_ignore(self) -> DKIgnore:
        return self._ignore

    def get_skip_recipe_checker(self) -> Union[str, bool]:
        return True
        skip = False
        if DKCloudCommandConfig.DK_SKIP_RECIPE_CHECKER in self._config_dict:
            skip = self._config_dict[DKCloudCommandConfig.DK_SKIP_RECIPE_CHECKER]
        return skip

    def get_hide_context_legend(self) -> Union[str, bool]:
        hide = False
        if DKCloudCommandConfig.DK_HIDE_CONTEXT_LEGEND in self._config_dict:
            hide = self._config_dict[DKCloudCommandConfig.DK_HIDE_CONTEXT_LEGEND]
        return hide

    def print_current_context(self, current_command: Optional[str] = None) -> None:
        if "ori" == current_command or "orderrun-info" == current_command:
            return
        if self.get_hide_context_legend():
            return

        context_list = self.context_list()
        if len(context_list) < 2:
            return
        click.secho(f"Current context is: {self.get_current_context()}", fg="yellow")

    def delete_context(self, context_name: str) -> None:
        context_path = os.path.join(self._dk_temp_folder, context_name)
        shutil.rmtree(context_path)

    def context_exists(self, context_name: str) -> bool:
        context_list = self.context_list()
        for context in context_list:
            if context != context_name and context.lower() == context_name.lower():
                raise Exception(f"You probably meant context: {context}")

        context_path = os.path.join(self._dk_temp_folder, context_name)
        return os.path.exists(context_path)

    def create_context(self, context_name: str) -> None:
        context_path = os.path.join(self._dk_temp_folder, context_name)
        try:
            os.makedirs(context_path)
        except Exception:
            pass

    def switch_context(self, context_name: str) -> None:
        dk_context_path = os.path.join(self._dk_temp_folder, DKCloudCommandConfig.CONTEXT_FILE)
        DKFileHelper.write_file(dk_context_path, context_name)

    def get_ip(self) -> Union[str, bool]:
        if DKCloudCommandConfig.DK_CLOUD_IP in self._config_dict:
            return self._config_dict[DKCloudCommandConfig.DK_CLOUD_IP]
        else:
            return False

    def get_port(self) -> Union[str, bool]:
        if DKCloudCommandConfig.DK_CLOUD_PORT in self._config_dict:
            return self._config_dict[DKCloudCommandConfig.DK_CLOUD_PORT]
        else:
            return False

    def get_username(self) -> Union[str, bool]:
        if DKCloudCommandConfig.DK_CLOUD_USERNAME in self._config_dict:
            return self._config_dict[DKCloudCommandConfig.DK_CLOUD_USERNAME]
        else:
            return False

    def get_password(self) -> Union[str, bool]:
        if DKCloudCommandConfig.DK_CLOUD_PASSWORD in self._config_dict:
            return self._config_dict[DKCloudCommandConfig.DK_CLOUD_PASSWORD]
        else:
            return False

    def get_jwt(self) -> Optional[str]:
        if DKCloudCommandConfig.DK_CLOUD_JWT in self._config_dict:
            return self._config_dict[DKCloudCommandConfig.DK_CLOUD_JWT]
        else:
            return None

    def set_jwt(self, jwt: Optional[str] = None) -> bool:
        self._config_dict[DKCloudCommandConfig.DK_CLOUD_JWT] = jwt
        return self.save_jwt_to_file()

    def update_jwt(self, refreshed_token: str) -> None:
        if refreshed_token != self.get_jwt():
            self.set_jwt(refreshed_token)

    def save_jwt_to_file(self) -> bool:
        dk_customer_temp_folder = self.get_dk_customer_temp_folder()
        try:
            if dk_customer_temp_folder:
                jwt_file_path = os.path.join(dk_customer_temp_folder, self.JWT_FILE_NAME)
                DKFileHelper.write_file(jwt_file_path, self._config_dict[self.DK_CLOUD_JWT])
            return True
        except Exception as e:
            print(f"DKCloudCommandConfig: failed to write jwt in file.\n {e}.")
            return False

    def set_dk_customer_temp_folder(self, dk_customer_temp_folder: str) -> None:
        self.dk_customer_temp_folder = dk_customer_temp_folder

    def set_dk_temp_folder(self, dk_temp_folder: str) -> None:
        self._dk_temp_folder = dk_temp_folder

    def get_dk_temp_folder(self) -> str:
        return self._dk_temp_folder

    def get_dk_customer_temp_folder(self) -> str:
        return self.dk_customer_temp_folder

    def get_general_config_file_location(self) -> str:
        return os.path.join(self._dk_temp_folder, DKCloudCommandConfig.GENERAL_CONFIG_FILE_NAME)

    def get_config_file_location(self) -> str:
        return os.path.join(self.dk_customer_temp_folder, DKCloudCommandConfig.CONFIG_FILE_NAME)

    def delete_jwt(self) -> None:
        if DKCloudCommandConfig.DK_CLOUD_JWT in self._config_dict:
            del self._config_dict[DKCloudCommandConfig.DK_CLOUD_JWT]

    def get_merge_tool(self) -> JSONData:
        if (
            DKCloudCommandConfig.DK_CLOUD_MERGE_TOOL not in self._config_dict
            or self._config_dict[DKCloudCommandConfig.DK_CLOUD_MERGE_TOOL] is None
            or self._config_dict[DKCloudCommandConfig.DK_CLOUD_MERGE_TOOL] is None
        ):
            raise Exception(
                "Merge tool was not properly configured. Please run 'dk config-list' to check "
                "current configuration and 'dk config' to change it."
            )
        return self._config_dict[DKCloudCommandConfig.DK_CLOUD_MERGE_TOOL]

    def get_diff_tool(self) -> JSONData:
        if (
            DKCloudCommandConfig.DK_CLOUD_DIFF_TOOL not in self._config_dict
            or self._config_dict[DKCloudCommandConfig.DK_CLOUD_DIFF_TOOL] is None
            or self._config_dict[DKCloudCommandConfig.DK_CLOUD_DIFF_TOOL] is None
        ):
            raise Exception(
                "Diff tool was not properly configured. Please run 'dk config-list' to check "
                "current configuration and 'dk config' to change it."
            )
        return self._config_dict[DKCloudCommandConfig.DK_CLOUD_DIFF_TOOL]

    def get_merge_dir(self) -> str:
        return os.path.join(self.get_dk_customer_temp_folder(), DKCloudCommandConfig.MERGE_DIR)

    def get_diff_dir(self) -> str:
        return os.path.join(self.get_dk_customer_temp_folder(), DKCloudCommandConfig.DIFF_DIR)

    def init_general_config(self) -> None:
        config_file_path = os.path.join(self._dk_temp_folder, DKCloudCommandConfig.GENERAL_CONFIG_FILE_NAME)
        config_file_contents = DKFileHelper.read_file(config_file_path)
        if config_file_contents:
            general_config_dict = json.loads(config_file_contents)
            for k in general_config_dict:
                self._config_dict[k] = general_config_dict[k]

    def init_from_dict(self, set_dict: JSONData) -> bool:
        self._config_dict = set_dict
        return self.validate_config()

    def init_from_file(self, file_json: str) -> bool:
        if file_json is None:
            print("DKCloudCommandConfig file path cannot be null")
            rv = False
        else:
            try:
                if file_json[0] == "~":
                    user_home = os.path.expanduser("~")
                    full_path = file_json.replace("~", user_home)
                else:
                    full_path = file_json
                statinfo = os.stat(full_path)
            except Exception:
                pass
                rv = False
            else:
                if statinfo.st_size > 0:
                    with open(full_path) as data_file:
                        try:
                            self._config_dict = json.load(data_file)
                        except ValueError as e:
                            print(f"DKCloudCommandConfig: failed json.load check syntax {full_path}. {e}")
                            rv = False
                        else:
                            rv = True
                else:
                    rv = False
        if rv is False:
            return False
        else:
            self.init_general_config()
            self.get_jwt_from_file()
            return self.validate_config()

    def get_jwt_from_file(self) -> None:
        jwt_file_path = os.path.join(self.get_dk_customer_temp_folder(), self.JWT_FILE_NAME)
        self._config_dict[self.DK_CLOUD_JWT] = DKFileHelper.read_file(jwt_file_path)

    def delete_jwt_from_file(self) -> None:
        self.delete_jwt()
        jwt_file_path = os.path.join(self.get_dk_customer_temp_folder(), self.JWT_FILE_NAME)
        if os.path.isfile(jwt_file_path):
            os.remove(jwt_file_path)

    def validate_config(self) -> bool:
        for v in self._required_config_attributes:
            if v not in self._config_dict:
                print(f"DKCloudCommandConfig: failed to find {v} in {DKCloudCommandConfig.CONFIG_FILE_NAME}")
                return False
        return True

    def get_latest_version_from_pip(self) -> str:
        response = requests.get("https://pypi.python.org/pypi/DKCloudCommand/json")
        info_json = response.json()
        return info_json["info"]["version"]
