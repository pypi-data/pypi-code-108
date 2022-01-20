# -*- coding: utf-8 -*-

import base64
import click
import json
import os
import shutil
import sys
import zlib

from DKCloudCommand.modules.DKCCUserTracking import UserTracking

from typing import Callable, List, Tuple, Union, Set, Any, Optional
from jinja2 import Template
from prettytable import PrettyTable, PLAIN_COLUMNS

from DKCommon.Constants import VAULT_GLOBAL
from DKCommon.DKPathUtils import is_windows_os

from DKCloudCommand.modules.DKActiveServingWatcher import DKActiveServingWatcherSingleton
from DKCloudCommand.modules.DKCloudAPI import DKCloudAPI
from DKCommon.DKFileEncode import DKFileEncode
from DKCloudCommand.modules.DKDateHelper import DKDateHelper
from DKCloudCommand.modules.DKFileHelper import DKFileHelper
from DKCloudCommand.modules.DKKitchenDisk import DKKitchenDisk, DK_DIR
from DKCloudCommand.modules.DKRecipeDisk import DKRecipeDisk
from DKCloudCommand.modules.DKReturnCode import DKReturnCode
from DKCloudCommand.modules.DKZipHelper import DKZipHelper
from DKCommon.typing import JSONData


KITCHEN_REVERT_DIR = "kitchen-revert"


def check_api_param_decorator(func: Callable) -> Callable:
    def check_api_wrapper(*args, **kwargs):
        if not isinstance(args[0], DKCloudAPI):
            if "modules.DKCloudAPI.DKCloudAPI" in str(type(args[0])):
                return func(*args, **kwargs)
            else:
                return "ERROR: DKCloudCommandRunner bad parameters \n"
        else:
            return func(*args, **kwargs)

    return check_api_wrapper


def print_result_decorator(func: Callable) -> Callable:
    def print_return_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if os.environ.get("DEBUG", False):
            print(f"{func.__module__}.{func.__name__}{args} returns\n{result}")
        return result

    return print_return_wrapper


# The goal of this file is to take the output from the CLI commands and
#  pretty print them for the user (human)
# Eventually make different types of output formats
#  ould add JSON (json), tab-delimited (text), ascii-formatted table (table)


class DKCloudCommandRunner(object):
    def __init__(self) -> None:
        pass

    TESTRESULTS = "testresults"
    TIMINGRESULTS = "timingresults"
    STATUSES = "statuses"
    SERVING = "serving"
    LOGS = "log"
    RECIPENAME = "recipe"
    ORDER_RUN_ID = "serving-id"
    KITCHEN = "kitchenname"
    STATE = "state"
    SUMMARY = "summary"
    TIMESTAMP = "start-time"

    ORDER_ID = "order_id"
    HID = "hid"

    @staticmethod
    @check_api_param_decorator
    def rude(dk_api: DKCloudAPI) -> str:
        rude = dk_api.rude()
        if rude is None:
            rs = "ERROR:  DKCloudCommand.rude failed"
        else:
            rs = f"DKCloudCommand.rude = {rude}\n"
        return rs

    @staticmethod
    def tree_view(
        user: str,
        kitchen_list: List[JSONData],
        node_name: Optional[str],
        tree_kitchen_dict: JSONData,
        prefix: str = "",
        output: List[str] = [],
    ) -> str:
        vert_line = "│"
        vert_line_mid = "├"
        vert_line_end = "└"

        box_char = ""
        if node_name is None or node_name == "master":
            DKCloudCommandRunner.print_node(user, kitchen_list, node_name, prefix, box_char, output)
        children = tree_kitchen_dict.get(node_name, None)
        if children is not None:
            for i, child in enumerate(children):
                if (i == 0 and len(children) == 1) or i == len(children) - 1:
                    box_char = vert_line_end
                else:
                    box_char = vert_line_mid
                DKCloudCommandRunner.print_node(user, kitchen_list, child, prefix, box_char, output)
                # for un-indenting the next parent sibling
                old_prefix = prefix
                prefix += " " if i == len(children) - 1 else vert_line
                prefix += "  "
                DKCloudCommandRunner.tree_view(user, kitchen_list, child, tree_kitchen_dict, prefix, output)
                # for un-indenting the next parent sibling
                prefix = old_prefix
        return "\n".join(output)

    @staticmethod
    def print_node(
        user: str,
        kitchen_list: List[JSONData],
        name: str,
        prefix: str,
        box_char: str,
        output: List[str],
    ) -> None:
        connector = "─ "

        if name is None:
            no_parent = click.style("No parent", fg="red")
            output.append(no_parent)
            return
        if DKCloudCommandRunner.user_in_kitchen_staff(kitchen_list, name, user):
            closed_tag = ""
        else:
            closed_tag = click.style(" (closed)", fg="magenta")
        styled_name = click.style(name, fg="yellow")
        output.append(f"{prefix}{box_char}{(connector if box_char != '' else '')}{styled_name}{closed_tag}")

    @staticmethod
    def user_in_kitchen_staff(kitchen_list: List[JSONData], kitchen_name: str, user: str) -> bool:
        for kitchen in kitchen_list:
            if kitchen["name"] == kitchen_name:
                staff = kitchen["kitchen-staff"]
                if staff is None or len(staff) == 0:
                    return True
                if user in kitchen["kitchen-staff"]:
                    return True
                return False
        return False

    @staticmethod
    def kitchen_exists(dk_api: DKCloudAPI, kitchen_name: str) -> bool:
        rc = dk_api.list_kitchen()
        if not rc.ok():
            raise Exception(f"Could not check if parent kitchen exists.\n{rc.get_message()}")
        kitchen_list = rc.get_payload()
        if kitchen_list is None or len(kitchen_list) == 0:
            raise Exception("Could not check if parent kitchen exists.\nEmpty kitchen list.")
        for kitchen in kitchen_list:
            if kitchen["name"] == kitchen_name:
                return True
        return False

    @staticmethod
    @check_api_param_decorator
    def list_kitchen(dk_api: DKCloudAPI) -> DKReturnCode:
        rc = dk_api.list_kitchen()
        if rc.ok():
            kl = rc.get_payload()
            if kl is not None and len(kl) > 0:
                has_orphans = False

                for k in kl:
                    if k["parent-kitchen"] is None:
                        has_orphans = True
                        break

                rs = f"kitchen-list returned {len(kl)} kitchens\n\n"
                tree_kitchen_dict = DKCloudCommandRunner.prepare_tree_kitchen_dict(kl)
                rs += DKCloudCommandRunner.tree_view(
                    dk_api.get_config().get_username(),
                    kl,
                    "master",
                    tree_kitchen_dict,
                    output=list(),
                )

                if has_orphans:
                    rs += "\n\nOrphan Kitchens:\n\n"
                    rs += DKCloudCommandRunner.tree_view(
                        dk_api.get_config().get_username(),
                        kl,
                        None,
                        tree_kitchen_dict,
                        output=list(),
                    )

                rc.set_message(rs)
            else:
                rc.set_message("No kitchens found.")
        else:
            rc.set_message(f"unable to list kitchens\nmessage: {rc.get_message()}")

        UserTracking.log_event(
            user_name=dk_api.get_config().get_username(),
            customer=dk_api.get_customer_name(),
            event_name="kitchen-list",
            event_data={
                # Not really useful, but will help make sure events fire
                # TODO:  Is there other things to collect here instead?
                "found_kitchens": (rc.get_message() != "No Kitchens found")
            },
        )
        return rc

    @staticmethod
    def prepare_tree_kitchen_dict(kitchen_list: List[JSONData]) -> JSONData:
        ret = dict()
        sorted_list = sorted(kitchen_list, key=lambda j: j["name"].lower())  # sort the list, ignore case
        for k in sorted_list:
            # populate kitchen dict as pre condition to build the tree view
            if k["name"] == k["parent-kitchen"] == "master":
                continue
            aux_kitchen_list = ret.get(k["parent-kitchen"], None)
            if aux_kitchen_list is None:
                aux_kitchen_list = []
            aux_kitchen_list.append(k["name"])
            ret[k["parent-kitchen"]] = aux_kitchen_list
        return ret

    @staticmethod
    def print_kitchen_children(dk_api: DKCloudAPI, kitchen: str) -> None:
        rc = dk_api.list_kitchen()
        if rc.ok():
            kl = rc.get_payload()
            if kl is not None and len(kl) > 0:
                # Check if kitchen exists
                kitchen_found = False
                for item in kl:
                    if item is not None and "name" in item and item["name"] == kitchen:
                        kitchen_found = True
                        break
                if not kitchen_found:
                    raise Exception(f"Kitchen {kitchen} does not exist.")
                # Check kitchen children
                tree_kitchen_dict = DKCloudCommandRunner.prepare_tree_kitchen_dict(kl)
                if (
                    kitchen not in tree_kitchen_dict
                    or tree_kitchen_dict[kitchen] is None
                    or len(tree_kitchen_dict[kitchen]) == 0
                ):
                    print("No child kitchens found.")
                else:
                    print(
                        click.style(
                            f"The following child kitchens to parent {kitchen} will be orphaned:",
                            fg="red",
                        )
                    )
                    print(
                        DKCloudCommandRunner.tree_view(
                            dk_api.get_config().get_username(), kl, kitchen, tree_kitchen_dict
                        )
                    )
            else:
                raise Exception("No kitchens found.")
        else:
            raise Exception(f"unable to list kitchens\nmessage: {rc.get_message()}")

    @staticmethod
    @check_api_param_decorator
    def vault_info(dk_api: DKCloudAPI, global_secrets: bool, kitchen: Optional[str]) -> str:
        output_message = ""

        def display_vault_info(item: str, payload: JSONData) -> str:
            message = ""
            if item in payload["config"]:
                item_name = "global" if item == VAULT_GLOBAL else item
                message += os.linesep
                message += f"---- {item_name} config ----{os.linesep}"
                if "disabled" in payload["config"][item] and payload["config"][item]["disabled"]:
                    message += " disabled" + os.linesep
                    return message
                if payload["config"][item]["service"] == "default":
                    message += " DataKitchen default" + os.linesep
                    return message
                source_kitchen = DKCloudCommandRunner.get_source_kitchen(dk_api, item, payload=payload)
                if item_name != "global" and source_kitchen:
                    message += f"(Inherited from Parent Kitchen {source_kitchen}){os.linesep}"
                message += f" prefix\t\t\t{payload['config'][item]['prefix']}{os.linesep}"
                message += f" private\t\t{payload['config'][item]['private']}{os.linesep}"
                message += f" service\t\t{payload['config'][item]['service']}{os.linesep}"
                message += f" token\t\t\t******{os.linesep}"
                message += f" url\t\t\t{payload['config'][item]['url']}{os.linesep}"
                if not item == VAULT_GLOBAL:
                    message += f" inheritable\t\t{payload['config'][item]['inheritable']}{os.linesep}"

            return message

        backend_response = dk_api.vault_info(kitchen)

        if global_secrets:
            global_output_message = display_vault_info(VAULT_GLOBAL, backend_response)
            if global_output_message == "":
                global_output_message = f"{os.linesep}Vault is not configured."
            output_message += global_output_message

        if kitchen:
            kitchen_output_message = display_vault_info(kitchen, backend_response)
            if kitchen_output_message == "":
                kitchen_output_message = f"{os.linesep}---- {kitchen} config ----{os.linesep}"
                secret_list_backend_response = dk_api.secret_list("", kitchen)
                if kitchen in secret_list_backend_response and secret_list_backend_response[kitchen]["error"]:
                    kitchen_output_message += secret_list_backend_response[kitchen]["error-message"] + os.linesep
                else:
                    kitchen_output_message += f'{os.linesep}Kitchen {kitchen} Vault is configured as "inherit".'
            output_message += kitchen_output_message

        return output_message

    @staticmethod
    def get_source_kitchen(
        dk_api: DKCloudAPI, kitchen_name: Optional[str], payload: Optional[JSONData] = None
    ) -> Optional[str]:
        source_kitchen = None
        if kitchen_name:
            if payload:
                vault_info_response = payload
            else:
                vault_info_response = dk_api.vault_info(kitchen_name)
            if (
                vault_info_response
                and "config" in vault_info_response
                and kitchen_name in vault_info_response["config"]
                and "sourceKitchen" in vault_info_response["config"][kitchen_name]
            ):
                source_kitchen = vault_info_response["config"][kitchen_name]["sourceKitchen"]
        return source_kitchen

    @staticmethod
    def is_global_vault_disabled(dk_api: DKCloudAPI, payload: Optional[JSONData] = None) -> bool:
        disabled = False
        if payload:
            vault_info_response = payload
        else:
            vault_info_response = dk_api.vault_info(None)

        if vault_info_response:
            disabled = vault_info_response.get("config", {}).get(VAULT_GLOBAL, {}).get("disabled")
            if disabled is None:
                disabled = False
        return disabled

    @staticmethod
    @check_api_param_decorator
    def vault_config(dk_api: DKCloudAPI, kitchen_name: Optional[str], param_dict: JSONData) -> str:
        dk_api.vault_config(kitchen_name, param_dict)
        return "Done."

    @staticmethod
    @check_api_param_decorator
    def vault_delete(dk_api: DKCloudAPI, kitchen_name: Optional[str]) -> str:
        dk_api.vault_delete(kitchen_name)
        return "Done."

    @staticmethod
    def check_secret_path(path: Optional[str]) -> None:
        if path is None:
            return
        wrong_vault_sequence_path = "vault://"
        if wrong_vault_sequence_path in path:
            raise click.ClickException(f'Secret key should not contain "{wrong_vault_sequence_path}"')

    @staticmethod
    @check_api_param_decorator
    def secret_list(dk_api: DKCloudAPI, path: Optional[str], global_secrets: bool, kitchen_name: Optional[str]) -> str:
        source_kitchen = DKCloudCommandRunner.get_source_kitchen(dk_api, kitchen_name)
        payload = dk_api.secret_list(path, kitchen_name)
        output_message = os.linesep
        items = list()
        if global_secrets:
            items.append(VAULT_GLOBAL)
        if kitchen_name:
            items.append(kitchen_name)

        for item in items:
            if item == VAULT_GLOBAL and DKCloudCommandRunner.is_global_vault_disabled(dk_api):
                output_message += f"---- global secrets ----{os.linesep}"
                output_message += f" (global vault is disabled){os.linesep * 2}"
                continue
            if item in payload:
                item_name = "global" if item == VAULT_GLOBAL else item
                output_message += f"---- {item_name} secrets ----{os.linesep}"
                if item_name != "global" and source_kitchen:
                    output_message += f"(Inherited from Parent Kitchen {source_kitchen}){os.linesep}"
                if "error" in payload[item] and payload[item]["error"]:
                    error_message = ""
                    if "error-message" in payload[item]:
                        error_message += f' {payload[item]["error-message"]}{os.linesep}'
                    else:
                        error_message += f"There was an error getting the secrets for {item_name} vault.{os.linesep}"
                    output_message += f" {error_message}{os.linesep}"
                    continue

                if "list" in payload[item]:
                    if item == VAULT_GLOBAL:
                        over_message = " (Overriden in Kitchen) "
                        opposite_item = kitchen_name
                    else:
                        over_message = " (Overrides Global) "
                        opposite_item = VAULT_GLOBAL
                    sorted_list = sorted(payload[item]["list"])
                    if len(sorted_list) == 0:
                        output_message += f" ( No secrets to display ){os.linesep}"
                    for list_item in sorted_list:
                        override_message = ""
                        if (
                            opposite_item
                            and opposite_item in payload
                            and "list" in payload[opposite_item]
                            and list_item in payload[opposite_item]["list"]
                        ):
                            override_message = over_message
                        output_message += f" {list_item}{override_message}{os.linesep}"

            output_message += os.linesep
        if not output_message.strip():
            output_message += f"(Secrets are not available){os.linesep}"

        return output_message

    @staticmethod
    @check_api_param_decorator
    def secret_exists(dk_api: DKCloudAPI, path: str, kitchen_name: Optional[str]) -> Tuple[bool, str]:
        payload = dk_api.secret_list(None, kitchen_name)

        if kitchen_name:
            item = kitchen_name
            item_name = item
        else:
            item = VAULT_GLOBAL
            item_name = "global"

        if item not in payload:
            return False, f"False{os.linesep}"

        if "error" in payload[item] and payload[item]["error"]:
            error_message = "There was an error getting the secrets"
            if "error-message" in payload[item]:
                error_message = payload[item]["error-message"]
            raise Exception(f"{error_message}{os.linesep}")

        if "list" in payload[item]:
            complete_path = "vault://{}".format(path)
            if complete_path in payload[item]["list"]:
                where_was_secret_found = item_name if item_name == "global" else "kitchen"
                return True, f"True (found in {where_was_secret_found} vault) {os.linesep}"

        return False, f"False{os.linesep}"

    @staticmethod
    @check_api_param_decorator
    def secret_write(dk_api: DKCloudAPI, path: str, value: str, kitchen: Optional[str]) -> DKReturnCode:
        if not kitchen and DKCloudCommandRunner.is_global_vault_disabled(dk_api):
            raise Exception("Global vault is disabled")
        rc = dk_api.secret_write(path, value, kitchen)
        if rc.ok():
            rc.set_message("Secret written.")
        else:
            rc.set_message(f"Unable write secret\nmessage: {rc.get_message()}")
        return rc

    @staticmethod
    @check_api_param_decorator
    def secret_delete(dk_api: DKCloudAPI, path: str, kitchen_name: Optional[str]) -> DKReturnCode:
        rc = dk_api.secret_delete(path, kitchen_name)
        if rc.ok():
            rc.set_message("Secret deleted.")
        else:
            rc.set_message(f"Unable deleted secret\nmessage: {rc.get_message()}")
        return rc

    @staticmethod
    def is_vault_config_writable(dk_api: DKCloudAPI, kitchen_name: Optional[str]) -> bool:
        backend_response = dk_api.vault_info(kitchen_name)
        if backend_response and "config" in backend_response and kitchen_name in backend_response["config"]:
            if "sourceKitchen" in backend_response["config"][kitchen_name]:
                return False  # is inherit
            service = backend_response["config"][kitchen_name]["service"]
            if "default" == service:
                return True  # is default
            if "custom" == service:
                return True  # is custom
        return False  # error condition

    @staticmethod
    @check_api_param_decorator
    def user_info(dk_api: DKCloudAPI) -> DKReturnCode:
        rc = DKReturnCode()
        id_token = dk_api.login()

        try:
            user_info = dk_api.get_user_info(id_token)

            if user_info is None:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner problems getting user info")
            else:
                name = user_info["name"] if "name" in user_info else ""
                email = user_info["email"] if "email" in user_info else ""
                customer_name = dk_api.get_customer_name() if not None else ""
                support_email = user_info["support_email"] if "support_email" in user_info else ""
                role = dk_api.get_user_role() if not None else ""

                message = f"""Name:\t\t\t{name}
Email:\t\t\t{email}
Customer Name:\t\t{customer_name}
Support Email:\t\t{support_email}
Role:\t\t\t{role}
"""
                rc.set(rc.DK_SUCCESS, message)

        except Exception:
            rc.set(rc.DK_FAIL, f"{sys.exc_info()[0]}")
        return rc

    @staticmethod
    @check_api_param_decorator
    def get_kitchen(
        dk_api: DKCloudAPI,
        kitchen_name: Optional[str],
        root_dir: str,
        recipes: Optional[List[str]] = None,
        get_all_recipes: bool = False,
    ) -> DKReturnCode:
        rc = DKReturnCode()
        msg_with_status = ""
        if kitchen_name is None or len(kitchen_name) == 0:
            rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - kitchen")
            return rc

        if not DKKitchenDisk.check_kitchen_folder(kitchen_name, root_dir):
            rc.set(rc.DK_FAIL, f"Cannot get Kitchen '{kitchen_name}' to folder '{root_dir}'")
            return rc

        lkrc = dk_api.list_kitchen()
        kl = lkrc.get_payload()
        found_kitchens = [found_kitchen for found_kitchen in kl if found_kitchen["name"] == kitchen_name]
        if len(found_kitchens) > 1:
            rc.set(rc.DK_FAIL, f"ERROR: Found multiple kitchens named '{kitchen_name}'")
            return rc
        elif len(found_kitchens) == 0:
            rc.set(rc.DK_FAIL, f"ERROR: Kitchen '{kitchen_name}' not found on server")
            return rc
        elif len(found_kitchens) == 1:
            if DKKitchenDisk.write_kitchen(kitchen_name, root_dir):
                msg_with_status = f"Got Kitchen '{kitchen_name}'"
            else:
                rc.set(rc.DK_FAIL, f"Problems getting '{kitchen_name}' kitchen")
                return rc

        if get_all_recipes:
            recipe_list = dk_api.list_recipe(kitchen_name).get_payload()
            if recipe_list is None:
                rc.set(rc.DK_FAIL, "ERROR:  DKCloudCommand.list_recipe failed")
                return rc
            else:
                recipes_to_get = recipe_list
        elif recipes is not None and len(recipes) > 0:
            recipes_to_get = recipes
        else:
            recipes_to_get = None

        if recipes_to_get is not None:
            for recipe in recipes_to_get:
                rc = DKCloudCommandRunner.get_recipe(dk_api, kitchen_name, recipe, os.path.join(root_dir, kitchen_name))
                rv = rc.get_message()
                if not rc.ok():
                    rc.set(rc.DK_FAIL, rv)
                    return rc
                else:
                    msg_with_status += "\n" + rv
        rc.set(rc.DK_SUCCESS, msg_with_status)
        return rc

    @staticmethod
    def _list_kitchen_variables(kitchen_overrides: Union[List[str], JSONData]) -> str:
        msg = ""
        if len(kitchen_overrides) > 0:
            field_names = ["Variable Name", "Value"]
            x = PrettyTable()
            x.field_names = field_names
            x.set_style(PLAIN_COLUMNS)
            x.header = True
            x.border = False
            x.align["Variable Name"] = "l"
            x.align["Value"] = "l"
            x.left_padding_width = 1
            row = ["----------------", "----------------"]
            x.add_row(row)

            if isinstance(kitchen_overrides, list):
                for override in kitchen_overrides:
                    x.add_row([override["variable"], override["value"]])
            else:
                for key, value in kitchen_overrides.items():
                    x.add_row([key, value])
            msg += f"\nRecipe Overrides\n{x.get_string()}\n"
        else:
            msg += "No recipe overrides for this kitchen"
        return msg

    @staticmethod
    def config_kitchen(
        dk_api: DKCloudAPI,
        kitchen: str,
        add: Tuple = (),
        get: Tuple = (),
        unset: Tuple = (),
        listall: bool = False,
    ) -> DKReturnCode:
        rc = DKReturnCode()

        if len(add) == 0 and len(get) == 0 and len(unset) == 0 and not listall:
            rc.set(rc.DK_SUCCESS, "Nothing to do")
            return rc

        output_message = ""
        if len(add) != 0 or len(unset) != 0:
            rv = dk_api.modify_kitchen_settings(kitchen, add=add, unset=unset)
            if rv.ok():
                overrides = rv.get_payload()
                modified_message = rv.get_message()
                output_message += modified_message
            else:
                list_msg = "Unable to update recipe overrides.\n"
                rc.set(rc.DK_FAIL, list_msg)
                return rc
        else:
            overrides = None

        if listall:
            if overrides is None:
                rv = dk_api.get_kitchen_settings(kitchen)
                if rv.ok():
                    kitchen_json = rv.get_payload()
                    overrides = kitchen_json["recipeoverrides"]
                    list_msg = DKCloudCommandRunner._list_kitchen_variables(overrides)
                    output_message += list_msg
                else:
                    list_msg = "Unable to get recipe overrides.\n"
                    rc.set(rc.DK_FAIL, list_msg)
                    return rc
            elif overrides is not None:
                list_msg = DKCloudCommandRunner._list_kitchen_variables(overrides)
                output_message += list_msg
            rc.set(rc.DK_SUCCESS, output_message, overrides)
            return rc

        if len(get) != 0:
            rv = dk_api.get_kitchen_settings(kitchen)
            if rv.ok():
                kitchen_json = rv.get_payload()
                overrides = kitchen_json["recipeoverrides"]
                if isinstance(get, tuple) or isinstance(get, list):
                    for get_this in get:
                        matches = [
                            override
                            for override in overrides
                            if DKCloudCommandRunner.is_override_equals(override, get_this)
                        ]
                        if len(matches) == 0:
                            output_message += "none\n"
                        else:
                            output_message += f"{DKCloudCommandRunner.override_get_value(overrides, matches[0])}\n"
                else:
                    matches = [
                        override for override in overrides if DKCloudCommandRunner.is_override_equals(override, get)
                    ]
                    if len(matches) == 0:
                        output_message += "none\n"
                    else:
                        output_message += f"{DKCloudCommandRunner.override_get_value(overrides, matches[0])}\n"
            else:
                msg = f"Unable to get {get}\n"
                rc.set(rc.DK_FAIL, msg)
                return rc
        rc.set(rc.DK_SUCCESS, output_message, overrides)
        return rc

    @staticmethod
    def is_override_equals(override: Union[JSONData, str], override_name: str) -> bool:
        if isinstance(override, dict):
            return override["variable"] == override_name
        else:
            return override == override_name

    @staticmethod
    def override_get_value(overrides: JSONData, override: str) -> str:
        if isinstance(override, dict):
            return override["value"]
        else:
            return overrides[override]

    @staticmethod
    def which_kitchen(dk_api: DKCloudAPI, path: Optional[str] = None) -> DKReturnCode:
        kitchen_name = DKKitchenDisk.find_kitchen_name(path)
        rc = DKReturnCode()
        if kitchen_name is None:
            rs = f"DKCloudCommand.which_kitchen unable to determine kitchen\nmessage: {rc.get_message()}"
            rc.set(rc.DK_FAIL, rs)
            return rc
        else:
            rs = f"You are in kitchen '{kitchen_name}'"
        rc.set(rc.DK_SUCCESS, rs)
        return rc

    @staticmethod
    def which_kitchen_name(path: Optional[str] = None) -> Optional[str]:
        return DKKitchenDisk.find_kitchen_name(path)

    @staticmethod
    @check_api_param_decorator
    def create_kitchen(
        dk_api: DKCloudAPI,
        parent_kitchen: Optional[str],
        new_kitchen: Optional[str],
        description: Optional[str] = None,
    ) -> DKReturnCode:
        kl = dk_api.create_kitchen(parent_kitchen, new_kitchen, description, "junk")
        if kl.ok():
            recipe_overrides = list()
            payload = kl.get_payload()
            if payload and "kitchen" in payload and "recipeoverrides" in payload["kitchen"]:
                recipe_overrides = payload["kitchen"]["recipeoverrides"]

            message = ""
            if len(recipe_overrides) > 0:
                message += "There are recipe overrides at the parent kitchen, which were copied onto the new kitchen:\n"
                for item in recipe_overrides:
                    message += f"Variable: {item}\n"
                message += "\n"

            message += f"DKCloudCommand.create_kitchen created {new_kitchen}\n"
            kl.set_message(message)
        else:
            kl.set_message(f"ERROR:  DKCloudCommand.create_kitchen failed\nmessage: {kl.get_message()}")
        return kl

    @staticmethod
    @check_api_param_decorator
    def delete_kitchen(dk_api: DKCloudAPI, kitchen: Optional[str], synchronous_delete: bool = False) -> DKReturnCode:
        try:
            odrc = dk_api.order_delete_all(kitchen)
            msg = odrc.get_message()
        except Exception as e:
            msg = str(e)
        kl = dk_api.delete_kitchen(kitchen, "delete kitchen", synchronous_delete)
        if kl.ok():
            if msg:
                kl.set_message(f">{msg}<\nKitchen {kitchen} has been deleted\n")
            else:
                kl.set_message(f"Kitchen {kitchen} has been deleted\n")
        else:
            kl.set_message(f">{msg}<\nunable to delete {kitchen}\nmessage: {kl.get_message()}")
        return kl

    @staticmethod
    @check_api_param_decorator
    def list_recipe(dk_api: DKCloudAPI, kitchen: Optional[str]) -> DKReturnCode:
        rc = dk_api.list_recipe(kitchen)
        if rc is None:
            raise Exception("DKCloudCommandRunner.list_recipe received no return code")
        elif not rc.ok():
            s = f"DKCloudCommand.list_recipe failed\nmessage: {rc.get_message()}"
        else:
            rl = rc.get_payload()
            s = f"DKCloudCommand.list_recipe returned {len(rl)} recipes\n"
            for r in rl:
                s += f"  {r}\n"
        rc.set_message(s)
        return rc

    @staticmethod
    @check_api_param_decorator
    def recipe_create(
        dk_api: DKCloudAPI,
        kitchen: Optional[str],
        name: Optional[str],
        template: Optional[str] = None,
    ) -> DKReturnCode:
        rc = DKReturnCode()
        try:
            rc = dk_api.recipe_create(kitchen, name, template)
            if not rc.ok():
                s = f"DKCloudCommand.recipe_create failed\nmessage: {rc.get_message()}"
            else:
                rc.get_payload()
                s = f"DKCloudCommand.recipe_create created recipe {name}\n"
            rc.set_message(s)
        except Exception as e:
            rc.set(rc.DK_FAIL, str(e))
        return rc

    @staticmethod
    @check_api_param_decorator
    def recipe_copy(
        dk_api: DKCloudAPI, kitchen: Optional[str], source: Optional[str], name: Optional[str]
    ) -> DKReturnCode:
        rc = DKReturnCode()
        try:
            rc = dk_api.recipe_copy(kitchen, source, name)
            if not rc.ok():
                s = f"DKCloudCommand.recipe_copy failed\nmessage: {rc.get_message()}"
            else:
                rl = rc.get_payload()
                s = f"DKCloudCommand.recipe_copy created recipe {name} from source {source}\n"
            rc.set_message(s)
        except Exception as e:
            rc.set(rc.DK_FAIL, str(e))
        return rc

    @staticmethod
    @check_api_param_decorator
    def recipe_delete(dk_api: DKCloudAPI, kitchen: Optional[str], name: Optional[str]) -> DKReturnCode:
        print("Deleting remote copy of recipe ...")
        rc = dk_api.recipe_delete(kitchen, name)
        if not rc.ok():
            s = f"DKCloudCommand.recipe_delete failed\nmessage: {rc.get_message()}"
        else:
            print("Done.")
            rl = rc.get_payload()
            kitchen_dir = DKKitchenDisk.find_kitchens_root(kitchen)
            if not kitchen_dir:
                print("Kitchen directory not found, skipping local delete")
            else:
                print("Deleting local copy of recipe ...")
                DKRecipeDisk.write_recipe_state_recipe_delete(kitchen_dir, name)
                recipe_path = os.path.join(kitchen_dir, kitchen, name)
                if os.path.isdir(recipe_path):
                    try:
                        shutil.rmtree(recipe_path)
                    except OSError:
                        print(f"Warning: Could not delete {recipe_path}")
                print("Done.")
            s = f"DKCloudCommand.recipe_delete deleted recipe {name}\n"
        rc.set_message(s)
        return rc

    @staticmethod
    @check_api_param_decorator
    def get_recipe(
        dk_api: DKCloudAPI,
        kitchen: Optional[str],
        recipe_name_param: str,
        start_dir: Optional[str] = None,
        delete_local: bool = False,
        overwrite: bool = False,
        yes: bool = False,
    ) -> DKReturnCode:
        rc = DKReturnCode()
        try:
            if start_dir is None:
                rp = os.getcwd()
            else:
                if os.path.isdir(start_dir) is False:
                    s = f"ERROR: DKCloudCommandRunner path ({start_dir}) does not exist"
                    rc.set(rc.DK_FAIL, s)
                    return rc
                rp = start_dir

            if not DKKitchenDisk.is_kitchen_root_dir(rp):
                recipe_name_found = DKRecipeDisk.find_recipe_name(rp)
                if recipe_name_found != recipe_name_param:
                    rc.set(
                        rc.DK_FAIL,
                        f"ERROR: DKCloudCommandRunner.get_recipe: Requested recipe '{recipe_name_param}', but you are in folder '{rp}'",
                    )
                    return rc
                rp = DKKitchenDisk.find_kitchen_root_dir(rp)

            if os.path.exists(os.path.join(rp, recipe_name_param)):
                # The recipe folder already exists. Compare the files, and see if there will be any conflicts.
                recipe_path = os.path.join(rp, recipe_name_param)
                rc = dk_api.recipe_status(kitchen, recipe_name_param, recipe_path)
                if not rc.ok():
                    rs = f"DKCloudCommand.recipe_status failed\nmessage: {rc.get_message()}"
                    rc.set_message(rs)
                    return rc

                rl = rc.get_payload()

                if overwrite:
                    rl_input = rl["different"]
                else:
                    rl_input = rl["non_local_modified"]
                if len(rl_input) > 0:
                    status, merged_different_files = DKCloudCommandRunner._merge_files(
                        dk_api, kitchen, recipe_name_param, recipe_path, rl_input, overwrite
                    )
                    if not status:
                        diffs_no_recipe = list()
                        for diff in rl_input:
                            diffs_no_recipe.append(diff.split(recipe_name_param + os.sep)[1])
                        s = "ERROR: DKCloudCommandRunner.get_recipe: There was trouble merging the differences between local and remote files.\n"
                        s += "\n".join(diffs_no_recipe)
                        s += "\nUse file-diff and file-merge to resolve issues.\n"
                        s += "No files written locally"
                        rc.set(rc.DK_FAIL, s)
                        return rc
                else:
                    merged_different_files = None

                if "only_remote" in rl and len(rl["only_remote"]) > 0:
                    folders_stripped = list()
                    files_stripped = list()
                    for remote_path, remote_files in rl["only_remote"].items():
                        parts = remote_path.partition(os.sep)
                        if len(remote_files) == 0:
                            folders_stripped.append(parts[2])
                        else:
                            for remote_file in remote_files:
                                files_stripped.append(os.path.join(parts[2], remote_file["filename"]))

                    minimal_paths = DKCloudCommandRunner.find_minimal_paths_to_get(folders_stripped)
                    paths_to_get = []
                    for path, is_path in minimal_paths.items():
                        paths_to_get.append(os.path.join(path, "*"))
                    paths_to_get.extend(files_stripped)
                    only_remote_files_rc = dk_api.get_recipe(kitchen, recipe_name_param, paths_to_get)

                    if only_remote_files_rc is not None:
                        remote_only_recipe_tree = only_remote_files_rc.get_payload()
                    else:
                        remote_only_recipe_tree = None

                else:
                    remote_only_recipe_tree = None

                delete_msg = DKCloudCommandRunner._get_recipe_delete_local(rl, recipe_path, delete_local, yes)

                # Start building the return message
                msg = ""

                # We are trying to get the local up to date with the remote.
                # Different diff results are different actions:
                # local_only - Do nothing
                # same - Do nothing
                # remote_only - Write new
                # different (merged_different_files) - overwrite
                remote_only_msg = ""
                if remote_only_recipe_tree is not None:
                    r = DKRecipeDisk(
                        dk_api.get_ignore(),
                        recipe_sha=remote_only_recipe_tree["ORIG_HEAD"],
                        recipe=remote_only_recipe_tree["recipes"][recipe_name_param],
                        path=rp,
                    )
                    if not r.save_recipe_to_disk(update_meta=False):
                        rc.set(
                            rc.DK_FAIL,
                            f"Problems saving differences and remote only files to disk. {remote_only_recipe_tree}",
                        )
                        return rc

                    remote_only_file_count = 0
                    remote_only_files = list()
                    for recipe_folder_name, recipe_folder_contents in remote_only_recipe_tree["recipes"][
                        recipe_name_param
                    ].items():
                        for remote_only_file in recipe_folder_contents:
                            remote_only_file_count += 1
                            file_path = os.path.join(
                                os.sep.join(recipe_folder_name.split(os.sep)[1:]),
                                remote_only_file["filename"],
                            )
                            remote_only_files.append(f"\t{file_path}")
                    remote_only_msg += f"{remote_only_file_count} new or missing files from remote:\n"
                    remote_only_files.sort()
                    remote_only_msg += "\n".join(remote_only_files)

                merged_files_msg = ""

                if merged_different_files is not None:
                    r = DKRecipeDisk(
                        dk_api.get_ignore(),
                        recipe_sha=rl["recipe_sha"],
                        recipe=merged_different_files,
                        path=rp,
                    )
                    if not r.save_recipe_to_disk(update_meta=False):
                        rc.set(
                            rc.DK_FAIL,
                            f"Problems saving differences and remote only files to disk. {merged_different_files}",
                        )
                        return rc

                    merged_file_count = 0
                    conflicted_file_count = 0
                    for merged_folder, folder_contents in merged_different_files.items():
                        for merged_file in folder_contents:
                            conflict_info = dict()
                            if "text" in merged_file:
                                conflict_info["conflict_tags"] = merged_file["text"]
                            elif "json" in merged_file:
                                conflict_info["conflict_tags"] = merged_file["json"]
                            elif "content" in merged_file:
                                conflict_info["conflict_tags"] = merged_file["content"]

                            merged_file_path = os.path.join(
                                os.sep.join(merged_folder.split(os.sep)[1:]),
                                merged_file["filename"],
                            )
                            if overwrite:
                                merged_files_msg += f"Getting from remote '{merged_file_path}'\n"
                            else:
                                merged_files_msg += f"Auto-merging '{merged_file_path}'\n"
                            merged_file_count += 1
                            if (
                                "<<<<<<<" in conflict_info["conflict_tags"]
                                and "=======" in conflict_info["conflict_tags"]
                                and ">>>>>>>" in conflict_info["conflict_tags"]
                            ):
                                conflicted_file_count += 1
                                conflict_info["filename"] = os.path.basename(merged_file["filename"])
                                conflict_info["from_kitchen"] = kitchen
                                conflict_info["sha"] = "none"
                                conflict_info["to_kitchen"] = kitchen
                                DKRecipeDisk.add_conflict_to_conflicts_meta(
                                    conflict_info, merged_folder, recipe_name_param, rp
                                )
                                merged_files_msg += f"CONFLICT (content): Merge conflict in {merged_file_path}\n"

                if len(delete_msg) > 0:
                    msg += delete_msg + "\n"
                if len(remote_only_msg) > 0:
                    msg += remote_only_msg + "\n"
                if len(merged_files_msg) > 0:
                    msg += merged_files_msg + "\n"

                if len(msg) == 0:
                    msg = "Nothing to do"
                rc.set(DKReturnCode.DK_SUCCESS, msg)
                return rc
            else:
                rc = DKCloudCommandRunner._get_recipe_new(dk_api, kitchen, recipe_name_param, rp)
            return rc
        except Exception as e:
            rc.set(rc.DK_FAIL, str(e))
            return rc

    @staticmethod
    def _get_recipe_delete_local(recipe_status_dict: JSONData, recipe_path: str, delete_local: bool, yes: bool) -> str:
        delete_msg = ""
        if not delete_local:
            return delete_msg

        # Creating local file delete list
        local_file_delete_list = []
        if "only_local" in recipe_status_dict and len(recipe_status_dict["only_local"]) > 0:
            if not yes:
                print("The following local only files will be deleted...\n")
            for item_path, item_files in recipe_status_dict["only_local"].items():
                item_path_no_recipe_name = item_path.partition(os.sep)[2]
                for item_file in item_files:
                    full_path = os.path.join(recipe_path, item_path_no_recipe_name, item_file["filename"])
                    local_file_delete_list.append(full_path)
                    if not yes:
                        print(f"\t{full_path}\n")

            if not yes and len(local_file_delete_list) == 0:
                print("\tNo local only files identified.\n")

        # Creating local dir delete list
        local_dir_delete_list = []
        if "only_local_dir" in recipe_status_dict and len(recipe_status_dict["only_local_dir"]) > 0:
            if not yes:
                print("The following local only directories will be deleted...\n")
            for item_path, item_files in recipe_status_dict["only_local_dir"].items():
                item_path_no_recipe_name = item_path.partition(os.sep)[2]
                full_path = os.path.join(recipe_path, item_path_no_recipe_name)
                local_dir_delete_list.append(full_path)
                if not yes:
                    print(f"\t{full_path}\n")

            if not yes and len(local_dir_delete_list) == 0:
                print("\tNo local only directories identified.\n")

        # Prompting for confirmation
        if len(local_file_delete_list) > 0 or len(local_dir_delete_list) > 0:
            if not yes:
                confirm = input("Are you sure you want to delete these local items? [yes/No]")
                if confirm.lower() == "yes":
                    yes = True
                else:
                    print("Skipping deletion of local items.")

        # Deleting local files
        if yes and len(local_file_delete_list) > 0:
            for item in local_file_delete_list:
                delete_msg += f"deleting local file: {item}\n"
                try:
                    os.remove(item)
                except Exception as e:
                    print(f"{e}")

        # Deleting local dirs
        if yes and len(local_dir_delete_list) > 0:
            for item in local_dir_delete_list:
                delete_msg += f"deleting local directory: {item}\n"
                try:
                    shutil.rmtree(item)
                except Exception:
                    pass

        return delete_msg

    @staticmethod
    def find_minimal_paths_to_get(paths_to_check: List[str]) -> JSONData:
        minimum_paths = {}
        skip_paths = {}
        paths_to_check.sort()
        for outer in range(0, len(paths_to_check)):
            this_path = paths_to_check[outer]
            if this_path not in skip_paths:
                if outer == len(paths_to_check) - 1 and this_path not in skip_paths and this_path not in minimum_paths:
                    minimum_paths[this_path] = False
                    continue
                for inner in range(outer + 1, len(paths_to_check)):
                    next_path = paths_to_check[inner]
                    if next_path not in skip_paths:
                        if DKCloudCommandRunner.is_subdirectory(next_path, this_path):
                            minimum_paths[this_path] = True
                            skip_paths[next_path] = True
            if this_path not in skip_paths and this_path not in minimum_paths:
                minimum_paths[this_path] = False
        return minimum_paths

    @staticmethod
    def os_path_split_asunder(path: str, debug: bool = False) -> List[str]:
        """
        http://stackoverflow.com/a/4580931/171094
        """
        parts = []
        while True:
            newpath, tail = os.path.split(path)
            if debug:
                print(repr(path), (newpath, tail))
            if newpath == path:
                assert not tail
                if path:
                    parts.append(path)
                break
            parts.append(tail)
            path = newpath
        parts.reverse()
        return parts

    # From http://stackoverflow.com/questions/3812849/how-to-check-whether-a-directory-is-a-sub-directory-of-another-directory/17624617#17624617
    @staticmethod
    def is_subdirectory(potential_subdirectory: str, expected_parent_directory: str) -> bool:
        """
        Is the first argument a sub-directory of the second argument?

        :param potential_subdirectory:
        :param expected_parent_directory:
        :return: True if the potential_subdirectory is a child of the expected parent directory

        """

        def _get_normalized_parts(path: str) -> List[str]:
            return DKCloudCommandRunner.os_path_split_asunder(os.path.realpath(os.path.abspath(os.path.normpath(path))))

        # make absolute and handle symbolic links, split into components
        sub_parts = _get_normalized_parts(potential_subdirectory)
        parent_parts = _get_normalized_parts(expected_parent_directory)

        if len(parent_parts) > len(sub_parts):
            # a parent directory never has more path segments than its child
            return False

        # we expect the zip to end with the short path, which we know to be the parent
        return all(part1 == part2 for part1, part2 in zip(sub_parts, parent_parts))

    @staticmethod
    def _merge_files(
        dk_api: DKCloudAPI,
        kitchen_name: str,
        recipe_name: str,
        recipe_path: str,
        differences: JSONData,
        force_remote_file: bool = False,
    ) -> Tuple[bool, JSONData]:
        merged_files = dict()
        status = True
        for folder_name, folder_contents in differences.items():
            for this_file in folder_contents:
                if force_remote_file:
                    file_path = os.path.join(os.sep.join(folder_name.split(os.sep)[1:]), this_file["filename"])
                    file_contents = dk_api.get_file(kitchen_name, recipe_name, file_path)
                    if folder_name not in merged_files:
                        merged_files[folder_name] = list()
                    this_file["text"] = file_contents
                    merged_files[folder_name].append(this_file)
                elif DKFileEncode.is_binary(this_file["filename"]):
                    file_path = os.path.join(os.sep.join(folder_name.split(os.sep)[1:]), this_file["filename"])
                    message1 = f"File {file_path} is binary, skipping file merge with remote..."
                    message2 = 'Use "dk recipe-get -o" to overwrite local copy'
                    click.secho(message1, fg="red")
                    click.secho(message2, fg="red")
                else:
                    rc = DKCloudCommandRunner._merge_file(
                        dk_api, kitchen_name, recipe_name, recipe_path, folder_name, this_file
                    )
                    if rc.ok():
                        payload = rc.get_payload()
                        if "error" not in payload:
                            if folder_name not in merged_files:
                                merged_files[folder_name] = list()

                            this_file["text"] = base64.b64decode(payload["merged_content"]).decode("utf-8")
                            merged_files[folder_name].append(this_file)
                        else:
                            status = False
                    else:
                        status = False
        return status, merged_files

    @staticmethod
    def _merge_file(
        dk_api: DKCloudAPI,
        kitchen_name: str,
        recipe_name: str,
        recipe_path: str,
        folder_name: str,
        file_info: JSONData,
    ) -> Optional[DKReturnCode]:
        # /v2/file/merge/<string:kitchenname>/<string:recipename>/<path:filepath>
        kitchen_root_dir = DKKitchenDisk.find_kitchen_root_dir(recipe_path)
        orig_head = DKRecipeDisk.get_orig_head(recipe_path)
        if orig_head is None:
            return None
        last_file_sha = "none"
        try:
            local_contents = DKFileHelper.read_file(os.path.join(kitchen_root_dir, folder_name, file_info["filename"]))
        except OSError as e:
            print(f"{e.filename} - {e.errno} - {e}")
            return None

        file_path_without_recipe = os.path.join(os.sep.join(folder_name.split(os.sep)[1:]), file_info["filename"])

        the_bytes = local_contents.encode("utf-8")

        file_contents = base64.b64encode(the_bytes)
        rc = dk_api.merge_file(
            kitchen_name,
            recipe_name,
            file_path_without_recipe,
            file_contents,
            orig_head,
            last_file_sha,
        )
        return rc

    @staticmethod
    def _get_recipe_new(dk_api: DKCloudAPI, kitchen: str, recipe_name_param: str, recipe_path: str) -> DKReturnCode:
        rc = DKReturnCode()
        try:
            rc = dk_api.get_recipe(kitchen, recipe_name_param)
            recipe_info = rc.get_payload()
            if isinstance(recipe_info, dict) and "recipes" in recipe_info:
                recipes = recipe_info["recipes"]
                if not rc.ok():
                    s = "ERROR:  DKCloudCommand.get_recipe failed"
                    rc.set_message(f"{s}\nmessage: {rc.get_message()}")
                else:
                    rs = f"DKCloudCommand.get_recipe has {len(recipes[recipe_name_param])} sections\n"
                    for r in recipes[recipe_name_param]:
                        rs += f"  {r}\n"
                    rc.set_message(rs)
                    d = DKRecipeDisk(
                        dk_api.get_ignore(),
                        recipe_info["ORIG_HEAD"],
                        recipes[recipe_name_param],
                        recipe_path,
                    )
                    rv = d.save_recipe_to_disk()
                    if rv is None:
                        s = "ERROR: could not save recipe to disk"
                        rc.set(rc.DK_FAIL, s)
            else:
                if len(rc.get_message()) > 0:
                    rc.set(rc.DK_FAIL, rc.get_message())
                else:
                    rc.set(rc.DK_FAIL, rc.get_payload())
            return rc
        except Exception as e:
            rc.set(rc.DK_FAIL, str(e))
            return rc

    @staticmethod
    def update_local_recipes_with_remote(
        dk_api: DKCloudAPI, kitchens_root: Optional[str], kitchen_name: Optional[str]
    ) -> None:
        try:
            if not kitchens_root or not kitchen_name:
                click.secho("The root path for your kitchens was not found, skipping local checks.")
                return

            click.secho(
                f"Updating Recipes in the local version of Target Kitchen {kitchen_name} to receive merged changes applied to remote..."
            )
            kitchen_path = os.path.join(kitchens_root, kitchen_name)
            if DKKitchenDisk.is_kitchen_root_dir(kitchen_path):
                for subdir in os.listdir(kitchen_path):
                    if not dk_api.get_ignore().ignore(subdir):
                        recipe_path_param = os.path.join(kitchen_path, subdir)
                        shutil.rmtree(recipe_path_param)
                        rc = DKCloudCommandRunner.get_recipe(
                            dk_api,
                            kitchen_name,
                            subdir,
                            start_dir=kitchen_path,
                            delete_local=True,
                            overwrite=True,
                            yes=True,
                        )

                        if not rc.ok():
                            click.secho(f"Could not properly update recipe {subdir}.\n Error is: {rc.get_message()}")
                click.secho(f"{kitchen_path} kitchen has been updated")
            else:
                click.secho("Could not find a local version of Target Kitchen. Skipping local updates.")
        except Exception as e:
            error_message = "Failed to update local recipes with remote.\n"
            if str(e):
                error_message += f"{e}\n"
            if e.strerror:
                error_message += f"{e.strerror}\n"
            if e.filename:
                error_message += f"Offending path is: {e.filename}\n"
            if is_windows_os():
                error_message += "\nPlease:\n"
                error_message += "-> navigate away from the Target Kitchen directory\n"
                error_message += "-> close any open file under that path\n"
            raise Exception(error_message)

    @staticmethod
    def check_local_recipes(dk_api: DKCloudAPI, kitchens_root: str, kitchen_name: str) -> None:
        kitchen_path = os.path.join(kitchens_root, kitchen_name)
        click.secho(
            f"Checking local version of \033[1mKitchen {kitchen_name}\033[0m to make sure that it is in sync with remote..."
        )
        if DKKitchenDisk.is_kitchen_root_dir(kitchen_path):
            for subdir in os.listdir(kitchen_path):
                if subdir != DK_DIR:
                    recipe_path_param = os.path.join(kitchen_path, subdir)
                    if os.path.isdir(recipe_path_param) is False:
                        continue
                    if not DKCloudCommandRunner.is_recipe_status_clean(dk_api, kitchen_name, subdir, recipe_path_param):
                        message = f"Kitchen {kitchen_name} is out of sync. Offending recipe is: {subdir}\n"
                        message += f"Go to this path: {recipe_path_param} \nand check with the following command: dk recipe-status\n"
                        message += "Then, put the recipe in sync again, with recipe-update, file-update, recipe-get or file-get command.\n"
                        message += "After that, rerun kitchen-merge-preview."
                        raise click.ClickException(message)
            click.secho(f"... {kitchen_path} kitchen is in sync to proceed")
        else:
            click.secho(
                f"...No local version of {kitchen_name} Kitchen found. Skipping check to confirm local is in sync with remote."
            )

    @staticmethod
    def is_recipe_status_clean(dk_api: DKCloudAPI, kitchen: str, recipe: str, recipe_path_param: Optional[str]) -> bool:
        rc = DKCloudCommandRunner.recipe_status(dk_api, kitchen, recipe, recipe_path_param)
        if not rc.ok():
            raise Exception(f"Error checking recipe status: {rc.get_message()}")
        rl = rc.get_payload()
        diff_count = len(rl["different"]) + len(rl["only_local"]) + len(rl["only_local_dir"]) + len(rl["only_remote"])
        return diff_count == 0

    @staticmethod
    @check_api_param_decorator
    def recipe_status(
        dk_api: DKCloudAPI, kitchen: str, recipe: str, recipe_path_param: Optional[str] = None
    ) -> DKReturnCode:
        if recipe_path_param is None:
            recipe_path_to_use = os.getcwd()
        else:
            if os.path.isdir(recipe_path_param) is False:
                return f"ERROR: DKCloudCommandRunner path ({recipe_path_param}) does not exist"
            recipe_path_to_use = recipe_path_param
        rc = dk_api.recipe_status(kitchen, recipe, recipe_path_to_use)
        if not rc.ok():
            rc.set_message(f"DKCloudCommand.recipe_status failed\nmessage: {rc.get_message()}")
            return rc
        else:
            rl = rc.get_payload()

            UserTracking.log_event(
                user_name=dk_api.get_config().get_username(),
                customer=dk_api.get_customer_name(),
                event_name="recipe-status",
                event_data={"kitchen_name": kitchen, "recipe_name": recipe, "path_param": recipe_path_param or ""},
            )

            same_file_count = 0
            if len(rl["same"]) > 0:
                for folder_name, folder_contents in rl["same"].items():
                    same_file_count += len(folder_contents)

            local_modified_file_names = list()
            remote_modified_file_names = list()
            local_and_remote_modified_file_names = list()

            DKCloudCommandRunner._get_file_names(rl, "local_modified", local_modified_file_names)
            DKCloudCommandRunner._get_file_names(rl, "remote_modified", remote_modified_file_names)
            DKCloudCommandRunner._get_file_names(rl, "local_and_remote_modified", local_and_remote_modified_file_names)

            local_file_names = list()
            local_folder_names = list()
            if len(rl["only_local"]) > 0:
                for folder_name, folder_contents in rl["only_local"].items():
                    if len(folder_contents) > 0:
                        for this_file in folder_contents:
                            local_file_names.append(
                                os.path.join(
                                    os.sep.join(folder_name.split(os.sep)[1:]),
                                    this_file["filename"],
                                )
                            )

            if len(rl["only_local_dir"]) > 0:
                for folder_name, folder_contents in rl["only_local_dir"].items():
                    parent, folder = os.path.split(folder_name)

                    if not dk_api.get_ignore().ignore(folder):
                        local_folder_names.append(os.sep.join(folder_name.split(os.sep)[1:]))

            remote_file_names = list()
            remote_folder_names = list()
            if len(rl["only_remote"]) > 0:
                for folder_name, folder_contents in rl["only_remote"].items():
                    if len(folder_contents) > 0:
                        for this_file in folder_contents:
                            remote_file_names.append(
                                os.path.join(
                                    os.sep.join(folder_name.split(os.sep)[1:]),
                                    this_file["filename"],
                                )
                            )
                    else:
                        parent, folder = os.path.split(folder_name)

                        if not dk_api.get_ignore().ignore(folder):
                            remote_folder_names.append(os.sep.join(folder_name.split(os.sep)[1:]))

            if len(rl["only_remote_dir"]) > 0:
                for folder_name, folder_contents in rl["only_remote_dir"].items():
                    if not dk_api.get_ignore().ignore(folder_name):
                        remote_folder_names.append(os.sep.join(folder_name.split(os.sep)[1:]))

            msg_lines = []

            def build_msg(msg, items):
                return f"{len(items)} {msg}:\n" + "\n".join([f"\t{i}" for i in items]) + "\n"

            if len(local_modified_file_names) > 0:
                local_modified_file_names.sort()
                msg_lines.append(build_msg("files are modified on local", local_modified_file_names))
            if len(remote_modified_file_names) > 0:
                remote_modified_file_names.sort()
                msg_lines.append(build_msg("files are modified on remote", remote_modified_file_names))
            if len(local_and_remote_modified_file_names) > 0:
                local_and_remote_modified_file_names.sort()
                msg_lines.append(
                    build_msg(
                        "files are modified on both local and remote",
                        local_and_remote_modified_file_names,
                    )
                )
            if len(local_file_names) > 0:
                local_file_names.sort()
                msg_lines.append(build_msg("files are local only", local_file_names))
            if len(local_folder_names) > 0:
                local_folder_names.sort()
                msg_lines.append(build_msg("directories are local only", local_folder_names))
            if len(remote_file_names) > 0:
                remote_file_names.sort()
                msg_lines.append(build_msg("files are remote only", remote_file_names))
            if len(remote_folder_names) > 0:
                remote_folder_names.sort()
                msg_lines.append(build_msg("directories are remote only", remote_folder_names))
            if same_file_count > 0:
                msg_lines.append(f"{same_file_count} files are unchanged\n")
            rc.set_message("\n".join(msg_lines))
            return rc

    @staticmethod
    def _get_all_files(dk_api: DKCloudAPI, path: str, b64_encode_binary_files: bool = False) -> JSONData:
        result = {}
        for item in os.listdir(path):
            if not dk_api.get_ignore().ignore(item):
                item_path = os.path.join(path, item)

                if os.path.isfile(item_path):
                    result[item_path] = DKFileHelper.read_file(
                        item_path, b64_encode_binary_files=b64_encode_binary_files
                    )
                elif os.path.isdir(item_path):
                    result.update(
                        DKCloudCommandRunner._get_all_files(
                            dk_api, item_path, b64_encode_binary_files=b64_encode_binary_files
                        )
                    )
        return result

    @staticmethod
    @check_api_param_decorator
    def update_all_files(
        dk_api: DKCloudAPI,
        kitchen: Optional[str],
        recipe_name: Optional[str],
        recipe_dir: Optional[str],
        message: Optional[str],
        delete_remote: bool = False,
    ) -> DKReturnCode:
        """
        reutrns a string.
        :param dk_api: -- api object
        :param kitchen: string
        :param recipe_name: string  -- kitchen name, string
        :param recipe_dir: string - path to the root of the directory
        :param message: string message -- commit message, string
        :rtype: DKReturnCode
        """
        rc = DKReturnCode()
        try:
            if kitchen is None or recipe_name is None or message is None:
                s = "ERROR: DKCloudCommandRunner bad input parameters"
                rc.set(rc.DK_FAIL, s)
                return rc

            rc = dk_api.recipe_status(kitchen, recipe_name, recipe_dir)
            if not rc.ok():
                rs = f"DKCloudCommand.update_all_files failed\nmessage: {rc.get_message()}"
                rc.set_message(rs)
                return rc

            rl = rc.get_payload()
            rs = DKCloudCommandRunner._check_remote_changes(rl)
            if rs:
                rc.set_message(rs)
                return rc

            rl_len = len(rl["different"]) + len(rl["only_local"])
            rl_len += len(rl["only_remote"]) + len(rl["only_remote_dir"])
            if rl_len == 0:
                rs = "DKCloudCommand.update_all_files no files changed."
                rc.set_message(rs)
                return rc

            changes = {}

            for folder, files in rl["different"].items():
                for f in files:
                    file = os.path.join(folder, f["filename"])
                    path = file[len(recipe_name) + 1 :]
                    full_path = os.path.join(recipe_dir, path)
                    if os.path.isfile(full_path):
                        contents = DKFileHelper.read_file(full_path, b64_encode_binary_files=True)
                        changes[path] = {"contents": contents, "isNew": False}

            for folder, files in rl["only_local"].items():
                if len(files) == 0:
                    item_path_no_recipe_name = folder.partition(os.sep)[2]
                    full_path = os.path.join(recipe_dir, item_path_no_recipe_name)
                    all_files = DKCloudCommandRunner._get_all_files(dk_api, full_path, b64_encode_binary_files=True)

                    for full_path, contents in all_files.items():
                        path = os.path.relpath(full_path, recipe_dir)
                        changes[path] = {"contents": contents, "isNew": True}
                else:
                    for f in files:
                        file = os.path.join(folder, f["filename"])
                        path = file[len(recipe_name) + 1 :]
                        full_path = os.path.join(recipe_dir, path)
                        if os.path.isfile(full_path):
                            file_contents = DKFileHelper.read_file(full_path, b64_encode_binary_files=True)
                            changes[path] = {"contents": file_contents, "isNew": True}
            for folder, files in rl["only_remote"].items():
                for f in files:
                    file = os.path.join(folder, f["filename"])
                    path = file[len(recipe_name) + 1 :]
                    full_path = os.path.join(recipe_dir, path)
                    if not os.path.isfile(full_path) and delete_remote:
                        changes[path] = {}

            # Check if there are empty local dirs, and remove them
            for folder in rl["only_local_dir"].keys():
                item_path_no_recipe_name = folder.partition(os.sep)[2]
                full_path = os.path.join(recipe_dir, item_path_no_recipe_name)
                if not os.listdir(full_path):
                    print(f"Removing empty local directory: {full_path}")
                    try:
                        shutil.rmtree(full_path)
                    except Exception:
                        pass

            rc = dk_api.update_files(kitchen, recipe_name, message, changes)

            if not rc.ok():
                return rc

            data = rc.get_payload()

            DKCloudCommandRunner.write_files(recipe_dir, data["formatted_files"])

            errors = len([i for i in data["issues"] if i["severity"] == "error"])

            issue_report = DKCloudCommandRunner.format_issues(data["issues"])

            msg = ""

            if errors:
                msg = f"\nUnable to update files due to errors in recipe:\n\n{issue_report}\n"
                rc.set_message(msg)

                return rc

            recipe_disk = DKRecipeDisk(dk_api.get_ignore())
            recipe_disk.write_recipe_state(recipe_dir)

            file_results = [k for k in data.keys() if k not in ["status", "issues", "branch", "formatted_files"]]

            file_results.sort()

            # Check if there are files which were not properly updated
            warning_message = None
            failing_files = list()
            for item in file_results:
                if not data[item]:
                    failing_files.append(item)
            if len(failing_files) > 0:
                warning_message = (
                    "The following files could not be updated, please try this command again to complete the update:\n"
                )
                for failing_file in failing_files:
                    warning_message += f"{failing_file}\n"

            created = [f for f in file_results if len(changes[f]) > 0 and "isNew" in changes[f] and changes[f]["isNew"]]
            updated = [
                f for f in file_results if len(changes[f]) > 0 and "isNew" in changes[f] and not changes[f]["isNew"]
            ]
            deleted = [f for f in file_results if len(changes[f]) == 0]

            # update FILE_SHA
            for file_recipe_path in created:
                DKRecipeDisk.write_recipe_state_file_add(recipe_dir, file_recipe_path)
            for file_recipe_path in updated:
                DKRecipeDisk.write_recipe_state_file_update(recipe_dir, file_recipe_path)
            for file_recipe_path in deleted:
                DKRecipeDisk.write_recipe_state_file_delete(recipe_dir, file_recipe_path)

            msg += "Update results:\n\n"
            msg += "New files:\n" + ("\n".join(["\t" + f for f in created]) if len(created) else "\tNone") + "\n"
            msg += "Updated files:\n" + ("\n".join(["\t" + f for f in updated]) if len(updated) else "\tNone") + "\n"
            msg += "Deleted files:\n" + ("\n".join(["\t" + f for f in deleted]) if len(deleted) else "\tNone") + "\n"

            msg += "\nIssues:\n\n" + issue_report

            if warning_message:
                msg += f"\n\nWarning:\n{warning_message}\n"

            rc.set_message(msg)

            return rc
        except Exception as e:
            rc.set(rc.DK_FAIL, str(e))
            return rc

    @staticmethod
    @check_api_param_decorator
    def update_file(
        dk_api: DKReturnCode,
        kitchen: Optional[str],
        recipe_name: Optional[str],
        recipe_dir: Optional[str],
        message: Optional[str],
        files_to_update_param: Optional[Union[List[str], str]],
    ) -> DKReturnCode:
        """
        :param dk_api: -- api object
        :param kitchen: string
        :param recipe_name: string  -- kitchen name, string
        :param recipe_dir: string - path to the root of the directory
        :param message: string message -- commit message, string
        :param files_to_update_param: string  -- file system directory where the recipe file lives
        """
        rc = DKReturnCode()
        try:
            if kitchen is None or recipe_name is None or message is None or files_to_update_param is None:
                s = "ERROR: DKCloudCommandRunner bad input parameters"
                rc.set(rc.DK_FAIL, s)
                return rc

            current_path = os.getcwd()

            # Take a simple string or an array
            if isinstance(files_to_update_param, str):
                files_to_update = [files_to_update_param]
            else:
                files_to_update = files_to_update_param

            # Check recipe status
            rc = dk_api.recipe_status(kitchen, recipe_name, recipe_dir)
            if not rc.ok():
                rs = f"DKCloudCommand.update_file failed\nmessage: {rc.get_message()}"
                rc.set_message(rs)
                return rc

            rl = rc.get_payload()
            rs = DKCloudCommandRunner._check_remote_changes(rl)
            if rs:
                rc.set_message(rs)
                return rc

            # Add new files
            if len(rl["only_local"]) > 0:
                for file_to_update in files_to_update:
                    file_to_update_is_new = False

                    full_path = os.path.join(current_path, file_to_update)
                    relative_path = os.path.relpath(full_path, recipe_dir)
                    relative_path_with_recipe = os.path.join(recipe_name, relative_path)
                    the_path, the_name = os.path.split(relative_path_with_recipe)

                    if the_path in rl["only_local"]:
                        file_list_in_path = rl["only_local"][the_path]
                        if file_list_in_path is not None:
                            if len(file_list_in_path) == 0:
                                file_to_update_is_new = True
                            else:
                                for item in file_list_in_path:
                                    if item["filename"] == the_name:
                                        file_to_update_is_new = True
                                        break
                    if file_to_update_is_new:
                        print(f"Adding: {file_to_update}")
                        DKCloudCommandRunner.add_file(dk_api, kitchen, recipe_name, message, file_to_update)
                        if not rc.ok():
                            rs = f"DKCloudCommand.update_file failed\nmessage: {rc.get_message()}"
                            rc.set_message(rs)
                            return rc

            msg = ""
            for file_to_update in files_to_update:
                try:
                    file_contents = DKFileHelper.read_file(file_to_update)
                except ValueError as e:
                    if len(msg) != 0:
                        msg += "\n"
                    msg += f"ERROR: {e}"
                    rc.set(rc.DK_FAIL, msg)
                    return rc

                full_path = os.path.join(current_path, file_to_update)
                recipe_path = DKRecipeDisk.find_recipe_root_dir()
                recipe_file_path = full_path[len(recipe_path) + 1 :]

                rc = dk_api.update_file(kitchen, recipe_name, message, recipe_file_path, file_contents)
                if not rc.ok():
                    if len(msg) != 0:
                        msg += "\n"
                    msg += f"DKCloudCommand.update_file for {file_to_update} failed\n\tmessage: {rc.get_message()}"
                    rc.set_message(msg)
                    return rc
                else:
                    DKCloudCommandRunner.write_files(recipe_path, rc.get_payload()["formatted_files"])

                    # update recipe meta
                    DKRecipeDisk.write_recipe_state_file_update(recipe_dir, recipe_file_path)
                    if len(msg) != 0:
                        msg += "\n"
                    msg += f"DKCloudCommand.update_file for {file_to_update} succeeded"

            rc.set_message(msg)
            return rc
        except Exception as e:
            rc.set(rc.DK_FAIL, str(e))
            return rc

    @staticmethod
    def write_files(recipe_path: str, files_dict: JSONData) -> None:
        for k, v in files_dict.items():
            full_path = os.path.join(recipe_path, k)
            contents = v
            if contents is not None:
                encoding = DKFileEncode.infer_encoding(full_path)
                DKFileHelper.write_file(full_path, contents, encoding)

    @staticmethod
    @check_api_param_decorator
    def add_file(
        dk_api: DKCloudAPI,
        kitchen: Optional[str],
        recipe_name: Optional[str],
        message: Optional[str],
        api_file_key: Optional[str],
    ) -> DKReturnCode:
        """
        returns a string.
        :param dk_api: -- api object
        :param kitchen: string
        :param recipe_name: string
        :param message: string  -- commit message, string
        :param api_file_key: string  -- directory where the recipe file lives
        :rtype: DKReturnCode
        """
        rc = DKReturnCode()
        if kitchen is None or recipe_name is None or message is None or api_file_key is None:
            s = "ERROR: DKCloudCommandRunner bad input parameters"
            rc.set(rc.DK_FAIL, s)
            return rc

        ig = dk_api.get_ignore()
        if ig.ignore(api_file_key):
            rs = f"DKCloudCommand.add_file ignoring {api_file_key}"
            rc.set_message(rs)
            return rc

        if not os.path.exists(api_file_key):
            s = f"'{api_file_key}' does not exist"
            rc.set(rc.DK_FAIL, s)
            return rc

        recipe_dir = DKRecipeDisk.find_recipe_root_dir()

        api_file_key = os.path.abspath(api_file_key)

        if api_file_key[0 : len(recipe_dir)] != recipe_dir:
            s = f"'{api_file_key}' is not inside recipe directory"
            rc.set(rc.DK_FAIL, s)
            return rc

        in_recipe_path = api_file_key[len(recipe_dir) + 1 :]

        try:
            file_contents = DKFileHelper.read_file(api_file_key)
        except Exception as e:
            s = f"ERROR: {e}"
            rc.set(rc.DK_FAIL, s)
            return rc
        rc = dk_api.add_file(kitchen, recipe_name, message, in_recipe_path, file_contents)
        if rc.ok():
            # update recipe meta
            DKRecipeDisk.write_recipe_state_file_add(recipe_dir, in_recipe_path)
            rs = f"DKCloudCommand.add_file for {in_recipe_path} succeed"
        else:
            rs = f"DKCloudCommand.add_file for {in_recipe_path} failed\nmessage: {rc.get_message()}"
        rc.set_message(rs)
        return rc

    @staticmethod
    @check_api_param_decorator
    def get_file(dk_api: DKCloudAPI, kitchen: str, recipe_name: str, filepath: str) -> DKReturnCode:
        rc = DKReturnCode()
        try:
            current_path = os.getcwd()

            full_path = os.path.join(current_path, filepath)

            recipe_path = DKRecipeDisk.find_recipe_root_dir()
            in_recipe_path = os.path.relpath(full_path, recipe_path)
            rc = dk_api.get_recipe(kitchen, recipe_name, [in_recipe_path])

            if rc.ok():
                rs = f"DKCloudCommand.get_recipe for {filepath} success"
                result = rc.get_payload()
                recipe = result["recipes"][recipe_name]

                relative_path_with_recipe = os.path.join(recipe_name, in_recipe_path)
                the_path, the_name = os.path.split(relative_path_with_recipe)
                folder = recipe[the_path]

                files = [f for f in folder if f["filename"] == the_name]
                if files:
                    file = files[0]

                    data = file["json"] if "json" in file else file["text"]

                    if DKFileEncode.is_binary(full_path):
                        if not isinstance(data, bytes):
                            data = data.encode("utf-8")

                    DKFileHelper.write_file(full_path, data)

                    DKRecipeDisk.write_recipe_state_file_update(recipe_path, in_recipe_path)
            else:
                rs = f"DKCloudCommand.get_recipe for {filepath} failed\nmessage: {rc.get_message()}"
            rc.set_message(rs)
            return rc
        except Exception as e:
            rc.set(rc.DK_FAIL, str(e))
            return rc

    @staticmethod
    @check_api_param_decorator
    def delete_file(
        dk_api: DKCloudAPI,
        kitchen: Optional[str],
        recipe_name: Optional[str],
        message: Optional[str],
        files_to_delete_param: Optional[Union[List[str], str]],
    ) -> DKReturnCode:
        """
        returns a string.
        :param dk_api: -- api object
        :param kitchen: string
        :param recipe_name: string  -- kitchen name, string
        :param message: string message -- commit message, string
        :param files_to_delete_param: path to the files to delete
        :rtype: DKReturnCode
        """
        rc = DKReturnCode()
        if kitchen is None or recipe_name is None or message is None or files_to_delete_param is None:
            s = "ERROR: DKCloudCommandRunner bad input parameters"
            rc.set(rc.DK_FAIL, s)
            return rc

        current_path = os.getcwd()
        recipe_path = DKRecipeDisk.find_recipe_root_dir()

        # Take a simple string or an array
        if isinstance(files_to_delete_param, str):
            files_to_delete = [files_to_delete_param]
        else:
            files_to_delete = files_to_delete_param
        msg = ""
        for file_to_delete in files_to_delete:
            if recipe_path:
                full_path = os.path.join(current_path, file_to_delete)
                in_recipe_path = os.path.relpath(full_path, recipe_path)
            else:
                in_recipe_path = file_to_delete
            basename = os.path.basename(file_to_delete)
            rc = dk_api.delete_file(kitchen, recipe_name, message, in_recipe_path, basename)
            if not rc.ok():
                msg += f"\nDKCloudCommand.delete_file for {file_to_delete} failed on remote delete\nmessage: {rc.get_message()}\n"
                rc.set_message(msg)
                return rc
            else:
                if recipe_path:
                    # update recipe meta
                    DKRecipeDisk.write_recipe_state_file_delete(recipe_path, in_recipe_path)

                    # delete local copy of the file
                    try:
                        os.remove(full_path)
                        msg += f"DKCloudCommand.delete_file for {file_to_delete} succeed on local delete\n"
                    except Exception as e:
                        msg += f"DKCloudCommand.delete_file for {file_to_delete} failed on local delete\n"

                msg += f"DKCloudCommand.delete_file for {file_to_delete} succeed on remote delete\n"
        rc.set_message(msg)
        return rc

    @staticmethod
    @check_api_param_decorator
    def watch_active_servings(dk_api: DKCloudAPI, kitchen: str, period: int) -> str:
        """
        returns a string.
        :param dk_api: -- api object
        :param kitchen: string
        :param period: integer
        :rtype: string
        """

        # try:
        #     p = int(period)
        # except ValueError:
        #     return 'DKCloudCommand.watch_active_servings requires an integer for the period'
        if period <= 0:
            return "DKCloudCommand.watch_active_servings requires a positive period"

        DKActiveServingWatcherSingleton().set_sleep_time(period)
        DKActiveServingWatcherSingleton().set_api(dk_api)
        DKActiveServingWatcherSingleton().set_formatter(DKDateHelper)
        DKActiveServingWatcherSingleton().set_kitchen(kitchen)
        DKActiveServingWatcherSingleton().start_watcher()
        return ""

    # http://stackoverflow.com/questions/19652446/python-program-with-thread-cant-catch-ctrlc
    @staticmethod
    def join_active_serving_watcher_thread_join() -> None:
        if DKActiveServingWatcherSingleton().get_watcher().get_run_thread() is not None:
            try:
                DKActiveServingWatcherSingleton().get_watcher().get_run_thread().join(1)
            except Exception as e:
                print(f"join_active_serving_watcher_thread_join {e}")

    @staticmethod
    def stop_watcher() -> None:
        DKActiveServingWatcherSingleton().stop_watcher()

    @staticmethod
    def watcher_running() -> bool:
        return DKActiveServingWatcherSingleton().should_run()

    @staticmethod
    @check_api_param_decorator
    def get_compiled_order_run(
        dk_api: DKCloudAPI,
        kitchen: Optional[str],
        recipe_name: Optional[str],
        variation_name: Optional[str],
    ) -> DKReturnCode:
        """
        returns a string.
        :param dk_api: -- api object
        :param kitchen: string
        :param recipe_name: string  -- kitchen name, string
        :param variation_name: string -- name of the recipe variation_name to be used
        :rtype: DKReturnCode
        """
        rc = DKReturnCode()
        try:
            rc = dk_api.get_compiled_order_run(kitchen, recipe_name, variation_name)
            compiled_content = rc.get_payload()
            target_dir = os.path.join(os.getcwd(), "compiled-recipe")
            DKCloudCommandRunner._dump_contents(compiled_content, target_dir)
            rs = "DKCloudCommand.get_compiled_order_run succeeded, compiled recipe stored in folder 'compiled-recipe'\n"
            rc.set_message(rs)
        except Exception as e:
            rc.set(rc.DK_FAIL, str(e))
        return rc

    @staticmethod
    @check_api_param_decorator
    def get_compiled_file(
        dk_api: DKCloudAPI,
        kitchen: Optional[str],
        recipe_name: Optional[str],
        variation_name: Optional[str],
        file_path: str,
    ) -> DKReturnCode:
        ret = DKReturnCode()
        try:
            current_path = os.getcwd()

            full_path = os.path.join(current_path, file_path)

            if not os.path.exists(full_path):
                rc = DKReturnCode()
                rc.set(DKReturnCode.DK_FAIL, f"File not found: {file_path}")
                return rc

            recipe_path = DKRecipeDisk.find_recipe_root_dir()

            # The the path relative to recipe root dir.
            recipe_file_path = full_path[len(recipe_path) + 1 :]

            contents = DKFileHelper.read_file(full_path)

            file_data = {
                "path": recipe_file_path,
                "contents": base64.b64encode(contents.encode("utf-8")).decode("utf-8"),
            }

            rc = dk_api.get_compiled_file(kitchen, recipe_name, variation_name, file_data)
            if rc.ok():
                result = rc.get_payload()

                if "compiled-file" in result:
                    if isinstance(result["compiled-file"], dict):
                        output = json.dumps(result["compiled-file"], indent=4)
                    else:
                        output = base64.b64decode(result["compiled-file"]).decode("utf-8")
                    rs = "DKCloudCommand.get_compiled_file succeeded:\n" + output
                    ret.set(DKReturnCode.DK_SUCCESS, rs)
                elif "error-message" in result:
                    rs = f'DKCloudCommand.get_compiled_file failed\n message: {result["error-message"]}\n'
                    ret.set(ret.DK_FAIL, rs)
            else:
                m = rc.get_message()
                rs = f"DKCloudCommand.get_compiled_file failed\nmessage: {m}\n"
                ret.set(ret.DK_FAIL, rs)
        except Exception as e:
            ret.set(ret.DK_FAIL, str(e))
        return ret

    @staticmethod
    @check_api_param_decorator
    def file_history(
        dk_api: DKCloudAPI, kitchen: str, recipe_name: str, file_path: str, change_count: int
    ) -> DKReturnCode:
        current_path = os.getcwd()

        full_path = os.path.join(current_path, file_path)

        if not os.path.exists(full_path):
            rc = DKReturnCode()
            rc.set(DKReturnCode.DK_FAIL, f"File not found: {file_path}")
            return rc

        recipe_path = DKRecipeDisk.find_recipe_root_dir()

        recipe_file_path = full_path[len(recipe_path) + 1 :]

        rc = dk_api.get_file_history(kitchen, recipe_name, recipe_file_path, change_count)
        if rc.ok():

            result = rc.get_payload()

            base_url = f"{dk_api.get_config().get_ip()}:{dk_api.get_config().get_port()}"

            def format_history_entry(entry):
                entry["url"] = f'{base_url}{entry["url"]}'
                return f'Author:\t\t{entry["author"]}\nDate:\t\t{entry["date"]}\nMessage:\t{entry["message"]}\nUrl:\t\t{entry["url"]}\n'

            output = "\n".join([format_history_entry(entry) for entry in result["history"]])

            rs = f"DKCloudCommand.file_history succeeded:\n{output}"

        else:
            m = rc.get_message()
            rs = f"DKCloudCommand.file_history failed\nmessage: {m}\n"
        rc.set_message(rs)
        return rc

    @staticmethod
    def _dump_contents(content: JSONData, target_dir: str) -> None:

        for folder, files in content.items():

            target_folder = os.path.join(target_dir, folder)

            try:
                os.makedirs(target_folder)
            except Exception:
                pass

            for file in files:

                target_file = os.path.join(target_folder, file["filename"])

                if "json" in file:
                    with open(target_file, "w") as f:
                        if isinstance(file["json"], dict):
                            json.dump(file["json"], f, indent=4)
                            continue
                    # if not isinstance(file['json'], dict):
                    DKFileHelper.write_file(target_file, file["json"])

    @staticmethod
    def recipe_variation_list(dk_api: DKCloudAPI, kitchen: str, recipe_name: str, get_remote: bool) -> DKReturnCode:
        rc = DKReturnCode()
        try:
            if get_remote:
                msg = DKCloudCommandRunner.get_remote_recipe_variation_list(dk_api, kitchen, recipe_name)
            else:
                msg = DKCloudCommandRunner.get_local_recipe_variation_list()
            rc.set(DKReturnCode.DK_SUCCESS, msg)
        except Exception as e:
            rc.set(rc.DK_FAIL, str(e))
        return rc

    @staticmethod
    def get_remote_recipe_variation_list(dk_api: DKCloudAPI, kitchen: str, recipe_name: str) -> str:
        file_path = "variations.json"
        file_contents = dk_api.get_file(kitchen, recipe_name, file_path)
        variations_json = json.loads(file_contents)
        return DKCloudCommandRunner.list_recipe_variation_list(variations_json)

    @staticmethod
    def get_local_recipe_variation_list() -> str:
        recipe_path = DKRecipeDisk.find_recipe_root_dir()
        with open(os.path.join(recipe_path, "variations.json"), "r") as file_contents:
            variations_json = json.load(file_contents)
        return DKCloudCommandRunner.list_recipe_variation_list(variations_json)

    @staticmethod
    def list_recipe_variation_list(variations_json: JSONData) -> str:
        variations = variations_json["variation-list"]

        def format(var_entry) -> str:
            name, variation = var_entry
            res = "\t" + name
            if "description" in variation:
                res += ": " + variation["description"]
            return res

        descriptions = [format(var_entry) for var_entry in variations.items()]
        descriptions.sort()

        msg = "Variations:\n" + "\n".join(descriptions) + "\n"
        return msg

    @staticmethod
    def recipe_ingredient_list(dk_api: DKCloudAPI, kitchen: str, recipe_name: str) -> DKReturnCode:
        recipe_path_to_use = os.getcwd()

        with open(os.path.join(recipe_path_to_use, "variations.json"), "r") as fp:
            variations_json = json.load(fp)

        ingredient_key = "ingredient-definition-list"
        if ingredient_key not in variations_json:
            raise Exception("Recipe has no ingredient information.")
        ingredients = variations_json[ingredient_key]

        def format(ingredient: JSONData) -> str:
            return f'\t{ingredient["ingredient-name"]}: {ingredient["description"]}'

        descriptions = [format(ingredient) for ingredient in ingredients]
        descriptions.sort()

        msg = "Ingredients:\n" + "\n".join(descriptions) + "\n"

        rc = DKReturnCode()
        rc.set(DKReturnCode.DK_SUCCESS, msg)

        return rc

    @staticmethod
    def recipe_validate(
        dk_api: DKCloudAPI, kitchen: str, recipe_name: str, variation_name: Optional[str]
    ) -> DKReturnCode:
        rc = DKReturnCode()
        try:
            recipe_root_dir = DKRecipeDisk.find_recipe_root_dir()

            recipe_path_to_use = os.getcwd()

            rc = dk_api.recipe_status(kitchen, recipe_name, recipe_path_to_use)
            if not rc.ok():
                rc.set_message(f"DKCloudCommand.recipe_status failed\nmessage: {rc.get_message()}")
                return rc
            else:
                rl = rc.get_payload()

            changed_files = {}

            if len(rl["only_remote"]) > 0:
                print("Warning: The following files are only present in remote file:")

                for folder_name, folder_contents in rl["only_remote"].items():
                    for this_file in folder_contents:
                        file_path = os.path.join(os.sep.join(folder_name.split(os.sep)[1:]), this_file["filename"])
                        print(f"{file_path}")
                    print("\n")

            if len(rl["different"]) > 0 or len(rl["only_local"]) > 0:
                print("Validating recipe with local changes applied")

                for folder_name, folder_contents in rl["different"].items():
                    for this_file in folder_contents:
                        file_path = os.path.join(os.sep.join(folder_name.split(os.sep)[1:]), this_file["filename"])
                        local_path = os.path.join(recipe_root_dir, file_path)

                        changed_files[file_path] = DKFileHelper.read_file(local_path)

                for folder_name, folder_contents in rl["only_local"].items():
                    for this_file in folder_contents:
                        file_path = os.path.join(os.sep.join(folder_name.split(os.sep)[1:]), this_file["filename"])
                        local_path = os.path.join(recipe_root_dir, file_path)

                        changed_files[file_path] = DKFileHelper.read_file(local_path)

            else:
                print("There are no local changes. Validating recipe with remote version.")

            rc = dk_api.recipe_validate(kitchen, recipe_name, variation_name, changed_files)
            if rc.ok():
                issues = rc.get_payload()

                if len(issues) > 0:
                    print("Recipe issues identified with the following files:")
                    rs = DKCloudCommandRunner.format_issues(issues)
                else:
                    rs = "No recipe issues identified."
            else:
                m = rc.get_message()
                e = m.split("the logfile errors are:nn")
                if len(e) > 1:
                    e2 = DKCloudCommandRunner._decompress(e[len(e) - 1])
                    errors = e2.split("|")
                    re = f"{e[0]} the logfile errors are: "
                    for e in errors:
                        re += f"\n{e}"
                else:
                    re = m
                rs = f"DKCloudCommand.recipe_validate failed\nmessage: {re}\n"
            rc.set_message(rs)
            return rc
        except Exception as e:
            rc.set(rc.DK_FAIL, str(e))
            return rc

    @staticmethod
    def format_issues(issues: List[JSONData]) -> str:
        by_path = {}

        for issue in issues:
            file = issue["file"]
            issue_list = by_path[file] if file in by_path else []
            issue_list.append(DKCloudCommandRunner.format_issue(issue))
            by_path[file] = issue_list

        files = list(by_path.keys())
        files.sort()

        result = []
        for file in files:
            file_name = file if file else "No file"
            result.append(file_name + ":")
            result += [f"\t{issue}" for issue in by_path[file]]

        if len(result) == 0:
            result.append("No issues found")

        return "\n".join(result)

    @staticmethod
    def format_issue(issue: JSONData) -> str:
        result = "\033[33mWarning: \033[39m" if issue["severity"] == "warning" else "\033[31mError: \033[39m"

        result += issue["description"]

        return result

    @staticmethod
    @check_api_param_decorator
    def kitchen_merge_preview(
        dk_api: DKCloudAPI,
        from_kitchen: Optional[str],
        to_kitchen: Optional[str],
        clean_previous_run: bool,
    ) -> DKReturnCode:
        rc = DKReturnCode()
        try:
            if from_kitchen is None or len(from_kitchen) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - source kitchen")
                return rc

            if to_kitchen is None or len(to_kitchen) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - target kitchen")
                return rc

            rdict = dk_api.kitchen_merge_preview(from_kitchen, to_kitchen)
            results = rdict["results"]
            warnings = rdict["warnings"]

            base_working_dir = dk_api.get_merge_dir()
            working_dir = os.path.join(base_working_dir, f"{from_kitchen}_to_{to_kitchen}")
            DKFileHelper.create_dir_if_not_exists(base_working_dir)
            if clean_previous_run is True:
                DKFileHelper.clear_dir(working_dir)
            DKFileHelper.create_dir_if_not_exists(working_dir)
            DKFileHelper.write_file(os.path.join(working_dir, "source_kitchen_sha"), rdict["source_kitchen_sha"])
            DKFileHelper.write_file(os.path.join(working_dir, "target_kitchen_sha"), rdict["target_kitchen_sha"])

            print("\n--- Merge Preview Results (only changed files are being displayed): ---")

            encoding = "base64"

            if len(results) == 0:
                print("Nothing to merge.")

            for line in results:
                line_status = line["status"]
                file_path = line["file"]
                if line_status == "conflict":
                    resolved_file = os.path.join(working_dir, file_path + "." + "resolved")
                    if os.path.isfile(resolved_file):
                        line_status = "resolved"
                    for item in ["base", "left", "right", "merge"]:
                        full_path = os.path.join(working_dir, file_path + "." + item)
                        contents = line[item]
                        DKFileHelper.write_file(full_path, contents, encoding=encoding)
                print(f"{line_status.rjust(8)}\t\t{file_path}")

            print("-" * 71)
            if warnings:
                print(f"\n--- Warnings {'-' * 58}")
                for line in warnings:
                    print(f"-> {line}")
                print("-" * 71)

            if "url" in rdict and rdict["url"]:
                print(f'\nUrl: \t{rdict["url"]}')

            conflict_resolution_msg = """If there are conflicts, remember to resolve using the following commands:
'dk file-merge -sk {source_kitchen} -tk {target_kitchen} file_path' and
'dk file-resolve -sk {source_kitchen} -tk {target_kitchen} file_path'
where 'file_path' is the path as stated in the Merge Preview Results"""
            print(f"\n{conflict_resolution_msg}")

            rc.set(rc.DK_SUCCESS, "\nKitchen merge preview done.")
            return rc
        except Exception as e:
            rc.set(rc.DK_FAIL, f"DKCloudCommandRunner Error.\n{e}")
            return rc

    @staticmethod
    @check_api_param_decorator
    def file_diff(
        dk_api: DKCloudAPI,
        kitchen: Optional[str],
        recipe: Optional[str],
        recipe_dir: str,
        file_path: Optional[str],
    ) -> DKReturnCode:
        rc = DKReturnCode()
        try:
            if kitchen is None or len(kitchen) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - kitchen")
                return rc

            if recipe is None or len(recipe) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - recipe")
                return rc

            if file_path is None or len(file_path) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - file path")
                return rc

            current_path = os.getcwd()
            full_path = os.path.join(current_path, file_path)
            recipe_path = DKRecipeDisk.find_recipe_root_dir()
            recipe_file_path = full_path[len(recipe_path) + 1 :]

            file_content = dk_api.get_file(kitchen, recipe, recipe_file_path)

            base_working_dir = dk_api.get_diff_dir()
            DKFileHelper.create_path_if_not_exists(base_working_dir)
            DKFileHelper.clear_dir(base_working_dir)
            aux_full_path = os.path.join(base_working_dir, kitchen, recipe, recipe_file_path)
            DKFileHelper.write_file(aux_full_path, file_content)

            # Call diff tool
            template_dict = dict()
            template_dict["remote"] = aux_full_path
            template_dict["local"] = os.path.join(recipe_dir, recipe_file_path)

            command_template_string = dk_api.get_config().get_diff_tool()
            command_template = Template(command_template_string)
            command = command_template.render(template_dict)

            print(f"Executing command: {command}\n")
            os.system(command)

            rc.set(rc.DK_SUCCESS, "File diff done.")
            return rc

        except Exception as e:
            rc.set(rc.DK_FAIL, f"DKCloudCommandRunner Error.\n{e}")
            return rc

    @staticmethod
    @check_api_param_decorator
    def file_merge(
        dk_api: DKCloudAPI,
        file_path: Optional[str],
        from_kitchen: Optional[str],
        to_kitchen: Optional[str],
    ) -> DKReturnCode:
        rc = DKReturnCode()
        try:
            if from_kitchen is None or len(from_kitchen) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - source kitchen")
                return rc

            if to_kitchen is None or len(to_kitchen) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - target kitchen")
                return rc

            if file_path is None or len(file_path) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - file path")
                return rc

            base_working_dir = dk_api.get_merge_dir()
            working_dir = os.path.join(base_working_dir, f"{from_kitchen}_to_{to_kitchen}")

            # Call merge tool
            template_dict = dict()
            template_dict["left"] = os.path.join(working_dir, f"{file_path}.left")
            template_dict["base"] = os.path.join(working_dir, f"{file_path}.base")
            template_dict["right"] = os.path.join(working_dir, f"{file_path}.right")
            template_dict["merge"] = os.path.join(working_dir, f"{file_path}.merge")

            # Check the paths exist
            for item in ["left", "base", "right", "merge"]:
                if not os.path.isfile(template_dict[item]):
                    error_message = f"File {template_dict[item]} not found.{os.linesep}"
                    error_message += "The file path is incorrect. "
                    error_message += "Use the file path specified in kitchen-merge-preview command output."
                    rc.set(rc.DK_FAIL, error_message)
                    return rc

            # Render template
            command_template_string = dk_api.get_config().get_merge_tool()
            command_template = Template(command_template_string)
            command = command_template.render(template_dict)

            print(f"Executing command: {command}\n")
            os.system(command)

            rc.set(
                rc.DK_SUCCESS,
                "File merge done. Remember to mark the file as resolved with the command: dk file-resolve",
            )
            return rc

        except Exception as e:
            rc.set(rc.DK_FAIL, f"DKCloudCommandRunner Error.\n{e}")
            return rc

    @staticmethod
    def file_resolve(
        dk_api: DKCloudAPI,
        from_kitchen: Optional[str],
        to_kitchen: Optional[str],
        file_path: Optional[str],
    ) -> DKReturnCode:
        rc = DKReturnCode()
        try:
            if from_kitchen is None or len(from_kitchen) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - source kitchen")
                return rc

            if to_kitchen is None or len(to_kitchen) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - target kitchen")
                return rc

            if file_path is None or len(file_path) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - file path")
                return rc

            base_working_dir = dk_api.get_merge_dir()
            working_dir = os.path.join(base_working_dir, f"{from_kitchen}_to_{to_kitchen}")

            base_file = os.path.join(working_dir, f"{file_path}.base")
            if not os.path.isfile(base_file):
                error_message = "The file path is incorrect. "
                error_message += "Use the file path specified in kitchen-merge-preview command output."
                rc.set(rc.DK_FAIL, error_message)
                return rc
            file_contents = DKFileHelper.read_file(base_file)

            resolved_file = os.path.join(working_dir, f"{file_path}.resolved")
            DKFileHelper.write_file(resolved_file, file_contents)

            rc.set(rc.DK_SUCCESS, "File resolve done.")
            return rc

        except Exception as e:
            rc.set(rc.DK_FAIL, f"DKCloudCommandRunner Error.\n{e}")
            return rc

    @staticmethod
    @check_api_param_decorator
    @print_result_decorator
    def kitchen_merge(dk_api: DKCloudAPI, from_kitchen: Optional[str], to_kitchen: Optional[str]) -> DKReturnCode:
        rc = DKReturnCode()
        working_dir = None
        try:
            if from_kitchen is None or len(from_kitchen) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - source kitchen")
                return rc

            if to_kitchen is None or len(to_kitchen) == 0:
                rc.set(rc.DK_FAIL, "DKCloudCommandRunner bad parameters - target kitchen")
                return rc

            base_working_dir = dk_api.get_merge_dir()
            working_dir = os.path.join(base_working_dir, f"{from_kitchen}_to_{to_kitchen}")

            if not os.path.exists(working_dir):
                raise Exception("Please run kitchen-merge-preview command before running kitchen-merge")

            manual_merge_dict = {}

            # walk the temporary merge directory
            print(f"looking for manually merged files in temporary directory {working_dir} ")
            for dirpath, dirnames, filenames in os.walk(working_dir):
                if len(filenames) > 0:
                    for filename in filenames:
                        if filename.endswith(".base"):
                            full_path = os.path.join(dirpath, filename)
                            aux_path = full_path
                            aux_path = aux_path[: -len(".base")]

                            # look for resolved version of the file in same directory
                            resolved_path = aux_path + ".resolved"
                            if not os.path.isfile(resolved_path):
                                message = (
                                    "There are unresolved conflicts, please resolve "
                                    "through the following sequence of commands:\n"
                                    '1) merge with "file-merge"\n'
                                    '2) mark as resolved with "file-resolve"\n'
                                    '3) Check no other conflicts with "kitchen-merge-preview"\n'
                                    "Offending file encountered is: {filename}"
                                )
                                raise Exception(message)

                            encoding = DKFileEncode.infer_encoding(aux_path)
                            contents = DKFileHelper.read_file(resolved_path, encoding=encoding)
                            print(f"Found {resolved_path}")

                            aux_path = aux_path[len(working_dir + os.sep) :]
                            manual_merge_dict[aux_path] = contents

            if len(manual_merge_dict) == 0:
                print("Calling Merge ...")
            else:
                print("Calling Merge with manual resolved conflicts ...")

            url = dk_api.kitchens_merge(from_kitchen, to_kitchen, manual_merge_dict)

            DKFileHelper.clear_dir(working_dir)

            msg = "Merge done. You can check your changes in target kitchen and delete the source kitchen."
            if url:
                msg += f"\nUrl: {url}\n\n"
            rc.set(rc.DK_SUCCESS, msg)
            return rc

        except Exception as e:
            if "Please run kitchen-merge-preview again" in str(e):
                DKFileHelper.clear_dir(working_dir)
            rc.set(rc.DK_FAIL, f"DKCloudCommandRunner Error.\n{e}")
            return rc

    @staticmethod
    def revert_kitchen(dk_api: DKCloudAPI, kitchen: str, preview: bool = False) -> Tuple[str, Optional[str]]:
        if preview:
            # Call the backend for the preview
            before_sha, after_sha, preview_url = dk_api.revert_kitchen_preview(kitchen)

            # Store the preview sha for future reference
            DKCloudCommandRunner._store_kitchen_revert_preview_sha(dk_api, kitchen, before_sha)

            # Prepare the output
            msg = "Kitchen revert preview done!." + os.linesep + f"Check preview results: {preview_url}"
            return msg, None

        # get kitchen revert preview sha
        before_sha = DKCloudCommandRunner._get_kitchen_revert_preview_sha(dk_api, kitchen)

        # call kitchen revert backend
        rdict = dk_api.revert_kitchen(kitchen, before_sha)
        if rdict["sha_expired"]:
            raise Exception(rdict["error_message"])
        new_kitchen_head = rdict["new_kitchen_head"]
        msg = "Revert Kitchen done!"
        return msg, new_kitchen_head

    @staticmethod
    def _get_kitchen_revert_preview_sha(dk_api: DKCloudAPI, kitchen: str) -> str:
        kitchen_revert_file = os.path.join(
            dk_api.get_config().get_dk_customer_temp_folder(), KITCHEN_REVERT_DIR, kitchen, ".kitchen_revert_file"
        )
        if not os.path.isfile(kitchen_revert_file):
            raise Exception("Run the 'kitchen-revert --preview' command first")
        return DKFileHelper.read_file(kitchen_revert_file)

    @staticmethod
    def _store_kitchen_revert_preview_sha(dk_api: DKCloudAPI, kitchen: str, sha: str):
        kitchen_revert_file = os.path.join(
            dk_api.get_config().get_dk_customer_temp_folder(), KITCHEN_REVERT_DIR, kitchen, ".kitchen_revert_file"
        )
        DKFileHelper.write_file(kitchen_revert_file, sha)

    @staticmethod
    def kitchen_history(dk_api: DKCloudAPI, kitchen_name: str, count: int) -> str:
        ret = list()
        commits = dk_api.kitchen_history(kitchen_name, count)
        for commit in commits:
            ret.append("-- ")
            ret.append(f"author  : {commit['author']}")
            ret.append(f"date    : {commit['date']}")
            ret.append(f"message : {commit['message']}")
            ret.append(f"sha     : {commit['sha']}")
        return os.linesep.join(ret)

    # --------------------------------------------------------------------------------------------------------------------
    #  Order commands
    # --------------------------------------------------------------------------------------------------------------------
    @staticmethod
    @check_api_param_decorator
    def create_order(
        dk_api: DKCloudAPI,
        kitchen: str,
        recipe_name: str,
        variation_name: str,
        node_name: Optional[str] = None,
        parameters: Optional[JSONData] = None,
        now: Optional[bool] = False,
    ) -> DKReturnCode:
        """
        returns a string.
        :param dk_api: -- api object
        :param kitchen: string
        :param recipe_name: string  -- kitchen name, string
        :param variation_name: string -- name of the recipe variation_name to be run
        :param node_name: string -- name of the single node to run
        :param now: boolean -- if the order should run immediately
        :rtype: DKReturnCode
        """
        rc = dk_api.create_order(kitchen, recipe_name, variation_name, node_name, parameters, now)
        if rc.ok():
            payload = rc.payload

            s = f'Order ID is: {payload["order_id"]}\n'
            variable_overrides = None
            if "variable_overrides" in payload:
                variable_overrides = payload["variable_overrides"]
            if variable_overrides is not None and len(variable_overrides) > 0:
                s += "The following variables will be overridden:\n"
                for variable, value in variable_overrides.items():
                    s += f"{variable}: {value}\n"
        else:
            m = rc.message.replace("\\n", "\n")
            e = m.split("the logfile errors are:")
            if len(e) > 1:
                e2 = DKCloudCommandRunner._decompress(e[-1])
                errors = e2.split("|")
                re = f"{e[0]} the logfile errors are: "
                for e in errors:
                    re += f"\n{e}"
            else:
                re = m
            s = f"DKCloudCommand.create_order failed\nmessage:\n\n{re}\n"

        rc_new = DKReturnCode()
        rc_new.set(rc.status, s, payload=rc.payload)
        return rc_new

    @staticmethod
    @check_api_param_decorator
    def order_resume(dk_api: DKCloudAPI, kitchen: str, orderrun_id: str) -> DKReturnCode:
        rc = dk_api.order_resume(kitchen, orderrun_id)
        rc.set_message(f"DKCloudCommand.order_resume {orderrun_id} succeeded\n")
        return rc

    @staticmethod
    @check_api_param_decorator
    def delete_one_order(dk_api: DKCloudAPI, kitchen: Optional[str], order_id: Optional[str]) -> DKReturnCode:
        kl = dk_api.order_delete_one(kitchen, order_id)
        kl.set_message(f"deleted order {order_id}\n")
        return kl

    @staticmethod
    @check_api_param_decorator
    def pause_order(dk_api: DKCloudAPI, kitchen: str, order_id: str) -> DKReturnCode:
        kl = dk_api.order_pause(kitchen, order_id)
        kl.set_message(f"paused order {order_id}\n")
        return kl

    @staticmethod
    @check_api_param_decorator
    def unpause_order(dk_api: DKCloudAPI, kitchen: str, order_id: str) -> DKReturnCode:
        kl = dk_api.order_unpause(kitchen, order_id)
        kl.set_message(f"unpaused order {order_id}\n")
        return kl

    @staticmethod
    @check_api_param_decorator
    def stop_order(dk_api: DKCloudAPI, kitchen: str, order_id: str) -> DKReturnCode:
        kl = dk_api.order_stop(kitchen, order_id)
        kl.set_message(f"stopped order {order_id}\n")
        return kl

    @staticmethod
    @check_api_param_decorator
    def stop_orderrun(dk_api, kitchen: str, orderrun_id: str) -> DKReturnCode:
        kl = dk_api.orderrun_stop(kitchen, orderrun_id)
        kl.set_message(f"stopped order run {orderrun_id}\n")
        return kl

    @staticmethod
    @check_api_param_decorator
    def delete_all_order(dk_api: DKCloudAPI, kitchen: str) -> DKReturnCode:
        kl = dk_api.order_delete_all(kitchen)
        kl.set_message(f"deleted kitchen {kitchen}\n")
        return kl

    @staticmethod
    @check_api_param_decorator
    def orderrun_detail(
        dk_api, kitchen: str, pd: JSONData, full_log: bool = False, log_threshold: str = "INFO"
    ) -> DKReturnCode:
        if DKCloudCommandRunner.SUMMARY in pd:
            display_summary = True
        else:
            display_summary = False
        # always get summary information
        pd[DKCloudCommandRunner.SUMMARY] = True
        rc = dk_api.orderrun_detail(kitchen, pd)
        s = ""
        if not rc.ok():
            s = f"Issue with getting order run details\nmessage: {rc.get_message()}"
            rc.set_message(s)
            return rc

        # we have a list of order runs, find the right dict
        payload = rc.get_payload()
        order_list = payload["orders"] if "orders" in payload else None
        order_run_list = payload["servings"]
        order_run = None
        if DKCloudCommandRunner.HID in pd:
            order_run_id = pd[DKCloudCommandRunner.HID]
            for run in order_run_list:
                if run[DKCloudCommandRunner.HID] == order_run_id:
                    order_run = run
                    break
        elif DKCloudCommandRunner.ORDER_ID in pd:
            order_id = pd[DKCloudCommandRunner.ORDER_ID]
            for run in order_run_list:
                if run[DKCloudCommandRunner.ORDER_ID] == order_id:
                    order_run = run
                    break
        else:
            # find the newest run
            if len(order_run_list) > 0:
                order_run = order_run_list[0]

        if order_run is None:
            rc.set(
                rc.DK_FAIL,
                f"No OrderRun information.  Try using 'dk order-list -k {kitchen}' to see what is available.",
            )
            return rc

        # order_run now contains the dictionary of the order run to display
        # pull out the information and put it in the message string of the rc

        if order_run and display_summary:
            s += "\nORDER RUN SUMMARY\n\n"
            summary = None
            if DKCloudCommandRunner.SUMMARY in order_run:
                summary = order_run[DKCloudCommandRunner.SUMMARY]
            pass
            order_id = order_run[DKCloudCommandRunner.ORDER_ID]
            order = DKCloudCommandRunner._get_order(order_list, order_id)
            order_id = "None"
            if order and "hid" in order:
                order_id = order["hid"]
            s += f"Order ID:\t{order_id}\n"

            order_run_id = order_run[DKCloudCommandRunner.HID]
            s += f"Order Run ID:\t{order_run_id}\n"
            s += f"Status:\t\t{order_run['status']}\n"
            s += f"Kitchen:\t{kitchen}\n"

            if summary and "name" in summary:
                s += f'Recipe:\t\t{summary["name"]}\n'
            else:
                s += "Recipe:\t\tNot available\n"

            s += f'Variation:\t{order_run.get("variation_name", "(unknown)")}\n'

            if summary and "start-time" in summary:
                s += f'Start time:\t{DKDateHelper.format_timestamp(summary["start-time"])}\n'
            else:
                s += "Start time:\tNot available\n"

            run_time = None
            if summary and "total-recipe-time" in summary:
                run_time = summary["total-recipe-time"]
            s += f"Run duration:\t{DKDateHelper.format_timing(run_time)} (H:M:S)\n"

        if (
            order_run
            and DKCloudCommandRunner.TESTRESULTS in order_run
            and isinstance(order_run[DKCloudCommandRunner.TESTRESULTS], str)
        ):
            s += "\nTEST RESULTS"
            s += order_run[DKCloudCommandRunner.TESTRESULTS]
        if (
            order_run
            and DKCloudCommandRunner.TIMINGRESULTS in order_run
            and isinstance(order_run[DKCloudCommandRunner.TIMINGRESULTS], str)
        ):
            s += "\n\nTIMING RESULTS\n\n"
            s += order_run[DKCloudCommandRunner.TIMINGRESULTS]
        if (
            "status" in pd
            and order_run
            and DKCloudCommandRunner.SUMMARY in order_run
            and isinstance(order_run[DKCloudCommandRunner.SUMMARY], dict)
        ):
            s += "\nSTEP STATUS\n\n"
            summary = order_run[DKCloudCommandRunner.SUMMARY]
            nodes = summary.get("nodes")
            if nodes:
                # loop through the sorted keys
                for key in sorted(nodes):
                    value = nodes[key]
                    if isinstance(value, dict):
                        # node/step info is stored as a dictionary, print the node name (key) and status
                        if "status" in value:
                            status = value["status"]
                            s += f"{key}\t{status}\n"
            else:
                s += "Not available\n"

        if order_run and "runstatus" in pd:
            s += order_run["status"]

        if order_run and "disp_order_id" in pd and DKCloudCommandRunner.ORDER_ID in order_run:
            s += order_run[DKCloudCommandRunner.ORDER_ID]

        if order_run and "disp_orderrun_id" in pd and DKCloudCommandRunner.HID in order_run:
            s += order_run[DKCloudCommandRunner.HID]

        if "logs" in pd and pd["logs"] and order_run and DKCloudCommandRunner.LOGS in order_run:
            s += "\n\nLOG\n"
            s += DKCloudCommandRunner._get_logs_from_order_run(order_run, log_threshold)

        if full_log:
            if "serving_hid" not in pd:
                error_message = "Please provide OrderRun ID (--order_run_id) to get the full logs."
                raise Exception(error_message)
            s += "\n\nFULL LOG\n"
            full_log_base64 = dk_api.get_order_run_full_log(kitchen, pd["serving_hid"])
            full_log_zipped = DKFileEncode.b64decode(full_log_base64)

            full_log = DKZipHelper.unzip_first_file_as_string_or_unicode(full_log_zipped)
            s += f"{os.linesep}{full_log}"

        rc.set_message(s)
        return rc

    @staticmethod
    def _get_logs_from_order_run(order_run: JSONData, log_threshold: str) -> str:
        ret = ""
        if order_run and DKCloudCommandRunner.LOGS in order_run:
            logs = order_run[DKCloudCommandRunner.LOGS]["lines"]
            # DEV-2237 don't show disk/memory usage until stats can be isolated per process/container
            # was items = ['datetime', 'record_type', 'disk_free', 'mem_usage', 'message']
            items = ["datetime", "record_type", "thread_name", "message"]
            log_header = f"Log Format:\t\t{' | '.join(items)}{os.linesep}"
            ret += os.linesep + log_header
            showable_log_types = DKCloudCommandRunner._showable_log_types(log_threshold)
            for log in logs:
                if not DKCloudCommandRunner._show_log(log, showable_log_types):
                    continue
                line = [str(log.get(x, "")) for x in items]
                log_line = " | ".join(line)
                ret += os.linesep + log_line
        return ret

    @staticmethod
    def _showable_log_types(log_threshold: str) -> Set[str]:
        ret = set()
        ret.add("ERROR")
        if log_threshold == "ERROR":
            return ret
        ret.add("WARN")
        if log_threshold == "WARN":
            return ret
        ret.add("INFO")
        if log_threshold == "INFO":
            return ret
        ret.add("DEBUG")
        if log_threshold == "DEBUG":
            return ret
        ret.add("TRACE")
        return ret

    @staticmethod
    def _show_log(log: Optional[str], showable_log_types: Set[str]) -> bool:
        if log is None:
            return False
        log_type = log.get("record_type")
        if log_type is None:
            return True
        return log_type in showable_log_types

    @staticmethod
    def _get_order(order_list: List[JSONData], order_id: str) -> Optional[JSONData]:
        ret = None
        for order in order_list:
            if order and "hid" in order and order["hid"] == order_id:
                return order
        return ret

    @staticmethod
    @check_api_param_decorator
    def list_order(
        dk_api: DKCloudAPI,
        kitchen: str,
        order_count: int = 5,
        order_run_count: int = 3,
        start: int = 0,
        recipe: Optional[str] = None,
    ) -> DKReturnCode:
        rc = dk_api.list_order(kitchen, order_count, order_run_count, start, recipe=recipe)
        if not rc.ok():
            s = f"DKCloudCommand.list_order failed\nmessage: {rc.get_message()}"
            rc.set_message(s)
            return rc

        rows = []
        payload = rc.get_payload()
        for order in payload["orders"]:
            # Found an order without any runs. Add it to the list.
            if order["hid"] is not None:
                if order["hid"] in payload["servings"]:
                    order_run_list = payload["servings"][order["hid"]]["servings"]
                else:
                    order_run_list = []
                aux_order = [
                    order["hid"],
                    order["recipe"],
                    order["variation"],
                    order["order-status"],
                    order["schedule"] if "schedule" in order else "",
                    order_run_list,
                ]
                rows.append(aux_order)

        s = ""
        for order in rows:
            s += DKCloudCommandRunner._display_order_summary(order, kitchen)
            count = 1
            for order_run in order[5]:
                s += DKCloudCommandRunner._display_order_run_summary(order_run, count)
                count += 1
            rc.set_message(s)

        return rc

    @staticmethod
    @check_api_param_decorator
    def delete_orderrun(dk_api: DKCloudAPI, kitchen: str, orderrun_id: str) -> DKReturnCode:
        rc = dk_api.delete_orderrun(kitchen, orderrun_id)
        if not rc.ok():
            rc.set_message(
                f"delete_orderrun error. unable to delete orderrun {orderrun_id}\nmessage: {rc.get_message()}"
            )
        else:
            payload = rc.get_payload()
            rc.set_message(f"DKCloudCommand.delete_orderrun {orderrun_id} succeeded\n")
        return rc

    @staticmethod
    @check_api_param_decorator
    def kitchen_settings_get(dk_api: DKCloudAPI, kitchen: str) -> DKReturnCode:
        rc = dk_api.kitchen_settings_json_get(kitchen)
        if not rc.ok():
            rc.set_message(f"kitchen_settings_get error. \nmessage: {rc.get_message()}")
        else:
            message = (
                "DKCloudCommand.kitchen_settings_get succeeded\n"
                "Find the kitchen-settings.json file in the current directory\n"
            )
            rc.set_message(message)
        return rc

    @staticmethod
    @check_api_param_decorator
    def kitchen_settings_update(dk_api: DKCloudAPI, kitchen: Optional[str], filepath: Optional[str]) -> DKReturnCode:
        if kitchen is None or filepath is None:
            s = "ERROR: DKCloudCommandRunner bad input parameters"
            rc = DKReturnCode()
            rc.set(rc.DK_FAIL, s)
            return rc
        rc = dk_api.kitchen_settings_json_update(kitchen, filepath)
        if not rc.ok():
            rc.set_message(f"kitchen_settings_update error. \nmessage: {rc.get_message()}")
        else:
            rc.set_message("DKCloudCommand.kitchen_settings_update succeeded\n")
        return rc

    # Helpers
    @staticmethod
    def _display_order_summary(order_info_list: List[str], kitchen: str) -> str:
        return f"""
ORDER SUMMARY (order ID: {order_info_list[0]})
Kitchen:\t{kitchen}
Recipe:\t\t{order_info_list[1]}
Variation:\t{order_info_list[2]}
Schedule:\t{order_info_list[4]}
Status:\t\t{order_info_list[3]}
"""

    @staticmethod
    def _display_order_run_summary(order_run: JSONData, number: int = -1) -> str:
        s = ""
        if number > 0:
            s += f"\n  {number}.  ORDER RUN\t(OrderRun ID: "
        else:
            s += "\n  ORDER RUN\t(OrderRun ID: "

        order_run_id = order_run["hid"]
        s += f"{order_run_id})\n"
        if "orderrun_status" in order_run:
            s += f'\tOrderRun Status {order_run["orderrun_status"]}\n'
        else:
            s += f'\tStatus:\t\t{order_run["status"]}\n'

        if order_run and "timings" in order_run and "start-time" in order_run["timings"]:
            start_time = order_run["timings"]["start-time"]
            s += f"\tStart time:\t{DKDateHelper.format_timestamp(start_time)}\n"
        else:
            s += "\tStart time:\tNot available\n"

        if order_run and "timings" in order_run and "end-time" in order_run["timings"]:
            end_time = order_run["timings"]["end-time"]
            s += f"\tEnd time:\t{DKDateHelper.format_timestamp(end_time)}\n"
        else:
            s += "\tEnd time:\tNot available\n"

        if order_run and "timings" in order_run and "duration" in order_run["timings"]:
            duration = order_run["timings"]["duration"]
            s += f"\tDuration:\t{DKDateHelper.format_timing(duration)} (H:M:S)\n"
        else:
            s += "\tDuration:\tNot available\n"
        return s

    @staticmethod
    def _get_order_run_top_line(order_run: JSONData) -> str:
        recipe_name = kitchen_name = order_run_id = status = "unknown"
        if DKCloudCommandRunner.RECIPENAME in order_run:
            recipe_name = order_run[DKCloudCommandRunner.RECIPENAME]
        if DKCloudCommandRunner.ORDER_RUN_ID in order_run:
            order_run_id = order_run[DKCloudCommandRunner.ORDER_RUN_ID]
        if DKCloudCommandRunner.KITCHEN in order_run:
            kitchen_name = order_run[DKCloudCommandRunner.KITCHEN]
        if DKCloudCommandRunner.STATE in order_run:
            status = order_run[DKCloudCommandRunner.STATE]
        return (
            f"Recipe ({recipe_name}) in Kitchen({kitchen_name}) with Status({status}) and OrderRun Id({order_run_id})"
        )

    @staticmethod
    # UNUSED METHOD?
    def _dump_order_run_statuses(rc, the_type):
        rs = ""
        for order_run in rc[the_type]:
            if isinstance(order_run, dict) is True and DKCloudCommandRunner.STATUSES in order_run:
                rs += f"Status for {DKCloudCommandRunner._get_order_run_top_line(order_run)}\n"
                rs += f"{order_run[DKCloudCommandRunner.STATUSES]}\n"
        return rs

    @staticmethod
    # UNUSED METHOD?
    def _dump_order_run_logs(rc, the_type):
        rs = ""
        for order_run in rc[the_type]:
            if isinstance(order_run, dict) is True and DKCloudCommandRunner.LOGS in order_run:
                rs += f"Log Files for {DKCloudCommandRunner._get_order_run_top_line(order_run)} \n"
                if order_run[DKCloudCommandRunner.LOGS] is not None and len(order_run[DKCloudCommandRunner.LOGS]) > 0:
                    try:
                        rs += DKCloudCommandRunner._decompress(order_run[DKCloudCommandRunner.LOGS])
                    except (ValueError, TypeError):
                        rs += "unable to decompress log file"
                else:
                    rs += "no log file"
                rs += "\n"
        return rs

    @staticmethod
    # UNUSED METHOD?
    def _dump_order_run_tests(rc, the_type):
        rs = ""
        for order_run in rc[the_type]:
            if isinstance(order_run, dict) is True and DKCloudCommandRunner.TESTRESULTS in order_run:
                rs += f"Test Results for {DKCloudCommandRunner._get_order_run_top_line(order_run)}\n"
                rs += f"{order_run[DKCloudCommandRunner.TESTRESULTS]}\n"
        return rs

    @staticmethod
    # UNUSED METHOD?
    def _dump_order_run_summary(rc, the_type, as_string=False):
        rs = ""
        for order_run in rc[the_type]:
            if isinstance(order_run, dict) is True and DKCloudCommandRunner.SUMMARY in order_run:
                if as_string is True:
                    rs += f"Test Results for {DKCloudCommandRunner._get_order_run_top_line(order_run)}\n"
                    rs += f"{json.dumps(order_run[DKCloudCommandRunner.SUMMARY], indent=4)}\n"
                else:
                    return order_run[DKCloudCommandRunner.SUMMARY]
        return rs

    @staticmethod
    # UNUSED METHOD?
    def _dump_order_run_timings(rc, the_type):
        rs = ""
        for order_run in rc[the_type]:
            if isinstance(order_run, dict) is True and DKCloudCommandRunner.TIMINGRESULTS in order_run:
                rs += f"Timing Results for {DKCloudCommandRunner._get_order_run_top_line(order_run)}\n"
                rs += f"{order_run[DKCloudCommandRunner.TIMINGRESULTS]}\n"
        return rs

    @staticmethod
    # UNUSED METHOD?
    def _split_one_end(path):
        """
        Utility function for splitting off the very end part of a path.
        """
        s = path.rsplit("/", 1)
        if len(s) == 1:
            return s[0], ""
        else:
            return tuple(s)

    @staticmethod
    # UNUSED METHOD?
    def _compress(the_input):
        if isinstance(the_input, str):
            return base64.b64encode(zlib.compress(the_input, 9))
        else:
            raise ValueError("compress requires string input")

    @staticmethod
    def _decompress(the_input: Union[str, Any]) -> bytes:
        if isinstance(the_input, str):
            return zlib.decompress(base64.b64decode(the_input).decode("utf-8"))
        else:
            raise ValueError("decompress requires string input")

    @staticmethod
    # UNUSED METHOD?  (Has test but no other usages)
    def _print_test_results(r) -> str:
        return "File"

    @staticmethod
    def _get_file_names(payload: JSONData, key: str, names: List[str]) -> None:
        if len(payload[key]) > 0:
            for folder_name, folder_contents in payload[key].items():
                if len(folder_contents) > 0:
                    for this_file in folder_contents:
                        names.append(os.path.join(os.sep.join(folder_name.split(os.sep)[1:]), this_file["filename"]))

    @staticmethod
    def _check_remote_changes(payload: JSONData) -> Optional[str]:
        msg = None
        if len(payload["remote_modified"]) + len(payload["local_and_remote_modified"]) > 0:
            file_names = list()
            DKCloudCommandRunner._get_file_names(payload, "remote_modified", file_names)
            DKCloudCommandRunner._get_file_names(payload, "local_and_remote_modified", file_names)
            msg = f"ERROR: {len(file_names)} files have remote changes. Please run 'dk recipe-get' first.\n"
            msg += "\n".join(["\t" + f for f in file_names])
        return msg
