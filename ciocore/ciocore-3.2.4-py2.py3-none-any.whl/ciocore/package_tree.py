"""This module represents the list of software packages as a tree.

It has methods and functions to traverse the tree to find
packages and build paths etc.

See tests in /tests/test_package_tree.py for additional usage info.
"""


import copy
import json

from ciocore.package_environment import PackageEnvironment


def remove_unreachable(paths):
    """Remove unreachable paths.

    Given some paths, remove those for which there are not additional paths present at each level up
    the hierarchy to the host. It is possible to have orphaned paths if a package can be reached by
    more than one path. For example, a shader library may be compatible with 2 versions of a
    renderer, but only one of those renderers is compatible with this host. We need to remove the
    entry that references a different host.
    """
    results = []
    previous = ""
    for path in sorted(paths):
        parts = path.split("/")
        valid_subpath = path == "%s/%s" % (previous, parts[-1])
        if len(parts) == 1 or valid_subpath:
            results.append(path)
            previous = path
    return results


def to_name(pkg):
    """Name like `houdini 16.5.323` or `maya 2016.SP3`.

    This name is derived from the product and version fields in a package. Note: It is not
    necessarily possible to go the other way and extract version fields from the name. It's purpose
    is to enable path construction to uniquely identify a package. For example, houdini
    16.0.736/arnold-houdini 2.0.2.2/al-shaders 1.0
    """
    version_parts = [
        pkg["major_version"],
        pkg["minor_version"],
        pkg["release_version"],
        pkg["build_version"],
    ]
    version_string = (".").join([p for p in version_parts if p])
    return "{} {}".format(pkg["product"], version_string)


def _build_tree(packages, package):
    """Build a tree of dependent software plugins.

    Add a children key, and For each ID in the `plugins` key, add the package it refers to to
    children. Recurse until no more plugins are left.
    """

    for child_id in package.get("plugins", []):
        child_package = next((c for c in packages if c["package_id"] == child_id), None)
        if child_package:
            child_package = _build_tree(packages, child_package)
            package["children"].append(child_package)
    package.pop("plugins", None)
    return package


def _is_product(pkg, **kwargs):
    """Is this pkg the product described in kwargs.

    Works in one of 2 ways. Match against either 1. display name, or 2. the raw keys (product,
    major_version, minor_version, release_version, build_version). The root node has no `product`
    key because it is a collection of host packages.
    """
    if not pkg.get("product"):
        return False

    name = kwargs.get("name")
    if name:
        if name == to_name(pkg):
            return True
        return False


    for key in kwargs:
        value = kwargs[key]
        pkg_value = pkg[key]
        if value and value != pkg_value:
            return False
    return True

def _find_by_keys(tree, **kw):
    """Given product and version keys find the package."""
    if not tree:
        return None
    if _is_product(tree, **kw):
        return tree
    for child_tree in tree["children"]:
        result = _find_by_keys(child_tree, **kw)
        if result:
            return result
    return None


def _find_by_name(branch, name, limit=None, depth=0):
    """Given a name made by `to_name` find the package.

    Name is typically part of a path. Limit will limit the search depth and is useful when you know
    the package should be a direct child and not any descndent.
    """
    if not branch:
        return None
    if _is_product(branch, name=name):
        return branch
    depth += 1

    if (not limit) or depth <= limit:
        for child_branch in branch["children"]:
            result = _find_by_name(child_branch, name, limit, depth)
            if result:
                return result
    return None


def _find_by_path(tree, path):
    """Find the package uniquely described by this path.

    This method loops through parts of the path name and searches the tree for each part.  When it
    finds a matching package, we use that package as the root of the tree for the next search. As we
    are searching for an exact path match, we limit the search to one level deep each time.
    """

    if not path:
        return None
        
    result = None
    for name in [p for p in path.split("/") if p]:
        tree = _find_by_name(tree, name, 1)
        result = tree
    return result


def _to_path_list(tree, **kw):
    """Get paths to all nodes.

    This means starting at the level of the given tree, get all the paths to intermediate and leaf
    nodes. This is useful for populating a chooser to choose packages fully qualified by path.

    * 'houdini 16.0.736'
    * 'houdini 16.0.736/arnold-houdini 2.0.1'
    * 'houdini 16.0.736/arnold-houdini 2.0.1/al-shaders 1.0'
    """
    parent_name = kw.get("parent_name", "")
    paths = kw.get("paths", [])

    for child_tree in tree["children"]:
        name = ("/").join([n for n in [parent_name, to_name(child_tree)] if n])
        paths.append(name)
        paths = _to_path_list(child_tree, paths=paths, parent_name=name)
    return paths


def to_all_paths(path):
    """Extract all ancestor paths from a path.

    This can be useful if the user selects a plugin from a chooser, because we know we'll want its
    host ancestors. Just split the string and work up the parts.
    """
    result = []
    parts = path.split("/")
    while parts:
        result.append(("/").join(parts))
        parts.pop()
    result.reverse()
    return result


def _clean_package(package):
    """Remove some unwanted keys.

    TODO - Some of these may turn out to be wanted after all.
    """
    pkg = copy.deepcopy(package)
    for att in [
        "build_id",
        "time_updated",
        "description",
        "updated_at",
        "time_created",
        "plugin_hosts",
        "relative_path",
    ]:
        pkg.pop(att, None)

    pkg["children"] = []
    return pkg


class PackageTree(object):
    """Class to represent available packages as a tree.

    Data structure is really a DAG because a tool may be compatible with more than one host product.
    """

    def __init__(self, packages, **kw):
        """Initialize based on a product.

        If product kw given then build the tree containing packages below versions of that product
        only. e.g. "houdini" or "maya-io"
        """
        product = kw.get("product")

        packages = [_clean_package(p) for p in packages]

        if product:
            root_ids = [p["package_id"] for p in packages if p["product"] == product]
        else:
            root_ids = [p["package_id"] for p in packages if not p["plugin_host_product"]]

        self.tree = _build_tree(packages, {"children": [], "plugins": root_ids})

    def find_by_name(self, name, limit=None, depth=0):
        """Search the tree for a product with the given name.

        This name is the name originally constructed from the package using to_name.
        """
        return _find_by_name(self.tree, name, limit, depth)

    def find_by_keys(self, **kw):
        """Search the tree for a product with the given keys.

        Whichever keys from the following are given, must match, product, major_version,
        minor_version, release_version, build_version
        """
        return _find_by_keys(self.tree, **kw)

    def find_by_path(self, path):
        """Find the package uniquely described by this path."""
        return _find_by_path(self.tree, path)

    def to_path_list(self, **kw):
        """Get paths to all nodes.

        Example:

            'maya-io 2018.SP2',
            'maya-io 2018.SP2/yeti 3.8',
            'maya-io 2018.SP2/yeti 3.1.15',
            'maya-io 2018.SP4',
            'maya-io 2018.SP4/yeti 2.2.2',
            'maya-io 2018.SP4/arnold-maya 2.0.2.3',
            'maya-io 2018.SP4/v-ray-maya 3.60.01.0',

        If the name keyword is given, get paths below the tree represented by that name.

        Example: to_path_list(name='maya-io 2018.SP4') 'yeti 2.2.2', 'arnold-maya 2.0.2.3',
        'v-ray-maya 3.60.01.0',

        A TypeError will be thrown if the name is invalid.
        """
        name = kw.get("name")
        if name:
            subtree = self.find_by_name(name)
            return _to_path_list(subtree)
        return _to_path_list(self.tree)

    def get_all_paths_to(self, **kw):
        """All paths to the package described in kw.

        Its possible there is more than one path to a given node. For now we just get all paths
        through the tree and then select the ones whose leaf matches.
        """
        all_paths = _to_path_list(self.tree)
        name = to_name(kw)
        return [p for p in all_paths if p.endswith(name)]

    def get_environment(self, paths):
        """Get merged environment from paths."""
        package_env = PackageEnvironment()
        for path in paths:
            package = _find_by_path(self.tree, path)
            if package:
                package_env.extend(package)
        return package_env

    def json(self):
        """The whole tree as json."""
        return json.dumps(self.tree)

    # TODO write tests for this
    def supported_host_names(self):
        """Pluck host paths from the available software tree.

        Dont get children"""
        pathlist = _to_path_list(self.tree)
        return sorted([p for p in pathlist if "/" not in p])

    def supported_plugins(self, host):
        """Make sorted list of plugins.

        Each entry is an object with a 'plugin' and a 'versions' key.

        Example:
        plugins = [
            {"plugin": "arnold", "versions": ["1","2","3"]},
            {"plugin": "vray", "versions": ["1","2","3"]},
        ]
        """

        try:
            subtree = self.find_by_name(host)
            plugin_versions = _to_path_list(subtree)
        except TypeError:
            return

        if not plugin_versions:
            return

        plugin_dict = {}
        for plugin, version in [pv.split(" ") for pv in plugin_versions]:
            if plugin not in plugin_dict:
                plugin_dict[plugin] = []
            plugin_dict[plugin].append(version)

        # convert to list so it can be sorted
        plugins = []
        for key in plugin_dict:
            plugins.append({"plugin": key, "versions": sorted(plugin_dict[key])})

        return sorted(plugins, key=lambda k: k["plugin"])
