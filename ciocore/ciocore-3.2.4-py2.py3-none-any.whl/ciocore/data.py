# Everything from the endpoints.


"""
Data from Conductor endpoints as a singleton.

Also has the ability to use fixtures for dev purposes.
"""
import json
import os
from ciocore.package_tree import PackageTree
from ciocore import api_client

__data__ = {}
__product__ = None
__fixtures_dir__ = None


def data(force=False, force_projects=False, force_software=False, force_instance_types=False):
    """
    Get projects , instance_types, and software from fixtures or api.

    Data will be valid.

    args: product, force_all, force_projects, force_software, force_instance_types
    """

    global __data__
    global __product__
    global __fixtures_dir__

    if not __product__:
        raise ValueError(
            'Data must be initialized before use, e.g. data.init("maya-io") or data.init("all").'
        )

    if force or force_projects:
        __data__["projects"] = None
    if force or force_instance_types:
        __data__["instance_types"] = None
    if force or force_software:
        __data__["software"] = None

    # PROJECTS
    if not __data__.get("projects"):
        projects_json = _get_json_fixture("projects")
        if projects_json:
            __data__["projects"] = projects_json
        else:
            __data__["projects"] = sorted(api_client.request_projects())

    # INST_TYPES
    if not __data__.get("instance_types"):
        instance_types = _get_json_fixture("instance_types")
        if instance_types:
            __data__["instance_types"] = instance_types
        else:
            instance_types = api_client.request_instance_types()
            __data__["instance_types"] = sorted(
                instance_types, key=lambda k: (k["cores"], k["memory"])
            )

    # SOFTWARE
    if not __data__.get("software"):
        software = _get_json_fixture("software")

        if not software:
            software = api_client.request_software_packages()

        if __product__ == "all":
            pt = PackageTree(software)
        else:
            pt = PackageTree(software, product=__product__)

        if pt.tree:
            __data__["software"] = pt

    return __data__


def valid():
    global __data__
    if not __data__.get("projects"):
        return False
    if not __data__.get("instance_types"):
        return False
    if not __data__.get("software"):
        return False
    return True


def clear():
    global __data__
    __data__ = {}


def init(product=None):
    global __product__
    if not product:
        raise ValueError("You must specify a product or 'all'")
    __product__ = product


def product():
    global __product__
    return __product__


def set_fixtures_dir(rhs):
    global __fixtures_dir__
    __fixtures_dir__ = rhs or ""


def _get_json_fixture(resource):
    global __fixtures_dir__
    if __fixtures_dir__:
        cache_path = os.path.join(__fixtures_dir__, "{}.json".format(resource))
        if os.path.isfile(cache_path):
            try:
                with open(cache_path) as f:
                    return json.load(f)
            except BaseException:
                pass
