# -*- coding: utf-8 -*-
# Copyright 2016 Cisco Systems, Inc
from __future__ import unicode_literals

import json
from datetime import datetime

import networkx

from yangsuite import get_logger
from .yangset import YSYangSet
from .repository import YSYangRepository
from .utility import yangset_path


log = get_logger(__name__)


class YSMutableYangSet(YSYangSet):
    """Class used for building and editing YSYangSets."""

    def __init__(self, *args, **kwargs):
        self._repository = None
        self._pruned_digraph = None
        super(YSMutableYangSet, self).__init__(*args, **kwargs)

    def write(self):
        """Save this yangset for later reuse via YSYangSet.load()."""
        data = {
            'setname': self.setname,
            'owner': self.owner,
            'repository': self.repository.slug,
            # Just write (name, rev) rather than (name, rev, abspath)
            # as we can trivially reconstruct abspath from the repo
            'modules': [
                (m[0], m[1]) for m in self.modules
            ],
        }
        path = yangset_path(self.owner, self.setname)
        with open(path, 'w') as fd:
            json.dump(data, fd, indent=2)
        # We're up to date!
        self.mtime = self.datastore_mtime
        log.info("Saved YANG set %s to %s", self, path)

    @property
    def modules(self):
        """Sorted list of (mod, rev, path) that this YSMutableYangSet has."""
        return self._modules

    @modules.setter
    def modules(self, values):
        """Unlike YSYangSet, this allows change."""
        self.mtime = None
        self._modules = None
        self._digraph = None
        super(YSMutableYangSet, self.__class__).modules.fset(self, values)

    @property
    def repository(self):
        return self._repository

    @repository.setter
    def repository(self, value):
        if isinstance(value, str):
            self._repository = YSYangRepository(value)
        elif isinstance(value, YSYangRepository):
            self._repository = value
        else:
            raise TypeError(
                "expected string or YSYangRepository instance, but got {0}"
                .format(value))
        if (hasattr(self, 'reponame') and
                self.repository.reponame != self.reponame):
            self.mtime = datetime.utcnow()
        self.reponame = self.repository.reponame

    @property
    def digraph(self):
        """Rough approximation of inter-module dependencies within this set.

        Unlike the base class :attr:`~._YSYangSetBase.digraph`, this includes
        additional modules within the repository that are not actually part
        of the set definition itself. These extra nodes are used for the
        :meth:`~._YSYangSetBase.extra_dependencies` / :meth:`upstream_modules`
        / :meth:`augmenter_modules` / :meth:`identity_deriving_modules`
        / :meth:`related_modules` APIs.

        Returns:
          :class:`networkx.DiGraph`
        """
        if self._digraph is None:
            self._digraph = self._get_module_graph(
                self.modules + self.repository.modules)
        return self._digraph

    # Please keep these in alphabetical order
    MODS_PARENTS_UNRELATED = [
        'ietf-inet-types',
        'ietf-interfaces',
        'ietf-yang-types',
        'openconfig-extensions',
        'openconfig-interfaces',
        'openconfig-types',
        'Cisco-IOS-XE-native',
        'Cisco-IOS-XE-types',
        'Cisco-IOS-XR-types',
    ]
    """Modules that are very widely imported and so do not indicate relation.

    In other words, two modules should NOT be considered 'related' simply
    because they both import one of these modules - otherwise, say, any module
    that imports 'ietf-inet-types' might report over 1000 "related" modules,
    which is not particularly useful.
    """

    @property
    def pruned_digraph(self):
        """Digraph excluding certain nodes/paths that are not of interest.

        Specifically, this prunes out the modules defined in
        :const:`MODS_PARENTS_UNRELATED`.
        """
        if self._pruned_digraph is None:
            pruned = self.digraph.copy()
            pruned.remove_nodes_from(self.MODS_PARENTS_UNRELATED)
            self._pruned_digraph = pruned
        return self._pruned_digraph

    def upstream_modules(self):
        """Get modules that are not part of this YANG set but make use of it.

        These are optional "upstream consumers" - modules that import
        modules contained in our YANG set. Adding these to the
        YANG set could possibly result in a more complete picture.

        .. note::

          This API makes use of the :attr:`pruned_digraph` rather than the
          :attr:`~._YSYangSetBase.digraph`, meaning that if this set includes
          any of the modules listed in :const:`MODS_PARENTS_UNRELATED`,
          other modules in the repository that import only said module(s)
          will *not* be included in the returned list.

        .. seealso::

          :meth:`~._YSYangSetBase.modules_using`: for getting the modules
          upstream of a single module, rather than the entire set. That API
          also does not prune the digraph or the list of modules returned,
          unlike this method.

        Returns:
          list: of (module, revision, path). This list may intersect with the
          lists returned by :meth:`augmenter_modules` and/or
          :meth:`identity_deriving_modules`.
        """
        results = set()
        g = self.pruned_digraph
        for name, rev, _ in self.modules:
            if name not in g:
                # Pruned out
                continue
            # If it's in self.modules, it must be marked as such
            assert g.node[name]['in_yangset']

            if not g.node[name]['found']:
                log.error("Module %s@%s not found", name, rev)
                continue

            # log.debug("Checking for modules depending on %s@%s", name, rev)
            for anc in networkx.ancestors(g, name):
                # log.debug("  Checking ancestor %s", anc)
                entry = (anc, g.node[anc]['revision'], g.node[anc]['path'])
                if not g.node[anc]['in_yangset'] and entry not in results:
                    log.debug("Adding upstream module %s (%s)", anc,
                              " → ".join(networkx.shortest_path(g, anc, name)))
                    results.add(entry)

        return sorted(results)

    def augmenter_modules(self):
        """Get modules that aren't in this set but augment modules that are.

        Returns:
          list: of (name, revision, path) .This list may intersect with the
          lists returned by :meth:`upstream_modules` and/or
          :meth:`identity_deriving_modules`.
        """
        results = set(self.repository.modules) - set(self.modules)
        return sorted(
            entry for entry in results if
            # Repository may have multiple revisions of the same mod
            # whereas digraph has one node per mod
            entry[0] in self.digraph.node and
            not self.digraph.node[entry[0]]['in_yangset'] and
            any(self.digraph.node[mod]['in_yangset']
                for mod in self.digraph.node[entry[0]]['augments']))

    def identity_deriving_modules(self):
        """Get modules that aren't in this set but provide derived identities.

        Returns:
          list: of (name, revision, path) .This list may intersect with the
          lists returned by :meth:`upstream_modules` and/or
          :meth:`augmenter_modules`.
        """
        results = set(self.repository.modules) - set(self.modules)
        return sorted(
            entry for entry in results if
            # Repository may have multiple revisions of the same mod
            # whereas digraph has one node per mod
            entry[0] in self.digraph.node and
            not self.digraph.node[entry[0]]['in_yangset'] and
            any(self.digraph.node[mod]['in_yangset'] for mod in
                self.digraph.node[entry[0]]['derives-identities-from']))

    def related_modules(self):
        """Get modules that aren't part of this YANG set but might be relevant.

        Think of this function as providing a "People who use this yangset
        might also be interested in..." set of suggestions.

        The set of modules returned by this API is non-intersecting with those
        reported by :meth:`~._YSYangSetBase.extra_dependencies` and
        :meth:`upstream_modules`, which represent known dependencies and known
        consumers of the modules in this YANG set, respectively.

        As currently implemented, this is 'degrees of separation' based, as
        shown below (``(*)`` represents modules too distant to be considered
        as related_modules)::

                        ┌───────────────────────┐
                        │ upstream_grandparent <─imports<─ (*)
          upstream_mods ┤   ^ imports ^         │
                        │ upstream_parent  <──imports<──┐  related_modules
                        └   ^ imports ^    ─────┘    ┌──│─────────┴───────┐
                      ┌─  module_in_yangset      ─┐  │ upstream_relative <─>(*)
          yangset ────┤     ^ imports ^           │  │                    │
                      └─  another_mod_in_yangset ─┘  │ dep_relative <──────>(*)
                        ┌   ^ imports ^    ────┐     └───^────────────────┘
                        │ extra_dep_child ──>imported─by─┘
          extra_depends ┤   ^ imports ^        │
                        │ extra_dep_grandchild ─>imported─by─> (*)
                        └──────────────────────┘

        .. note::

          This API makes use of the :attr:`pruned_digraph` rather than the
          :attr:`~._YSYangSetBase.digraph`, meaning that if this set includes
          any of the modules listed in :const:`MODS_PARENTS_UNRELATED`,
          other modules in the repository that import or are imported by
          said module(s) alone will *not* be included in the returned list.

        Returns:
          list: of tuples (`modulename`, `revision`, `path`)
        """
        # For now this is hard-coded; maybe let them be user-specified?
        MAX_DEGREES = 1

        upstream = self.upstream_modules()

        results = set()
        g = self.pruned_digraph
        for node_name in g.nodes_iter():
            if not g.node[node_name]['found']:
                continue
            entry = (node_name, g.node[node_name]['revision'],
                     g.node[node_name]['path'])
            if entry not in self.modules:
                continue

            for ancestor in self._ancestors(g, node_name, MAX_DEGREES):
                if not g.node[ancestor]['found']:
                    continue
                for desc in self._descendants(g, ancestor, MAX_DEGREES):
                    if not g.node[desc]['found']:
                        continue
                    entry = (desc, g.node[desc]['revision'],
                             g.node[desc]['path'])
                    if entry not in self.modules and entry not in upstream:
                        results.add(entry)

            for desc in self._descendants(g, node_name, MAX_DEGREES):
                if not g.node[desc]['found']:
                    continue
                for anc in self._ancestors(g, desc, MAX_DEGREES):
                    if not g.node[anc]['found']:
                        continue
                    entry = (anc, g.node[anc]['revision'],
                             g.node[anc]['path'])
                    if entry not in self.modules and entry not in upstream:
                        results.add(entry)

        return sorted(results)

    @staticmethod
    def _ancestors(g, node_name, max_distance):
        """Helper function for related_modules().

        Since :meth:`networkx.ancestors` doesn't filter by max distance,
        we have to roll our own.

        Args:
          g (networkx.DiGraph): graph
          node_name (str): node whose ancestors we want
          max_distance (int): maximum number of edges to traverse

        Returns:
          list(str): of node names representing the requested ancestors
        """
        return [k for k, v in
                networkx.shortest_path_length(g, target=node_name).items()
                if v <= max_distance and k != node_name]

    @staticmethod
    def _descendants(g, node_name, max_distance):
        """Helper function for related_modules().

        Since :meth:`networkx.descendants` doesn't filter by max distance,
        we have to roll our own.

        Args:
          g (networkx.DiGraph): graph
          node_name (str): node whose descendants we want
          max_distance (int): maximum number of edges to traverse

        Returns:
          list(str): of node names representing the requested descendants
        """
        return [k for k, v in
                networkx.shortest_path_length(g, source=node_name).items()
                if v <= max_distance and k != node_name]
