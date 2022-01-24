import json
import os
import requests

from urllib.parse import quote
from typing import Tuple, Any, List, Optional
from requests import RequestException, Response

from DKCloudCommand.modules.DKCloudCommandConfig import DKCloudCommandConfig
from DKCommon.api_utils.DKApiHelper import DKApiHelper
from DKCommon.api_utils.api_utils import validate_and_get_response, get_issue_messages
from DKCommon.Constants import VAULT_GLOBAL
from DKCommon.DKFileEncode import DKFileEncode
from DKCommon.DKPathUtils import (
    normalize,
    normalize_dict_keys,
    normalize_dict_value,
    normalize_get_compiled_file,
    normalize_recipe_dict,
    normalize_recipe_dict_kmp,
    normalize_recipe_validate,
    UNIX,
    WIN,
)
from DKCloudCommand.modules.DKFileHelper import DKFileHelper
from DKCloudCommand.modules.DKRecipeDisk import (
    DKRecipeDisk,
    compare_sha,
    get_directory_sha,
)
from DKCloudCommand.modules.DKReturnCode import DKReturnCode, convert_return_code

# Typing imports
from DKCloudCommand.modules.DKIgnore import DKIgnore
from DKCommon.typing import JSONData

__author__ = "DataKitchen, Inc."
"""
NOMENCLATURE

Some example files:

abspath
  /tmp/test/simple/description.json
  /tmp/test/simple/resources/cools.sql

Here are what the parts are called:

file_name
    description.json
    cools.sql

recipe_name
  simple

filepath # as known to the user
api_file_key # specifies the file to create/update/delete
             # relative to being in the top recipe directory
             # i.e. file name and path to the file name, relative to the recipe root
             # recipe root = cd /tmp/test/simple
  resources/cool.sql
  cool.sql

recipe_file_key # used as a key to the dictionary
  simple/resources # for cool.sql
  simple # for description.json

recipe_file # location on disk including the recipe name
  simple/resources/cool.sql
  simple/description.json

filedir # the directory portion between the recipe and the file_name
  resources


For the CLI, assume the user has CD to the top of the recipe
e.g.
  cd /var/tmp/test/simple

"""


class DKCloudAPI:
    _use_https = False
    DKAPP_KITCHEN_FILE = "kitchen.json"
    DKAPP_KITCHENS_DIR = "kitchens"
    MESSAGE = "message"
    FILEPATH = "filepath"
    TEMPLATENAME = "templatename"
    FILE = "file"
    FILES = "files"
    FILENAME = "filename"
    JSON = "json"
    TEXT = "text"
    SHA = "sha"
    LAST_UPDATE_TIME = "last_update_time"
    DESCRIPTION = "description"

    def __init__(self, dk_cli_config: Optional[DKCloudCommandConfig]) -> None:
        if isinstance(dk_cli_config, DKCloudCommandConfig):
            self._config = dk_cli_config
            self._role = None
            self._customer_name = None
            self._api_helper = None

    def parse_response(self, response: Response) -> JSONData:
        if response and response.headers and "refreshed_token" in response.headers:
            refreshed_token = response.headers["refreshed_token"]
            self._config.update_jwt(refreshed_token)
        return validate_and_get_response(response)

    def get_ignore(self) -> DKIgnore:
        return self._config.get_ignore()

    def get_config(self) -> DKCloudCommandConfig:
        return self._config

    def get_url_for_direct_rest_call(self) -> str:
        if self._use_https is False:
            return f"{self._config.get_ip()}:{self._config.get_port()}"
        else:
            return "must use http"

    def login(self) -> Optional[str]:
        try:
            url = self.get_url_for_direct_rest_call()
            token = self._config.get_jwt()

            if not token or not DKApiHelper.valid_token(url, token):
                self._api_helper = DKApiHelper.new(url, self._config.get_username(), self._config.get_password())
                self._config.set_jwt(self._api_helper.token)
            else:
                self._api_helper = DKApiHelper.new_from_token(url, token)

            return self._api_helper.token
        except Exception as e:
            print(str(e))
            return None

    def _get_common_headers(self, one_time_token: Optional[str] = None) -> JSONData:
        if one_time_token is not None:
            return {"Authorization": f"Bearer {one_time_token}"}
        else:
            return {"Authorization": f"Bearer {self._config.get_jwt()}"}

    def get_user_info(self, id_token: str) -> Optional[JSONData]:
        url = f"{self.get_url_for_direct_rest_call()}/v2/userinfo"
        try:
            response = requests.get(url, headers=self._get_common_headers(id_token))
        except (RequestException, ValueError, TypeError) as c:
            print(f"userinfo: exception: {c}")
            return None

        try:
            parsed_response = self.parse_response(response)
        except Exception as e:
            return None

        if response is not None:
            if "role" in parsed_response:
                self._role = parsed_response["role"]
            else:
                self._role = None
                print("role not found in user_info")

            if "customer_name" in parsed_response:
                self._customer_name = parsed_response["customer_name"]
            else:
                self._customer_name = None
                print("customer_name not found in user_info")
            return parsed_response
        else:
            print("userinfo: response is empty")
            return None

    def get_user_role(self) -> str:
        if self._role is None:
            id_token = self._config.get_jwt()
            self.get_user_info(id_token)
        return self._role

    def is_user_role(self, role: str) -> bool:
        current_role = self.get_user_role()
        if current_role is None or role is None:
            return False
        if current_role != role:
            return False
        return True

    def get_customer_name(self) -> str:
        if not self._customer_name:
            id_token = self._config.get_jwt()
            self.get_user_info(id_token)
        return self._customer_name

    def get_merge_dir(self) -> str:
        return self._config.get_merge_dir()

    def get_diff_dir(self) -> str:
        return self._config.get_diff_dir()

    # implementation ---------------------------------
    @staticmethod
    def rude() -> str:
        return "**rude**"

    # It looks like this is only called from TestCloudAPI.py.  Consider moving this function
    # return kitchen dict
    def get_kitchen_dict(self, kitchen_name: str) -> JSONData:
        return self._api_helper.get_kitchen_dict(kitchen_name)

    # returns a list of kitchens
    # '/v2/kitchen/list', methods=['GET'])
    def list_kitchen(self) -> DKReturnCode:
        return convert_return_code(self._api_helper.list_kitchen())

    def vault_info(self, kitchen_name: Optional[str]) -> JSONData:
        req_dict = dict()
        if kitchen_name:
            req_dict["kitchens"] = kitchen_name
        url = f"{self.get_url_for_direct_rest_call()}/v2/vault/config"
        response = requests.get(url, data=json.dumps(req_dict), headers=self._get_common_headers())
        return self.parse_response(response)

    def vault_config(self, kitchen_name: Optional[str], in_dict: JSONData) -> JSONData:
        req_dict = dict()
        req_dict["config"] = dict()
        if kitchen_name:
            req_dict["config"][kitchen_name] = in_dict
        else:
            req_dict["config"][VAULT_GLOBAL] = in_dict
        url = f"{self.get_url_for_direct_rest_call()}/v2/vault/config"
        response = requests.post(url, data=json.dumps(req_dict), headers=self._get_common_headers())
        return self.parse_response(response)

    def vault_delete(self, kitchen_name: str) -> JSONData:
        url = f"{self.get_url_for_direct_rest_call()}/v2/vault/config/{kitchen_name}"
        response = requests.delete(url, headers=self._get_common_headers())
        return self.parse_response(response)

    def secret_list(self, path: Optional[str], kitchen_name: Optional[str]) -> JSONData:
        path = path or ""
        url = f"{self.get_url_for_direct_rest_call()}/v2/secret/{path}"
        req_dict = dict()
        if kitchen_name:
            req_dict["kitchens"] = kitchen_name
        response = requests.get(url, data=json.dumps(req_dict), headers=self._get_common_headers())
        return self.parse_response(response)

    def secret_write(self, path: Optional[str], value: str, kitchen_name: Optional[str]) -> DKReturnCode:
        rc = DKReturnCode()
        path = path or ""
        url = f"{self.get_url_for_direct_rest_call()}/v2/secret/{path}"
        try:
            pdict = {"value": value}
            if kitchen_name:
                pdict["kitchen"] = kitchen_name
            response = requests.post(url, data=json.dumps(pdict), headers=self._get_common_headers())
            self.parse_response(response)
            rc.set(rc.DK_SUCCESS, None, None)
            return rc
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"secret_write: exception: {c}")
            return rc

    def secret_delete(self, path: Optional[str], kitchen_name: Optional[str]) -> DKReturnCode:
        rc = DKReturnCode()
        path = path or ""
        url = f"{self.get_url_for_direct_rest_call()}/v2/secret/{path}"
        try:
            request_dict = dict()
            if kitchen_name:
                request_dict["kitchen"] = kitchen_name
            response = requests.delete(url, data=json.dumps(request_dict), headers=self._get_common_headers())
            self.parse_response(response)
            rc.set(rc.DK_SUCCESS, None, None)
            return rc
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"secret_delete: exception: {c}")
            return rc

    # '/v2/kitchen/update/<string:kitchenname>', methods=['POST'])
    def update_kitchen(self, update_kitchen: Optional[JSONData], message: Optional[str]) -> Optional[bool]:
        return self._api_helper.update_kitchen(update_kitchen, message)

    # '/v2/kitchen/create/<string:existingkitchenname>/<string:newkitchenname>', methods=['GET'])
    def create_kitchen(
        self,
        existing_kitchen_name: Optional[str],
        new_kitchen_name: Optional[str],
        description: Optional[str],
        message: Optional[str],
    ) -> DKReturnCode:
        return convert_return_code(
            self._api_helper.create_kitchen(existing_kitchen_name, new_kitchen_name, description, message=message)
        )

    # '/v2/kitchen/delete/<string:existingkitchenname>', methods=['DELETE'])
    def delete_kitchen(
        self, existing_kitchen_name: Optional[str], message: Optional[str], synchronous_delete: bool = False
    ) -> DKReturnCode:
        return convert_return_code(self._api_helper.delete_kitchen(existing_kitchen_name, message, synchronous_delete))

    def modify_kitchen_settings(self, kitchen_name: str, add: Tuple = (), unset: Tuple = ()) -> DKReturnCode:
        rc = self.get_kitchen_settings(kitchen_name)
        if not rc.ok():
            return rc

        kitchen_json = rc.get_payload()
        overrides = kitchen_json["recipeoverrides"]

        msg = ""
        commit_message = ""

        msg_lines = []
        commit_msg_lines = []

        if len(add) > 0:
            if isinstance(overrides, list):
                for add_this in add:
                    matches = [
                        existing_override
                        for existing_override in overrides
                        if existing_override["variable"] == add_this[0]
                    ]
                    if len(matches) == 0:
                        overrides.append(
                            {
                                "variable": add_this[0],
                                "value": add_this[1],
                                "category": "from_command_line",
                            }
                        )
                    else:
                        matches[0]["value"] = add_this[1]

                    msg_lines.append(f"{add_this[0]} added with value '{add_this[1]}'\n")
                    commit_msg_lines.append(f"{add_this[0]} added")
            else:
                for add_this in add:
                    overrides[add_this[0]] = add_this[1]
                    msg_lines.append(f"{add_this[0]} added with value '{add_this[1]}'\n")
                    commit_msg_lines.append(f"{add_this[0]} added")

        # tom_index = next(index for (index, d) in enumerate(lst) if d["name"] == "Tom")
        # might be a string?
        if len(unset) > 0:
            if isinstance(overrides, list):
                if isinstance(unset, list) or isinstance(unset, tuple):
                    for unset_this in unset:
                        match_index = next(
                            (index for (index, d) in enumerate(overrides) if d["variable"] == unset_this),
                            None,
                        )
                        if match_index is not None:
                            del overrides[match_index]
                            msg_lines.append(f"{unset_this} unset")
                            commit_msg_lines.append(f"{unset_this} unset")
                else:
                    match_index = next(
                        (index for (index, d) in enumerate(overrides) if d["variable"] == unset),
                        None,
                    )
                    if match_index is not None:
                        del overrides[match_index]
                        msg_lines.append(f"{unset} unset")
                        commit_msg_lines.append(f"{unset} unset")
            else:
                msg_lines = []
                if isinstance(unset, list) or isinstance(unset, tuple):
                    for unset_this in unset:
                        if unset_this in overrides:
                            del overrides[unset_this]
                        msg_lines.append(f"{unset_this} unset")
                        commit_msg_lines.append(f"{unset_this} unset")
                else:
                    if unset in overrides:
                        del overrides[unset]
                    msg_lines.append(f"{unset} unset")
                    commit_msg_lines.append(f"{unset} unset")

        msg = "\n".join(msg_lines)
        commit_message = " ; ".join(commit_msg_lines)

        rc = self.put_kitchen_settings(kitchen_name, kitchen_json, commit_message)
        if not rc.ok():
            return rc

        rc = DKReturnCode()
        rc.set(rc.DK_SUCCESS, msg, overrides)
        return rc

    def get_kitchen_settings(self, kitchen_name: str) -> DKReturnCode:
        rc = DKReturnCode()
        url = f"{self.get_url_for_direct_rest_call()}/v2/kitchen/settings/{kitchen_name}"
        try:
            response = requests.get(url, headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"settings_kitchen: exception: {c}")
            return rc
        rdict = self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, rdict)
        return rc

    def put_kitchen_settings(self, kitchen_name: str, kitchen_dict: JSONData, msg: str) -> DKReturnCode:
        rc = DKReturnCode()

        try:
            kitchen_json = json.dumps(kitchen_dict)
        except ValueError as ve:
            # Make sure this is valid json
            rc.set(rc.DK_FAIL, str(ve))
            return rc

        d1 = dict()
        d1["kitchen.json"] = kitchen_dict
        d1["message"] = msg
        url = f"{self.get_url_for_direct_rest_call()}/v2/kitchen/settings/{kitchen_name}"
        try:
            response = requests.put(url, headers=self._get_common_headers(), data=json.dumps(d1))
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"settings_kitchen: exception: {c}")
            return rc
        rdict = self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, rdict)
        return rc

    def kitchen_settings_json_update(self, kitchen: str, filepath: str) -> DKReturnCode:
        rc = DKReturnCode()

        # Open local file to see contents
        msg = ""
        try:
            file_content = DKFileHelper.read_file(filepath[0])
            json_content = json.loads(file_content)
        except IOError as e:
            if len(msg) != 0:
                msg += "\n"
            msg += f"{e}"
            rc.set(rc.DK_FAIL, msg)
            return rc
        except ValueError as e:
            if len(msg) != 0:
                msg += "\n"
            msg += f"ERROR: {e}"
            rc.set(rc.DK_FAIL, msg)
            return rc

        # send new version to backend
        pdict = dict()
        pdict[self.FILEPATH] = filepath
        pdict[self.FILE] = json_content
        url = f"{self.get_url_for_direct_rest_call()}/v2/kitchen/settings/json/{kitchen}"
        try:
            response = requests.post(url, data=json.dumps(pdict), headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"kitchen_settings_json_update: exception: {c}")
            return rc
        self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None)
        return rc

    def kitchen_settings_json_get(self, kitchen: Optional[str]) -> DKReturnCode:
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen parameter")
            return rc

        url = f"{self.get_url_for_direct_rest_call()}/v2/kitchen/settings/json/{kitchen}"
        try:
            response = requests.get(url, headers=self._get_common_headers())
            pass
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"kitchen_settings_json_get: exception: {c}")
            return rc
        rdict = self.parse_response(response)
        try:
            full_dir = os.getcwd()
            DKRecipeDisk.write_files(full_dir, rdict, format=True)
            rc.set(rc.DK_SUCCESS, None, rdict)
            return rc
        except Exception as e:
            s = f'kitchen_settings_json_get: unable to write file: {rdict["filename"]}\n{e}\n'
            rc.set(rc.DK_FAIL, s)
            return rc

    def list_recipe(self, kitchen: Optional[str]) -> DKReturnCode:
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen parameter")
            return rc
        url = f"{self.get_url_for_direct_rest_call()}/v2/kitchen/recipenames/{kitchen}"
        try:
            response = requests.get(url, headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"list_recipe: exception: {c}")
            return rc

        rdict = self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, rdict["recipes"])
        return rc

    def recipe_create(self, kitchen: Optional[str], name: str, template: Optional[str] = None) -> DKReturnCode:
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen parameter")
            return rc

        pdict = dict()
        pdict[self.TEMPLATENAME] = template

        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/create/{kitchen}/{name}"
        try:
            response = requests.post(url, data=json.dumps(pdict), headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"recipe_create: exception: {c}")
            return rc

        self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None)
        return rc

    def recipe_copy(self, kitchen: Optional[str], source: Optional[str], name: Optional[str]) -> DKReturnCode:
        rc = DKReturnCode()
        for item in [kitchen, source, name]:
            if item is None or isinstance(item, str) is False:
                rc.set(rc.DK_FAIL, "not all parameters present")
                return rc

        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/copy/{kitchen}/{source}/{name}"
        try:
            response = requests.post(url, headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"recipe_copy: exception: {c}")
            return rc

        self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None)
        return rc

    def recipe_delete(self, kitchen: Optional[str], name: Optional[str]) -> DKReturnCode:
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen parameter")
            return rc
        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/{kitchen}/{name}"
        try:
            response = requests.delete(url, headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"recipe_delete: exception: {c}")
            return rc
        self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None)
        return rc

    # returns a recipe
    # api.add_resource(GetRecipeV2, '/v2/recipe/get/<string:kitchenname>/<string:recipename>',
    #             methods=['GET', 'POST'])
    # get() gets all files in a recipe
    # post() gets a list of files in a recipe in the post as a 'recipe-files' list of dir / file names
    def get_recipe(self, kitchen: str, recipe: str, list_of_files: List[str] = None) -> DKReturnCode:
        return convert_return_code(self._api_helper.get_recipe(kitchen, recipe, list_of_files=list_of_files))

    def update_file(
        self,
        kitchen: Optional[str],
        recipe: Optional[str],
        message: str,
        api_file_key: Optional[str],
        file_contents: str,
    ) -> DKReturnCode:
        """
        returns success or failure (True or False)
        '/v2/recipe/update/<string:kitchenname>/<string:recipename>', methods=['POST']
        :param self: DKCloudAPI
        :param kitchen: basestring
        :param recipe: basestring  -- kitchen name, basestring
        :param message: basestring message -- commit message, basestring
        :param api_file_key:  -- the recipe based file path (recipe_name/node1/data_sources, e.g.)
        :param file_contents: -- character string of the recipe file to update

        :rtype: DKReturnCode
        """
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen parameter")
            return rc
        if recipe is None or isinstance(recipe, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe parameter")
            return rc
        if api_file_key is None or isinstance(api_file_key, str) is False:
            rc.set(rc.DK_FAIL, "issue with api_file_key parameter")
            return rc

        pdict = dict()
        pdict[self.MESSAGE] = message
        if DKFileEncode.is_binary(api_file_key):
            file_contents = DKFileEncode.b64encode(file_contents)
        pdict[self.FILEPATH] = normalize(api_file_key, UNIX)
        if isinstance(file_contents, bytes):  # decode bytes to unicode:
            file_contents = file_contents.decode("utf-8")
        pdict[self.FILE] = file_contents
        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/update/{kitchen}/{recipe}"
        try:
            response = requests.post(url, data=json.dumps(pdict), headers=self._get_common_headers())
            pass
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"update_file: exception: {c}")
            return rc
        rdict = self.parse_response(response)
        rdict["formatted_files"] = normalize_dict_keys(rdict["formatted_files"], WIN)
        rc.set(rc.DK_SUCCESS, get_issue_messages(rdict), payload=rdict)
        return rc

    def _decode_contents_in_changes_dictionary(self, changes: JSONData) -> None:
        for file_key, val_dict in changes.items():
            if isinstance(val_dict, dict):
                if "contents" in val_dict:
                    if isinstance(val_dict["contents"], bytes):
                        val_dict["contents"] = val_dict["contents"].decode("utf-8")

    def update_files(
        self, kitchen: Optional[str], recipe: Optional[str], message: str, changes: JSONData
    ) -> DKReturnCode:
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen parameter")
            return rc
        if recipe is None or isinstance(recipe, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe parameter")
            return rc
        pdict = dict()
        pdict[self.MESSAGE] = message
        self._decode_contents_in_changes_dictionary(changes)

        pdict[self.FILES] = normalize_dict_keys(changes, UNIX)
        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/update/{kitchen}/{recipe}"
        try:
            response = requests.post(url, data=json.dumps(pdict), headers=self._get_common_headers())
            pass
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"update_file: exception: {c}")
            return rc

        rdict = self.parse_response(response)
        rdict = normalize_dict_keys(rdict, WIN, ignore=["status", "issues", "branch", "formatted_files"])
        rdict["formatted_files"] = normalize_dict_keys(rdict["formatted_files"], WIN)
        rc.set(rc.DK_SUCCESS, None, rdict)
        return rc

    # Create a file in a recipe
    def add_file(
        self,
        kitchen: Optional[str],
        recipe: Optional[str],
        message: str,
        api_file_key: Optional[str],
        file_contents: str,
    ) -> DKReturnCode:
        """
        returns True for success or False for failure
        '/v2/recipe/create/<string:kitchenname>/<string:recipename>', methods=['PUT']
        :param self: DKCloudAPI
        :param kitchen: basestring
        :param recipe: basestring  -- kitchen name, basestring
        :param message: basestring message -- commit message, basestring
        :param api_file_key:  -- file name and path to the file name, relative to the recipe root
        :param file_contents: -- character string of the recipe file to update

        :rtype: boolean
        """
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen parameter")
            return rc
        if recipe is None or isinstance(recipe, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe parameter")
            return rc
        if api_file_key is None or isinstance(api_file_key, str) is False:
            rc.set(rc.DK_FAIL, "issue with api_file_key parameter")
            return rc

        pdict = dict()
        pdict[self.MESSAGE] = message
        if DKFileEncode.is_binary(api_file_key):
            file_contents = DKFileEncode.b64encode(file_contents)
        if isinstance(file_contents, bytes):
            file_contents = file_contents.decode("utf-8")
        pdict[self.FILE] = file_contents
        pdict[self.FILEPATH] = normalize(api_file_key, UNIX)
        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/create/{kitchen}/{recipe}"
        try:
            response = requests.put(url, data=json.dumps(pdict), headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"add_file: exception: {c}")
            return rc

        self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None)
        return rc

    # api.add_resource(DeleteRecipeFileV2, '/v2/recipe/delete/<string:kitchenname>/<string:recipename>',
    #              methods=['DELETE'])
    def delete_file(
        self,
        kitchen: Optional[str],
        recipe: Optional[str],
        message: str,
        recipe_file_key: Optional[str],
        recipe_file: Optional[str],
    ) -> DKReturnCode:
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen parameter")
            return rc
        if recipe is None or isinstance(recipe, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe parameter")
            return rc
        if recipe_file_key is None or isinstance(recipe_file_key, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe_file_key parameter")
            return rc
        if recipe_file is None or isinstance(recipe_file, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe_file parameter")
            return rc
        pdict = dict()
        pdict[self.MESSAGE] = message
        pdict[self.FILEPATH] = normalize(recipe_file_key, UNIX)
        pdict[self.FILE] = recipe_file
        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/delete/{kitchen}/{recipe}"
        try:
            response = requests.delete(url, data=json.dumps(pdict), headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"delete_file: exception: {c}")
            return rc

        self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None)
        return rc

    def get_compiled_order_run(
        self, kitchen: Optional[str], recipe_name: Optional[str], variation_name: Optional[str]
    ) -> DKReturnCode:
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen")
            return rc
        if recipe_name is None or isinstance(recipe_name, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe_name")
            return rc
        if variation_name is None or isinstance(variation_name, str) is False:
            rc.set(rc.DK_FAIL, "issue with variation_name")
            return rc
        url = f"{self.get_url_for_direct_rest_call()}/v2/servings/compiled/get/{kitchen}/{recipe_name}/{variation_name}"
        try:
            response = requests.get(url, headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"get_compiled_order_run: exception: {c}")
            return rc
        rdict = self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, rdict[recipe_name])
        return rc

    def get_compiled_file(
        self,
        kitchen: Optional[str],
        recipe_name: Optional[str],
        variation_name: Optional[str],
        file_data: JSONData,
    ) -> DKReturnCode:
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen")
            return rc
        if recipe_name is None or isinstance(recipe_name, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe_name")
            return rc
        if variation_name is None or isinstance(variation_name, str) is False:
            rc.set(rc.DK_FAIL, "issue with variation_name")
            return rc

        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/compile/{kitchen}/{recipe_name}/{variation_name}"

        try:
            data = {"file": normalize_get_compiled_file(file_data, UNIX)}
            response = requests.post(url, data=json.dumps(data), headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"get_compiled_file: exception: {c}")
            return rc

        rdict = self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, rdict)
        return rc

    def get_file(self, kitchen: str, recipe: str, file_path: str) -> JSONData:
        rc = DKReturnCode()
        file_path = normalize(file_path, UNIX)
        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/file/{kitchen}/{recipe}/{file_path}"
        response = requests.get(url, headers=self._get_common_headers())
        rdict = self.parse_response(response)
        return rdict["contents"]

    def get_file_history(
        self, kitchen: Optional[str], recipe_name: Optional[str], file_path: str, change_count: int
    ) -> DKReturnCode:
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen")
            return rc
        if recipe_name is None or isinstance(recipe_name, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe_name")
            return rc

        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/history/{kitchen}/{recipe_name}/{normalize(file_path, UNIX)}?change_count={change_count}"

        try:
            response = requests.get(url, headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"get_compiled_file: exception: {c}")
            return rc

        rdict = self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, rdict)
        return rc

    def recipe_validate(
        self,
        kitchen: Optional[str],
        recipe_name: Optional[str],
        variation_name: Optional[str],
        changed_files: JSONData,
    ) -> DKReturnCode:
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen")
            return rc
        if recipe_name is None or isinstance(recipe_name, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe_name")
            return rc
        if variation_name is None or isinstance(variation_name, str) is False:
            rc.set(rc.DK_FAIL, "issue with variation_name")
            return rc
        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/validate/{kitchen}/{recipe_name}/{variation_name}"
        try:
            payload = {"files": normalize_dict_keys(changed_files, UNIX)}

            response = requests.post(url, headers=self._get_common_headers(), data=json.dumps(payload))
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"recipe_validate: exception: {c}")
            return rc

        rdict = self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, normalize_recipe_validate(rdict["results"], WIN))
        return rc

    def revert_kitchen(self, kitchen: str, sha: str) -> str:
        url = f"{self.get_url_for_direct_rest_call()}/v2/kitchen/revert/{kitchen}/{sha}"
        response = requests.post(url, headers=self._get_common_headers())
        rdict = self.parse_response(response)
        return rdict

    def revert_kitchen_preview(self, kitchen: str) -> Tuple[str, str, str]:
        url = f"{self.get_url_for_direct_rest_call()}/v2/kitchen/revert/{kitchen}"
        response = requests.get(url, headers=self._get_common_headers())
        rdict = self.parse_response(response)
        return rdict["before_sha"], rdict["after_sha"], rdict["preview_url"]

    def kitchen_history(self, kitchen_name: str, count: int) -> list:
        url = f"{self.get_url_for_direct_rest_call()}/v2/kitchen/history/{kitchen_name}"
        payload = {"per_page": count}
        response = requests.get(url, headers=self._get_common_headers(), data=json.dumps(payload))
        response_dict = self.parse_response(response)
        return response_dict["commits"]

    def kitchen_merge_preview(self, from_kitchen: str, to_kitchen: str) -> JSONData:
        """
        preview of kitchen merge
        '/v2/kitchen/merge/<string:kitchenname>/<string:parentkitchen>', methods=['GET']
        :param self: DKCloudAPI
        :param from_kitchen: string
        :param to_kitchen: string
        :rtype: dict
        """
        url = f"{self.get_url_for_direct_rest_call()}/v2/kitchen/merge/{from_kitchen}/{to_kitchen}"
        response = requests.get(url, headers=self._get_common_headers())
        rdict = self.parse_response(response)
        return normalize_recipe_dict_kmp(rdict, WIN)

    def kitchens_merge(self, from_kitchen: str, to_kitchen: str, resolved_conflicts: Optional[JSONData] = None) -> str:
        """
        '/v2/kitchen/merge/<string:kitchenname>/<string:parentkitchen>', methods=['POST']
        :param self: DKCloudAPI
        :param from_kitchen: string
        :param to_kitchen: string
        :param resolved_conflicts: dict
        :rtype: dict
        """
        url = f"{self.get_url_for_direct_rest_call()}/v2/kitchen/merge/{from_kitchen}/{to_kitchen}"

        pdict = {"files": normalize_dict_keys(resolved_conflicts, UNIX)}
        working_dir = os.path.join(self.get_merge_dir(), f"{from_kitchen}_to_{to_kitchen}")
        pdict["source_kitchen_sha"] = DKFileHelper.read_file(os.path.join(working_dir, "source_kitchen_sha"))
        pdict["target_kitchen_sha"] = DKFileHelper.read_file(os.path.join(working_dir, "target_kitchen_sha"))
        response = requests.post(url, data=json.dumps(pdict), headers=self._get_common_headers())
        rdict = self.parse_response(response)

        if rdict["sha_expired"]:
            raise Exception(rdict["error_message"])

        if (
            "merge-kitchen-result" not in rdict
            or "status" not in rdict["merge-kitchen-result"]
            or rdict["merge-kitchen-result"]["status"] != "success"
        ):
            raise Exception("kitchen_merge_manual: backend returned with error status.\n")

        return f'{self._config.get_ip()}:{self._config.get_port()}/{rdict["merge-kitchen-result"]["url"]}'

    def merge_file(
        self,
        kitchen: Optional[str],
        recipe: Optional[str],
        file_path: Optional[str],
        file_contents: Optional[JSONData],
        orig_head: Optional[str],
        last_file_sha: Optional[str],
    ) -> DKReturnCode:
        """
        Returns the result of merging a local file with the latest version on the remote.
        This does not cause any side-effects on the server, and no actual merge is performed in the remote repo.
        /v2/file/merge/<string:kitchenname>/<string:recipename>/<path:filepath>, methods=['POST']
        :param kitchen: name of the kitchen where this file lives
        :param recipe: name of the recipe that owns this file
        :param file_path: path to the file, relative to the recipe
        :param file_contents: contents of the file
        :param orig_head: sha of commit head of the branch when this file was obtained.
        :param last_file_sha: The sha of the file when it was obtained from the server.
        :return: dict
        """
        rc = DKReturnCode()
        if (
            kitchen is None
            or isinstance(kitchen, str) is False
            or recipe is None
            or isinstance(recipe, str) is False
            or file_path is None
            or isinstance(file_path, str) is False
            or orig_head is None
            or isinstance(orig_head, str) is False
            or last_file_sha is None
            or isinstance(last_file_sha, str) is False
            or file_contents is None
        ):
            rc.set(rc.DK_FAIL, "One or more parameters is invalid. ")
            return rc

        params = dict()
        params["orig_head"] = orig_head
        params["last_file_sha"] = last_file_sha
        params["content"] = file_contents.decode("utf-8")
        adjusted_file_path = normalize(file_path, UNIX)
        url = f"{self.get_url_for_direct_rest_call()}/v2/file/merge/{kitchen}/{recipe}/{adjusted_file_path}"
        try:
            response = requests.post(url, data=json.dumps(params), headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            print(f"merge_file: exception: {c}")
            return None

        rdict = self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, normalize_dict_value(rdict, "file_path", WIN))
        return rc

    def recipe_status(self, kitchen: str, recipe: str, local_dir: Optional[str] = None) -> Any:
        """
        gets the status of a recipe
        :param self: DKCloudAPI
        :param kitchen: string
        :param recipe: string
        :param local_dir: string --
        :rtype: dict
        """
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen parameter")
            return rc
        if recipe is None or isinstance(recipe, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe parameter")
            return rc
        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/tree/{kitchen}/{recipe}"
        try:
            response = requests.get(url, headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"get_recipe: exception: {c}")
            return rc

        rdict = self.parse_response(response)
        normalize_recipe_dict(rdict, WIN)

        # Now get the local sha.
        if local_dir is None:
            check_path = os.getcwd()
        else:
            if os.path.isdir(local_dir) is False:
                print(f"Local path {local_dir} does not exist")
                return None
            else:
                check_path = local_dir
        local_sha = get_directory_sha(self.get_ignore(), check_path)

        if recipe not in rdict["recipes"]:
            raise Exception(f"Recipe {recipe} does not exist on remote.")

        remote_sha = rdict["recipes"][recipe]

        rv = compare_sha(self.get_ignore(), remote_sha, local_sha, local_dir, recipe)
        rv["recipe_sha"] = rdict["ORIG_HEAD"]
        rc.set(rc.DK_SUCCESS, None, rv)
        return rc

    # returns a recipe
    def recipe_tree(self, kitchen: Optional[str], recipe: Optional[str]) -> DKReturnCode:
        """
        gets the status of a recipe
        :param self: DKCloudAPI
        :param kitchen: string
        :param recipe: string
        :rtype: dict
        """
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen parameter")
            return rc
        if recipe is None or isinstance(recipe, str) is False:
            rc.set(rc.DK_FAIL, "issue with recipe parameter")
            return rc
        url = f"{self.get_url_for_direct_rest_call()}/v2/recipe/tree/{kitchen}/{recipe}"
        try:
            response = requests.get(url, headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"recipe_tree: exception: {c}")
            return rc
        rdict = self.parse_response(response)
        remote_sha = rdict["recipes"][recipe]
        rc.set(rc.DK_SUCCESS, None, remote_sha)
        return rc

    # --------------------------------------------------------------------------------------------------------------------
    #  Order commands
    # --------------------------------------------------------------------------------------------------------------------
    #  Cook a recipe variation in a kitchen
    def create_order(
        self,
        kitchen: str,
        recipe_name: str,
        variation_name: str,
        node_name: Optional[str] = None,
        parameters: Optional[JSONData] = None,
        now: Optional[bool] = False,
    ) -> DKReturnCode:
        return self._api_helper.create_order(
            kitchen, recipe_name, variation_name, node_name=node_name, parameters=parameters, now=now
        )

    def order_resume(self, kitchen: str, serving_hid: Optional[str]) -> DKReturnCode:
        rc = DKReturnCode()
        if serving_hid is None or isinstance(serving_hid, str) is False:
            rc.set(rc.DK_FAIL, "issue with orderrun_id")
            return rc

        pdict = dict()
        pdict["serving_hid"] = quote(serving_hid)
        pdict["kitchen_name"] = kitchen
        orderrun_id = None

        url = f"{self.get_url_for_direct_rest_call()}/v2/order/resume/{orderrun_id}"
        try:
            response = requests.put(url, data=json.dumps(pdict), headers=self._get_common_headers())
        except (RequestException, ValueError) as c:
            rc.set(rc.DK_FAIL, f"orderrun_delete: exception: {c}")
            return rc

        rdict = self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, rdict["order_id"])
        return rc

    # Get the details about a Order-Run (fka Serving)
    def orderrun_detail(self, kitchen: Optional[str], pdict: JSONData, return_all_data: bool = False) -> DKReturnCode:
        """
        api.add_resource(OrderDetailsV2, '/v2/order/details/<string:kitchenname>', methods=['POST'])
        :param self: DKCloudAPI
        :param kitchen: string
        :param pdict: dict
        :param return_all_data: boolean
        :rtype: DKReturnCode
        """
        return convert_return_code(self._api_helper.orderrun_detail(kitchen, pdict))

    def get_order_run_full_log(self, kitchen: str, order_run_id: str) -> JSONData:
        url = f"{self.get_url_for_direct_rest_call()}/v2/order/export/logs/{kitchen}/{quote(order_run_id)}"
        try:
            response = requests.get(url, headers=self._get_common_headers())
        except (RequestException, ValueError) as c:
            raise Exception(f"get_order_run_full_log: exception: {c}")
        rdict = self.parse_response(response)
        return rdict["log"]

    def list_order(
        self,
        kitchen: Optional[str],
        order_count: int = 5,
        order_run_count: int = 3,
        start: int = 0,
        recipe: Optional[str] = None,
        save_to_file: Optional[str] = None,
    ) -> DKReturnCode:
        """
        List the orders for a kitchen or recipe
        """
        rc = DKReturnCode()
        if kitchen is None or isinstance(kitchen, str) is False:
            rc.set(rc.DK_FAIL, "issue with kitchen parameter")
            return rc

        if recipe:
            url = f"{self.get_url_for_direct_rest_call()}/v2/order/status/{kitchen}?start={start}&count={order_count}&scount={order_run_count}&r={recipe}"
        else:
            url = f"{self.get_url_for_direct_rest_call()}/v2/order/status/{kitchen}?start={start}&count={order_count}&scount={order_run_count}"
        try:
            response = requests.get(url, headers=self._get_common_headers())
        except (RequestException, ValueError, TypeError) as c:
            rc.set(rc.DK_FAIL, f"get_recipe: exception: {c}")
            return rc
        rdict = self.parse_response(response)
        if save_to_file is not None:
            import pickle

            pickle.dump(rdict, open(save_to_file, "wb"))

        rc.set(rc.DK_SUCCESS, None, rdict)
        return rc

    def order_delete_all(self, kitchen: Optional[str]) -> DKReturnCode:
        """
        api.add_resource(OrderDeleteAllV2, '/v2/order/deleteall/<string:kitchenname>', methods=['DELETE'])
        :param self: DKCloudAPI
        :param kitchen: string
        :rtype: DKReturnCode
        """
        return convert_return_code(self._api_helper.order_delete_all(kitchen))

    def order_delete_one(self, kitchen: str, serving_book_hid: Optional[str]) -> DKReturnCode:
        """
        api.add_resource(OrderDeleteV2, '/v2/order/delete/<string:orderid>', methods=['DELETE'])
        :param self: DKCloudAPI
        :param order_id: string
        :rtype: DKReturnCode
        """
        rc = DKReturnCode()
        if serving_book_hid is None or isinstance(serving_book_hid, str) is False:
            rc.set(rc.DK_FAIL, "issue with order_id")
            return rc
        order_id = None
        pdict = dict()
        serving_book_hid2 = quote(serving_book_hid)
        pdict["serving_book_hid"] = serving_book_hid2
        pdict["kitchen_name"] = kitchen
        url = f"{self.get_url_for_direct_rest_call()}/v2/order/delete/{order_id}"
        try:
            response = requests.delete(url, data=json.dumps(pdict), headers=self._get_common_headers())
        except (RequestException, ValueError) as c:
            rc.set(rc.DK_FAIL, f"order_delete_one: exception: {c}")
            return rc
        self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, None)
        return rc

    # Get the details about a Order-Run (fka Serving)
    def delete_orderrun(self, kitchen: str, serving_hid: Optional[str]) -> DKReturnCode:
        """
        api.add_resource(ServingDeleteV2, '/v2/serving/delete/<string:servingid>', methods=['DELETE'])
        """
        rc = DKReturnCode()
        if serving_hid is None or isinstance(serving_hid, str) is False:
            rc.set(rc.DK_FAIL, "issue with orderrun_id")
            return rc
        pdict = dict()
        pdict["serving_hid"] = quote(serving_hid)
        pdict["kitchen_name"] = kitchen
        orderrun_id = None

        url = f"{self.get_url_for_direct_rest_call()}/v2/serving/delete/{orderrun_id}"
        try:
            response = requests.delete(url, data=json.dumps(pdict), headers=self._get_common_headers())
            self.parse_response(response)
            rc.set(rc.DK_SUCCESS, None, None)
            return rc
        except (RequestException, ValueError) as c:
            rc.set(rc.DK_FAIL, f"orderrun_delete: exception: {c}")
            return rc

    def order_pause(self, kitchen: str, order_id: str) -> DKReturnCode:
        return convert_return_code(self._api_helper.order_pause(kitchen, order_id))

    def order_unpause(self, kitchen: str, order_id: str) -> DKReturnCode:
        return convert_return_code(self._api_helper.order_unpause(kitchen, order_id))

    def order_stop(self, kitchen: str, serving_book_hid: Optional[str]) -> DKReturnCode:
        """
        api.add_resource(OrderStopV2, '/v2/order/stop/<string:orderid>', methods=['PUT'])
        """
        rc = DKReturnCode()
        if serving_book_hid is None or isinstance(serving_book_hid, str) is False:
            rc.set(rc.DK_FAIL, "issue with order id")
            return rc
        pdict = dict()
        serving_book_hid2 = quote(serving_book_hid)
        pdict["serving_book_hid"] = serving_book_hid2
        pdict["kitchen_name"] = kitchen
        order_id = None
        url = f"{self.get_url_for_direct_rest_call()}/v2/order/stop/{order_id}"
        try:
            response = requests.put(url, data=json.dumps(pdict), headers=self._get_common_headers())
        except (RequestException, ValueError) as c:
            rc.set(rc.DK_FAIL, f"order_stop: exception: {c}")
            return rc

        self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, None)
        return rc

    def orderrun_stop(self, kitchen: str, orderrun_id: Optional[str]) -> DKReturnCode:
        """
        api.add_resource(ServingStopV2, '/v2/serving/stop/<string:servingid>', methods=['Put'])
        """
        rc = DKReturnCode()
        if orderrun_id is None or isinstance(orderrun_id, str) is False:
            rc.set(rc.DK_FAIL, "issue with orderrun_id")
            return rc

        pdict = dict()
        pdict["serving_hid"] = quote(orderrun_id)
        pdict["kitchen_name"] = kitchen

        url = f"{self.get_url_for_direct_rest_call()}/v2/serving/stop/{orderrun_id}"
        try:
            response = requests.put(url, data=json.dumps(pdict), headers=self._get_common_headers())
        except (RequestException, ValueError) as c:
            rc.set(rc.DK_FAIL, f"order_stop: exception: {c}")
            return rc
        self.parse_response(response)
        rc.set(rc.DK_SUCCESS, None, None)
        return rc
