# Copyright 2016 Cisco Systems, Inc
import os
import warnings
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ysyangtree.context import YSContext
from ysyangtree.ymodels import DEFAULT_INCLUDED_NODETYPES, ALL_NODETYPES
from yangsuite.logs import get_logger
from ysfilemanager import split_user_set
from django.utils.html import escape
from ysyangtree.yangsettree import (create_yangset_tree,
                                    get_yangset_tree)
from ysyangtree.models import YangSetTree
import json

log = get_logger(__name__)
rfc_info_cache = {}


NODETYPE_TO_RFC_SECTION = {
    'anyxml': '7.10',
    'case': '7.9.2',
    'choice': '7.9',
    'container': '7.5',
    'grouping': '7.11',
    'identity': '7.16',
    'input': '7.13.2',
    'leaf': '7.6',
    'leaf-list': '7.7',
    'leafref': '9.9',
    'list': '7.8',
    'notification': '7.14',
    'output': '7.13.3',
    'rpc': '7.13',
    'typedef': '7.3',
}


@login_required
def get_rfc(request):
    """Get the Json object with RFC content of each nodetype.

    Parse the RFC content if not cached, else return cached information.
    """
    nodetype = request.POST.get('nodetype')

    if not nodetype:
        return JsonResponse({'content': 'module'})

    if nodetype not in rfc_info_cache and nodetype in NODETYPE_TO_RFC_SECTION:
        rfc_info_cache[nodetype] = rfc_section_text(
            NODETYPE_TO_RFC_SECTION[nodetype])

    if rfc_info_cache.get(nodetype, None):
        return JsonResponse({
            'content': rfc_info_cache[nodetype],
            'reference': ("https://tools.ietf.org/html/rfc6020#section-" +
                          NODETYPE_TO_RFC_SECTION[nodetype]),
        })
    else:
        log.info("No specific page range known for nodetype '%s'", nodetype)
        return JsonResponse({'content': 'No additional information known',
                             'reference': ''})


def rfc_section_text(start, end=None):
    """Function to retrieve the requested subsection of RFC 6020."""
    with open(os.path.join(os.path.dirname(__file__), 'rfc6020.txt')) as fd:
        content = fd.read().splitlines()
    if not end:
        subs = start.split(".")
        subs[-1] = str(int(subs[-1]) + 1)
        end = ".".join(subs)
    for i, line in enumerate(content):
        if line.startswith(start):
            content = content[i:]
            break
    else:
        # we finished the loop without finding a match
        log.error("Did not find start section '%s' in the RFC.", start)
        return ""

    for i, line in enumerate(content):
        if line.startswith(end):
            content = content[:i]
            break
    else:
        log.warning("Did not find end section '%s' in the RFC.", end)

    return escape("\n".join(content))


##########################################
# Django view functions below this point #
##########################################


def ctx_status(ref, yangset=None):
    """Report the status of the context associated with the given key."""
    ctx = YSContext.get_instance(ref, yangset)
    if ctx is None:
        return JsonResponse({}, status=404,
                            reason="No request in progress.")
    return JsonResponse({
        'value': ctx.load_status['count'],
        'max': ctx.load_status['total'],
        'info': ctx.load_status['info'],
    })


def create_display_node(tree_data, included_nodetypes):
    """Fetch child node tree data"""
    display_data = []
    display_dict = {}
    display_dict['id'] = tree_data.get('id')
    display_dict['text'] = tree_data.get('text')
    display_dict['icon'] = tree_data.get('icon')
    display_dict['data'] = tree_data.get('data')

    if 'children' in tree_data.keys():
        node = tree_data.get('children')
        for y in range(len(node)):
            node_type = node[y].get('data').get('nodetype')
            if node_type in included_nodetypes:
                display_data.append(create_display_node(node[y],
                                    included_nodetypes))
            display_dict['children'] = display_data

    return display_dict


@login_required
def get_tree(request):
    """Retrieve context and build the JSTree based on module name.

    Args:
      request (django.http.HttpRequest): HTTP POST request

        - ref (str): reference for finding shared context (default: username)
        - name (str): module name to be parsed (DEPRECATED)
        - names (list): module name(s) to parse
        - yangset (str): YANG set name 'owner:setname' to use with context.
        - included_nodetypes (list): nodetypes to include in the tree.
          If unspecified, defaults to
          :const:`ymodels.DEFAULT_INCLUDED_NODETYPES`.
    Returns:
      django.http.JsonResponse: JSTree
    """
    if request.method == 'POST':
        names = request.POST.getlist('names[]')
        if not names:
            name = request.POST.get('name')
            if name:
                warnings.warn('Please provide a list "names[]" instead of '
                              'a single "name" parameter.', DeprecationWarning)
                names = [name]

        if not names:
            return JsonResponse({}, status=400,
                                reason="No model name(s) specified")

        yangset = request.POST.get('yangset')

        try:
            owner, setname = split_user_set(yangset)
        except ValueError:
            return JsonResponse({}, status=400,
                                reason="Invalid yangset string")

        ref = request.POST.get('reference')
        if not ref:
            if request.user.username != owner:
                ref = owner
            else:
                ref = request.user.username

        repository = request.POST.get('repository')
        if not repository:
            repository = ''

        included_nodetypes = request.POST.getlist('included_nodetypes[]',
                                                  DEFAULT_INCLUDED_NODETYPES)

        if (len(included_nodetypes) == len(DEFAULT_INCLUDED_NODETYPES)):
            all_node = False
        else:
            all_node = True

        add_modules = {'module': names}

        ysettree = get_yangset_tree(owner, setname, names, ref)
        if ysettree and isinstance(ysettree, YangSetTree):
            ysettree = ysettree
        else:
            if ysettree:
                return ysettree
            else:
                ysettree = True

        if ysettree is True:
            ysettree = create_yangset_tree(owner, setname,
                                           add_modules, repository,
                                           ref,
                                           nodes=ALL_NODETYPES)
        modules_data = []

        if isinstance(ysettree, YangSetTree):
            modules_details = json.loads(ysettree.set_modules).get('moduledet')
            for name in names:
                for num in range(len(modules_details)):
                    if (modules_details[num].get('name') == name):
                        if modules_details[num].get('type') == 'submodule':
                            main_mod = modules_details[num].get('main_module')
                            if main_mod not in names:
                                names.append(main_mod)
                        else:
                            arg_mod = modules_details[num].get('augments')
                            if arg_mod:
                                for add in arg_mod:
                                    if add not in names:
                                        names.append(add)

            tree_data = json.loads(ysettree.data).get('data')

            for name in names:
                for num in range(len(tree_data)):
                    if (tree_data[num]['text'] == name):
                        if all_node:
                            modules_data.append(tree_data[num])
                        else:
                            child_dict = {}
                            child_dict = create_display_node(
                                          tree_data[num], included_nodetypes)

                            modules_data.append(child_dict)
        else:
            if ysettree:
                return ysettree

        return JsonResponse({'data': modules_data,
                             'included_nodetypes': sorted(included_nodetypes)})

    else:
        yangset = request.GET.get('yangset')
        ref = request.GET.get('reference')
        if not ref:
            ref = request.user.username
        return ctx_status(ref, yangset)


@login_required
def explore(request, yangset=None, modulenames=None):
    """Render the base yangtree explore page, with optional selections.

    Args:
      request (django.http.HttpRequest): HTTP GET request

        -  yangset (str): YANG set slug 'owner+setname' to auto-select.
        -  modulenames (str): module name(s) to auto-select from this yangset,
           as comma-separated list of the form "module-1,module-2,module-3"
    Returns:
      django.http.HttpResponse: page to display
    """
    return render(request, 'ysyangtree/yangtree.html', {
        'yangset': yangset or '',
        'modulenames': modulenames or '',
    })
