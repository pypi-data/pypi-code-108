import glob
import json
import pathlib
from typing import Optional

from .models import Plan


def _validate_test_plan_folder(folder_name: str) -> Optional[dict[str, str]]:
    """Validate the structure of the test plan folder.
    Returns a dictionary containing {"lrn": str, "plan-name": str}
    of the test plan OR None on error
    """
    plan_info = {"lrn": "", "plan-name": ""}

    # Find the manifest file in the test plan folder
    matches = glob.glob(folder_name + "/*/manifest.json")
    if (not matches) or (len(matches) > 1):
        return None

    try:
        with open(matches[0], "r") as manifest_file:
            manifest = json.load(manifest_file)
            plan_info["lrn"] = manifest["lrn"]
            plan_info["plan-name"] = manifest["name"]
    except FileNotFoundError as e:
        return None
    except Exception as exc:
        return None

    return plan_info


def get_plan(testplan_folder: str, workspace_id: str) -> Plan:
    """Construct & return a Plan object from the given testplan folder.
    The testplan folder path must be resolvable inside Docker,
    if running in Docker.
    Returns an empty Plan on error, where the lrn is a NULL string.
    """
    plan_info = _validate_test_plan_folder(folder_name=testplan_folder)
    if (not plan_info) or (plan_info["plan-name"] == ""):
        return Plan("", pathlib.Path(""), "")

    _catalog = pathlib.Path(testplan_folder)
    return Plan(
        lrn=plan_info["lrn"],
        name=plan_info["plan-name"],
        catalog=_catalog,
        workspace_id=workspace_id,
    )
