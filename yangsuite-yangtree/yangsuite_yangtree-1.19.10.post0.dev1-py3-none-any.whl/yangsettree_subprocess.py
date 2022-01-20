import pickle
from ysyangtree.ymodels import ALL_NODETYPES, YSYangModels
from ysyangtree.context import YSContext
from ysfilemanager import YSYangSet, merge_user_set
from yangsuite.paths import set_base_path
import sys
import argparse
import json
import logging
import base64
import os


def _get_module_tree_data(ctx, models, ys, modules, node_callback):
    """Populate set_modules, data, and yangsettree_mtime for YANG set tree
        required to store in database.
    Args:
        ctx (YSContext): User context
        models (dict) : Jstree data of yangset
        ys (YSYangSet): Yangset details
        modules (list): A list of modules
        node_callback (function): Function to call for each node in the tree
            in order to populate additional data into the tree. Must accept
            kwargs ``stmt``, ``node``, and ``parent_data``
            (which may be ``None``), and return ``node``.

    Returns:
        dict: Details for database fields: set_modules, data, and
              yangsettree_mtime
    """
    dg = ctx.repository.digraph
    tree_modules = models.jstree.get('data')
    process_status = {}
    type_module = []
    for num in range(len(tree_modules)):
        name = tree_modules[num]['text']
        if name in dg.node.keys():
            data_modules = tree_modules[num].get('data')
            imported = data_modules.get('imports')
            module_augments = dg.node[name]['augments']
            revision = dg.node[name]['revision']
            if (data_modules.get('submodule') is None):
                mod_type = 'module'
                module_name = ''
            else:
                mod_type = 'submodule'
                module_name = data_modules.get('module')
            type_module.append({
                'name': name,
                'revision': revision,
                'type': mod_type,
                'main_module': module_name,
                'imported': imported,
                'augments': module_augments
            })

    process_status["set_modules"] = json.dumps({'moduledet': type_module})

    gen_tree = {}
    if node_callback is not None:
        for mod, psy in models.yangs.items():
            gen_tree[mod] = psy.generate_tree(node_callback)
        process_status["data"] = json.dumps(gen_tree)
    else:
        process_status["data"] = json.dumps(models.jstree)

    process_status["yangsettree_mtime"] = str(ys.datastore_mtime)

    return process_status


def _sub_create_tree(user, setname, modules, repo,
                     ref='',
                     nodes=ALL_NODETYPES,
                     plugin_name='yangsuite-yangtree',
                     node_callback=None,
                     child_class=None):
    """Popluate data for a new YANG set tree.
    Args:
        user (str): Encoded and serialized User instance
        setname(str): Name of setname
        modules (list): A list of modules
        repo(str): User repository
        ref (str): Reference
        nodes (frozenset): Nodes included in tree
        plugin_name (str): Name of plugin
        node_callback (function): Function to call for each node in the tree
            in order to populate additional data into the tree. Must accept
            kwargs ``stmt``, ``node``, and ``parent_data``
            (which may be ``None``), and return ``node``.

    Returns:
        str: Details for database fields: set_modules, data, repo and
             yangsettree_mtime for successfully created yangset or error
             details when any error occurred during validations.
    """
    process_status = {}
    try:
        user = base64.b64decode(args.user)
        user = pickle.loads(user)
    except (OSError, ValueError) as e:
        process_status["status"] = 404
        process_status["reason"] = "No such yangset"
        return process_status
    if node_callback:
        node_callback = base64.b64decode(args.node_callback)
        node_callback = pickle.loads(node_callback)
    else:
        node_callback = None

    if child_class:
        child_class = base64.b64decode(args.child_class)
        child_class = pickle.loads(child_class)
    else:
        child_class = None

    try:
        ys = YSYangSet.load(user.username, setname)
    except (OSError, ValueError):
        process_status["status"] = 404
        process_status["reason"] = "No such yangset"
        return process_status
    except RuntimeError:
        process_status["status"] = 404
        process_status["reason"] = "No such yangset owner"
        return process_status

    yangset = merge_user_set(user.username, setname)

    models = YSYangModels.get_instance(ref)
    if ((not models) or
            models.modelnames != sorted(modules) or
            models.ctx.repository != ys or
            models.ctx.repository.is_stale):
        # Not a valid cache entry - need a new one
        try:
            ctx = YSContext.get_instance(ref, yangset)
        except RuntimeError:
            process_status["status"] = 404
            process_status["reason"] = "No such user"
            return process_status
        except KeyError:
            process_status["status"] = 404
            process_status["reason"] = "Bad cache reference"
            return process_status
        if ctx is None:
            process_status["status"] = 404
            process_status["reason"] = "User context '{0}' not found".format(
                                        ref)
            return process_status

        models = YSYangModels(ctx, modules,
                              included_nodetypes=nodes,
                              child_class=child_class)

        process_status = _get_module_tree_data(ctx, models,
                                               ys, modules,
                                               node_callback)

        process_status["repo"] = ctx.repository.reponame

        return process_status
    else:
        if node_callback is None:
            models.included_nodetypes = nodes


if __name__ == '__main__':
    logging.disable(logging.WARNING)
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--user', type=os.fsencode)
        parser.add_argument('--setname', type=str)
        parser.add_argument('--modules', nargs='*')
        parser.add_argument('--ref', type=str)
        parser.add_argument('--repo', type=str)
        parser.add_argument('--nodes', nargs='+')
        parser.add_argument('--plugin_name', type=str,
                            default='yangsuite-yangtree')
        parser.add_argument('--node_callback', type=os.fsencode)
        parser.add_argument('--child_class', type=os.fsencode)
        parser.add_argument('--basepath', type=str)
        args = parser.parse_args()
        import django
        django.setup()
        if args.basepath:
            set_base_path(args.basepath)

        process_status = _sub_create_tree(
                                          args.user, args.setname,
                                          args.modules, args.repo,
                                          args.ref, args.nodes,
                                          args.plugin_name,
                                          args.node_callback,
                                          args.child_class)

        print(json.dumps(process_status))
    except RuntimeError as e:
        print('Error: :404:', str(e), file=sys.stderr)
        print(str(e.output))
        exit(1)
