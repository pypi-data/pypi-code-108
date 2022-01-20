# Copyright 2016-2021 Cisco Systems, Inc
import json
from django.http import JsonResponse
from ysyangtree.models import YangSetTree
from ysyangtree.ymodels import ALL_NODETYPES
from django.contrib.auth.models import User
from yangsuite.paths import get_base_path
from django.utils import timezone
from slugify import slugify
import os
import subprocess
import pickle
import base64
import sys


def get_yangset_tree(owner, setname, modules,
                     ref='', plugin_name='yangsuite-yangtree'):
    """Fetch yangset data from database.
    Args:
        owner (str): User name
        setname (str): Name of YANGSet
        modules (list): A list of modules to be included
                            in the Yang Set Tree
        ref (str): Reference
        plugin_name (str): Name of plugin

    Returns:
        YangSetTree: YangSetTree for yangset from the database.
    """
    try:
        user = User.objects.get(username=owner)
    except:
        return JsonResponse({}, status=404, reason="No such user")

    if not ref:
        ref = owner

    if setname:
        ysettree = YangSetTree.objects.filter(setname__iexact=slugify(setname),
                                              user=user,
                                              ref=ref,
                                              plugin_name=plugin_name)

    else:
        ysettree = YangSetTree.objects.filter(user=user,
                                              ref=ref,
                                              plugin_name=plugin_name)
    if ysettree:
        if modules:
            modules_name = []
            for tree in ysettree:
                old_modules = json.loads(tree.set_modules).get('moduledet')

                for num in range(len(old_modules)):
                    modules_name.append(old_modules[num].get('name'))

                if all(item in modules_name for item in modules):
                    return tree
        else:
            return ysettree[0]


def check_yangset_require_update(owner, setname, modules,
                                 ref='', plugin_name='yangsuite-yangtree'):
    """Check if a new YANG set tree needs to be created/updated.
    Args:
        owner (str): User name
        setname (str): Name of YANGSet
        modules (list): A list of modules to be included
                            in the Yang Set Tree
        ref (str): Reference
        plugin_name (str): Name of plugin

    Returns:
        Boolean or YangSetTree: True if a new Yang Tree needs to be
                                created/updated. YangSetTree tree if an entry
                                exist in the database.
    """
    create_set = False
    try:
        user = User.objects.get(username=owner)
    except:
        return JsonResponse({}, status=404, reason="No such user")

    if not ref:
        ref = owner

    ysettree = YangSetTree.objects.filter(setname__iexact=slugify(setname),
                                          user=user,
                                          ref=ref,
                                          plugin_name=plugin_name)

    if ysettree:
        # To check if all modules data exist in the stored tree. A new tree
        # needs to be created if modules are added or deleted to yangset.
        if modules:
            modules_name = []
            add_modules_name = [modules[x][0] for x in range(len(modules))]
            for tree in ysettree:
                old_modules = json.loads(tree.set_modules).get('moduledet')

                for num in range(len(old_modules)):
                    modules_name.append(old_modules[num].get('name'))

                if (all(item in modules_name for item in add_modules_name)
                   and (len(modules_name) == len(add_modules_name))):
                    for num in range(len(modules)):
                        module_name = modules[num][0]
                        revision = modules[num][1]
                        for add_num in range(len(old_modules)):
                            if ((module_name == old_modules[add_num]['name'])
                               and (revision !=
                               old_modules[add_num]['revision'])):
                                create_set = True
                                break
                    if not create_set:
                        return tree
                else:
                    create_set = True
        else:
            return ysettree
    else:
        create_set = True

    return create_set


def create_yangset_tree(owner, setname, modules, repo,
                        ref='',
                        nodes=ALL_NODETYPES,
                        plugin_name='yangsuite-yangtree',
                        node_callback=None,
                        child_class=None):
    """Create a new YANG set tree.
    Args:
        owner (str): User name
        setname(str): Name of setname
        modules (dict): A dictionary of modules
        repo(str): User repository
        ref (str): Reference
        nodes (frozenset): Nodes included in tree
        plugin_name (str): Name of plugin
        node_callback (function): Function to call for each node in the tree
            in order to populate additional data into the tree. Must accept
            kwargs ``stmt``, ``node``, and ``parent_data``
            (which may be ``None``), and return ``node``.

    Returns:
        YangSetTree: Created database tree
    """
    names = modules.get('module', [])
    try:
        user = User.objects.get(username=owner)
    except:
        return JsonResponse({}, status=404, reason="No such user")

    if not ref:
        ref = owner

    # Create a subprocess to create a yangset data to store in database
    get_yangsettree_proc = os.path.join(
                           os.path.dirname(os.path.abspath(__file__)),
                           'yangsettree_subprocess.py'
                           )

    sub_user = base64.b64encode(pickle.dumps(user))
    if child_class:
        sub_child_class = base64.b64encode(pickle.dumps(child_class))
    else:
        sub_child_class = ''
    if node_callback:
        sub_node_callback = base64.b64encode(pickle.dumps(node_callback))
    else:
        sub_node_callback = ''

    cmd = [
        sys.executable,
        get_yangsettree_proc,
        '--user', sub_user,
        '--setname', setname,
        '--ref', ref,
        '--repo', repo,
        '--basepath', get_base_path(),
        '--child_class', sub_child_class,
        '--node_callback', sub_node_callback,
        '--plugin_name', plugin_name,
        '--modules',
        ]
    cmd += names
    cmd += '--nodes',
    cmd += ALL_NODETYPES
    try:
        if sys.platform == "win32":
            cmd = [x.decode('utf-8') if type(x) != str else x for x in cmd]
            out = subprocess.run(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True)
        else:
            out = subprocess.run(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        if out.stdout:
            tree_json = json.loads(out.stdout.decode('utf-8'))

            tree_details_keys = ["set_modules", "data", "yangsettree_mtime",
                                 "repo"]
            if all(details in tree_json for details in tree_details_keys):
                set_modules = tree_json['set_modules']
                data = tree_json['data']
                yangsettree_mtime = tree_json['yangsettree_mtime']
                repo = tree_json['repo']
            else:
                return JsonResponse({}, status=tree_json['status'],
                                    reason=tree_json['reason'])
        else:
            return JsonResponse({}, status=404,
                                reason='Error occurred while creating tree')

    except subprocess.CalledProcessError as e:
        print(str(e.output.decode('utf-8')))
        print(str(e), file=sys.stderr)
        return JsonResponse({})

    try:
        if node_callback is not None:
            ysettree = check_yangset_require_update(owner, setname, names, ref,
                                                    plugin_name)
        else:
            ysettree = YangSetTree.objects.filter(setname__iexact=slugify(
                                                  setname),
                                                  user=user,
                                                  ref=ref,
                                                  plugin_name=plugin_name
                                                  ).first()
        if ysettree and ysettree is not True:
            # Delete the yangset database record
            ysettree.delete()
            del ysettree

        ysettree = YangSetTree(
            setname=slugify(setname),
            user=user,
            ref=ref,
            plugin_name=plugin_name,
            set_modules=set_modules,
            data=data,
            repository=repo,
            yangsettree_mtime=yangsettree_mtime,
            updated_on=timezone.now()
        )

        ysettree.save()
        del tree_json

        return ysettree
    except Exception as e:
        raise e


def delete_yangset_tree(owner, setname):
    """Delete a YANG set tree.
    Args:
        setname (str): Name of YANGSet
        owner (str): User name
    """
    try:
        user = User.objects.get(username=owner)
    except:
        return JsonResponse({}, status=404, reason="No such user")
    ysettree = YangSetTree.objects.filter(setname__iexact=slugify(setname),
                                          user=user,
                                          ref=owner)

    if ysettree:
        # Delete the tree and corresponding yang modules instance
        ysettree.delete()
        del ysettree
