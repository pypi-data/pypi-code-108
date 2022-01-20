# -*- coding: utf-8 -*-

from Acquisition import aq_base
from copy import deepcopy
from cpskin.core.transmo.wrapper import Wrapper
from plone import api
from Products.Five.browser import BrowserView

import base64
import json
import pprint
import sys
import traceback


def _clean_dict(dct, error):
    new_dict = dct.copy()
    message = str(error)
    for key, value in dct.items():
        if message.startswith(repr(value)):
            del new_dict[key]
            return key, new_dict
    raise ValueError('Could not clean up object')


class GetItem(BrowserView):

    def __call__(self):
        """
        """

        try:
            context_dict = Wrapper(self.context)

        except Exception, e:
            tb = pprint.pformat(traceback.format_tb(sys.exc_info()[2]))
            return 'ERROR: exception wrapping object: {0}\n{1}'.format(
                str(e), tb)

        passed = False
        while not passed:
            try:
                JSON = json.dumps(context_dict)
                passed = True
            except Exception, error:
                if 'serializable' in str(error):
                    key, context_dict = _clean_dict(context_dict, error)
                    pprint.pprint('Not serializable member {0} of {1} ignored'.format(key, repr(self)))  # noqa
                    passed = False
                else:
                    return ('ERROR: Unknown error serializing object: {0}'.format(str(error)))  # noqa
        self.request.response.setHeader('Content-Type', 'application/json')
        return JSON


class GetChildren(BrowserView):

    def __call__(self):
        """
        """

        children = []
        if getattr(aq_base(self.context), 'objectIds', False):
            children = self.context.objectIds()
            # Btree based folders return an OOBTreeItems
            # object which is not serializable
            # Thus we need to convert it to a list
            if not isinstance(children, list):
                children = [item for item in children]

        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(children)


class GetCatalogResults(BrowserView):

    def __call__(self):
        """Returns a list of paths of all items found by the catalog.
           Query parameters can be passed in the request.
        """
        if not hasattr(self.context.aq_base, 'unrestrictedSearchResults'):
            return
        query = self.request.form.get('catalog_query', None)
        if query:
            query = eval(base64.b64decode(query),
                         {'__builtins__': None}, {})
        item_paths = [item.getPath() for item
                      in self.context.unrestrictedSearchResults(**query)]
        # sometimes some content are unindexed
        plone_path = '/'.join(api.portal.get().getPhysicalPath())
        item_paths_with_parents = add_parent(item_paths, plone_path)
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(item_paths_with_parents)


def add_parent(item_paths, plone_path):
    old_paths = deepcopy(item_paths)
    paths = []
    for item_path in item_paths:
        parent_path = '/'.join(item_path.split('/')[:-1])
        if parent_path not in old_paths and parent_path not in paths \
                and parent_path is not plone_path:
            paths.append(parent_path)
        paths.append(item_path)
    return paths
