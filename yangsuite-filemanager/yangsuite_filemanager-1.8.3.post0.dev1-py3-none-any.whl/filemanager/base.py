# Copyright 2016 Cisco Systems, Inc
import io
import os.path
import traceback
from datetime import datetime

import networkx

try:
    # _YSYangSetBase will be a subclass of pyang.repository if available:
    from pyang import Repository

    ReadError = Repository.ReadError
except ImportError:
    # ...but if not, we can operate on our own just fine
    Repository = object

    class ReadError(Exception):
        pass

from yangsuite import get_logger
from ..quickparser import quick_parse


log = get_logger(__name__)


class _YSYangSetBase(Repository):
    """A Repository containing a specific subset of YANG modules.

    This is a private semi-abstract class - users should use one of the
    following concrete subclasses:

    - :class:`.YSYangRepository`
    - :class:`.YSYangSet`
    - :class:`.YSMutableYangSet`
    """

    #
    # APIs required for the pyang.Repository interface
    #

    def get_modules_and_revisions(self, ctx=None):
        """Get the list of modules and revisions contained in this set.

        Args:
          ctx (YSContext): unused, but included in order to match the
            :meth:`pyang.Repository.get_modules_and_revisions` API

        Returns:
          list: of tuples ``(modulename, revision, handle)``, where
          ``handle`` is used in the call to :func:`get_module_from_handle` to
          retrieve the module. In this implementation, ``handle`` is simply
          the absolute file path.
        """
        return self.modules

    def get_module_from_handle(self, handle, *args):
        """Get the raw module text from the repository.

        Args:
          handle (object): Key to locate the module (in this case, the
            absolute file path)
          *args: Ignored; for compatibility with pyang 1.7.6 and 1.7.7,
            which add an extra parameter to this API.

        Returns:
          tuple: ``(ref, format, text)``

          - ``ref`` is a string which is used to identify the source of
            the text for the user, used in error messages. In this
            implementation it is the absolute path.
          - ``format`` is always 'yang' at present
          - ``text`` is the raw text data

        Raises:
          ReadError: if the file cannot be read.
        """
        try:
            with io.open(handle, 'r', encoding='utf-8') as fd:
                text = fd.read()
        except (IOError, UnicodeDecodeError) as ex:
            log.debug(traceback.format_exc())
            raise ReadError("{0}: {1}".format(handle, ex))

        return (handle, 'yang', text)

    #
    # Additional public methods and properties
    #

    def __init__(self, owner, modules):
        """Create a YANG set instance.

        Args:
          owner (str): User owning this set definition
          modules (list): List of [module, revision, absfilepath] lists
            of interest.
        """
        super(_YSYangSetBase, self).__init__()    # no-op at present
        self.owner = owner
        self.mtime = self.datastore_mtime
        """Datetime when this instance's contents were last changed."""
        self._modules = None
        self.modules = modules
        self._digraph = None

    @property
    def datastore_mtime(self):
        """Datetime when the underlying data store was last modified.

        Will be None if there is no underlying data store.

        If this time exists and is newer than ``self.mtime``, that means that
        this instance has become stale (no longer in sync with the underlying
        datastore) and hence ``is_stale`` will be True.
        """
        return None

    @property
    def is_stale(self):
        """Has the underlying data been modified since we were inited?"""
        return ((self.mtime is None and self.datastore_mtime is not None) or
                self.datastore_mtime is not None and self.mtime is not None and
                self.datastore_mtime > self.mtime)

    @property
    def modules(self):
        """Sorted list of (mod, rev, path) that this YSYangSet contains."""
        return self._modules

    @modules.setter
    def modules(self, value):
        """In this class just take what we're given.

        Subclasses may override this method to provide sanitization and such.
        """
        self._modules = value
        if not self.mtime:
            self.mtime = datetime.utcnow()

    def module_path(self, modulename, revision=None):
        """Get the absolute path to the requested module.

        Returns:
          str: Absolute file path, or None if not found
        """
        found_name = False
        for name, rev, path in self.modules:
            if name == modulename:
                found_name = True
                if revision is None or rev == revision:
                    return path
        else:
            if found_name:
                log.warning("Found module %s but not revision %s in %s",
                            modulename, revision, self)
            else:
                log.warning("Module %s not found in %s", modulename, self)
            return None

    @property
    def digraph(self):
        """Rough approximation of inter-module dependencies within this set.

        As noted in :func:`quick_parse`, this is a naive approach
        focused on speed rather than accuracy; using a proper YANG parser
        like :mod:`pyang` would be more accurate but much slower and more
        costly in terms of memory consumption.

        For more accurate results use a true YANG parser like :mod:`pyang`.

        Returns:
          :class:`networkx.DiGraph`
        """
        if self._digraph is None:
            self._digraph = self._get_module_graph(self.modules)
        return self._digraph

    def validate(self):
        """Check that the modules included in this YANG set are complete.

        Similar to but much less thorough than
        :meth:`ysyangtree.YSContext.validate`.

        Returns:
          list: of dicts with keys 'name', 'revision',
          'in_yangset', 'found', 'usable', 'errors', 'warnings' --
          matching :meth:`ysyangtree.YSContext.validate`.
        """
        results = []
        g = self.digraph
        for name, rev, _ in sorted(self.modules + self.extra_dependencies()):
            result = {
                'name': name,
                'revision': rev,
                'found': False,
                'in_yangset': False,
                'usable': False,
                'errors': [],
                'warnings': [],
            }
            if name not in g.node:
                result['errors'].append("No information available")
                result['in_yangset'] = any(m[0] == name for m in self.modules)
                results.append(result)
                continue

            result.update({
                'found': g.node[name]['found'],
                'in_yangset': g.node[name]['in_yangset'],
                'usable': g.node[name]['usable'],
            })

            # Add errors/warnings for things that we already know
            if not result['found']:
                result['errors'].append(
                    "Not found in YANG set or user repository")
            elif not result['in_yangset']:
                # Unreachable in YSYangSet but possible in YSMutableYangSet
                result['warnings'].append(
                    "Found in user repository but must be added "
                    "to the YANG set.")
            elif not result['usable']:
                result['errors'].append("Error in parsing module")
            existing_prefixes = {}
            result['errors'] += self._check_unique_prefixes(
                existing_prefixes, g.node[name]['imports'])

            # Now, check for derived errors
            for desc in sorted(networkx.descendants(g, name)):
                result['errors'] += self._check_unique_prefixes(
                    existing_prefixes, g.node[desc]['imports'])
                if not g.node[desc]['in_yangset']:
                    result['usable'] = False
                    if g.node[desc]['found']:
                        # Not in YSYangSet but possible in YSMutableYangSet
                        result['warnings'].append(
                            "Missing dependency {0} - possibly add {0}@{1}"
                            " from the repository?"
                            .format(desc, g.node[desc]['revision']))
                    else:
                        result['errors'].append(
                            "Dependency {0}@{1} not found!"
                            .format(desc, g.node[desc]['revision']))

            results.append(result)

        return results

    def extra_dependencies(self):
        """Get modules that aren't in this YANG set but need to be.

        These are mandatory dependencies - the modules in
        this YANG set 'import' or 'include' these modules, and/or
        the submodules in this YANG set 'belongs-to' these modules,
        and so the set is incomplete without access to them.

        Returns:
          list: of ``(module, revision, path)`` (for modules found in the
          repository) or ``(module, "unknown", None)`` (for modules
          altogether missing).
        """
        results = set()
        g = self.digraph
        for name, rev, _ in self.modules:
            if name not in g:
                log.warning("Module %s@%s is not in the digraph", name, rev)
                continue

            # If it's in self.modules, it must be marked as such
            assert g.node[name]['in_yangset']

            if not g.node[name]['found']:
                log.error("Module %s@%s not found", name, rev)
                continue

            dependencies = networkx.descendants(g, name)
            if g.node[name]['kind'] == 'submodule':
                belongs_to = g.node[name].get('belongs-to')
                if belongs_to:
                    dependencies.add(belongs_to)

            if dependencies:
                log.debug("Checking %d dependencies of %s@%s",
                          len(dependencies), name, rev)
            for dep in dependencies:
                if not g.node[dep]['in_yangset']:
                    log.debug("Dependency %s is not in the yangset", dep)
                    results.add(
                        (dep, g.node[dep]['revision'], g.node[dep]['path']))

        if results:
            log.info("Missing dependencies for %s: %s", self, sorted(results))
        return sorted(results)

    def modules_using(self, module):
        """Get the set of known modules that import or include this module.

        Args:
          module (str): Module name of interest.
        Returns:
          set: of module names
        """
        if module not in self.digraph:
            # *Should* it be in the digraph?
            if any(m[0] == module for m in self.modules):
                log.error('Module "%s" in "%s".modules missing from digraph',
                          module, self)
            return set()
        return networkx.ancestors(self.digraph, module)

    def modules_augmenting(self, module):
        """Get the set of known modules that augment this module.

        This is a subset of the modules returned by :meth:`modules_using`,
        and may overlap with the set returned by
        :meth:`modules_deriving_identities_from`.

        Args:
          module (str): Module name of interest
        Returns:
          set: of module names
        """
        users = self.modules_using(module)
        return [mod for mod in users
                if module in self.digraph.node[mod]['augments']]

    def modules_deriving_identities_from(self, module):
        """Get the set of known modules that derive identities from the module.

        This is a subset of the modules returned by :meth:`modules_using`,
        and may overlap with the set returned by :meth:`modules_augmenting`.

        Args:
          module (str): Module name of interest
        Returns:
          set: of module names
        """
        users = self.modules_using(module)
        return [mod for mod in users
                if module in self.digraph.node[mod]['derives-identities-from']]

    #
    # Private and magic methods
    #

    def __eq__(self, other):
        """Equality test."""
        return (self.owner == other.owner and
                self.modules == other.modules)

    def __ne__(self, other):
        """In python 3, defining __eq__ implies __ne__, but not in python 2."""
        return not self == other

    def __repr__(self):
        """String representation"""
        return "YANG set owned by '{0}' ({1} modules)".format(
            self.owner, len(self.modules))

    # The below code is heavily based on symd; at present symd itself doesn't
    # meet our needs for several reasons:
    # 1) symd uses a global variable 'G' to store its network graph, which will
    #    of course not work in our multi-user environment
    # 2) symd automatically imports matplotlib, which is a pretty beefy package
    # 3) symd presumes output to console or file, rather than providing clean
    #    APIs for use as a library.
    # In any case, we're only actually using a very small subset of symd,
    # so we can just implement our own version of that functionality here.

    def _get_module_graph(self, potential_modules):
        """Build a NetworkX directed graph from the given files.

        Creates a list of yang modules from the specified yang files and stores
        them as nodes in a NetworkX directed graph. This function also stores
        node attributes (list of imports, tag, revision, ...) for each module
        in the NetworkX data structures.

        See also :func:`symd.get_yang_modules`.

        Returns:
          :class:`networkx.DiGraph`: constructed graph
        """
        graph = networkx.DiGraph()
        for n, r, yf in potential_modules:
            attr = {
                'kind': None,
                'revision': r,
                'found': os.path.isfile(yf),
                'in_yangset': (n, r, yf) in self.modules,
                'usable': False,
                'imports': {},
                'includes': [],
                'augments': [],
                'derives-identities-from': [],
                'path': yf,
            }
            try:
                data = quick_parse(yf)
            except (IOError, UnicodeDecodeError) as ioe:
                log.debug(traceback.format_exc())
                log.warning(ioe)
                if n not in graph.node:
                    graph.add_node(n, **attr)
                continue

            name = data['name']
            if n != name:
                log.warning("Mismatch between expected name (%s) and "
                            "name parsed from %s (%s)?", n, yf, name)

            if len(data['revisions']) > 0:
                rev = max(data['revisions'])
            else:
                log.error("No revision specified for module '%s', file '%s'",
                          name, yf)
                rev = None
            attr.update({
                'kind': data['kind'],
                'revision': rev,
                'found': True,
                'usable': attr['in_yangset'],
                'imports': data['imports'],
                'includes': data['includes'],
                'augments': data['augments'],
                'derives-identities-from': data['derives-identities-from'],
            })

            if data['kind'] == 'submodule':
                attr['belongs-to'] = data.get('belongs-to')

            # Since our 'import/include' statements do not have associated
            # revisions (just module names), our graph nodes are just module
            # names, not module@revision.
            #
            # If we have multiple revisions of a given module, the node's
            # imports are just the superset of all revisions' imports,
            # and likewise for augments.

            if name not in graph:
                graph.add_node(name, **attr)
                continue
            # Else, update existing node:
            en = graph.node[name]
            en_rev = en['revision']
            if en_rev and rev and rev > en_rev:
                log.debug("Replacing with newer revision for "
                          "module '%s' ('%s' -> '%s')",
                          name, en_rev, rev)
                en['revision'] = rev
                # Let's keep the path of the newer revision as well
                en['path'] = yf

            if data['kind'] != en['kind']:
                # Shouldn't happen, not sure what we should do?
                log.warning("Module type mismatch for %s - "
                            "'%s' has %s, '%s' has %s",
                            name, rev, data['kind'], en_rev, en['kind'])

            en['imports'].update(data['imports'])

            # Convert to set then back to list so we don't duplicate
            for key in [
                    'includes',
                    'augments',
                    'derives-identities-from',
            ]:
                en[key] = sorted(set(en[key]) | set(data[key]))

        # Graph is now built for all modules in this set.
        # Next, what about missing imports?
        # See also symd.get_unknown_modules()
        unknown_attr = {
            'kind': 'module',
            'revision': 'unknown',
            'found': False,
            'in_yangset': False,
            'usable': False,
            'imports': {},
            'includes': [],
            'augments': [],
            'derives-identities-from': [],
            'path': None,
        }
        for node_name in graph.nodes():
            node = graph.node[node_name]
            deps = sorted(node['imports'].keys()) + node['includes']
            if node['kind'] == 'submodule':
                belongs_to = node.get('belongs-to')
                if belongs_to:
                    deps.append(belongs_to)
            for dep in deps:
                if dep not in graph.node:
                    log.debug("Module '%s': depends on module '%s' that "
                              "was not scanned", node_name, dep)
                    graph.add_node(dep, **unknown_attr)
                    if dep in node['includes']:
                        graph.node[dep]['kind'] = 'submodule'
                        graph.node[dep]['belongs-to'] = None

        # OK, now with found and missing modules, we should be able to
        # construct the graph edges for a complete graph.
        # See also symd.get_module_dependencies()
        for node_name in graph.nodes_iter():
            for dep in graph.node[node_name]['imports'].keys():
                if dep in graph.node:
                    graph.add_edge(node_name, dep)
                else:
                    # Shouldn't happen?
                    log.error("Module '%s': imports unexpected module '%s'",
                              node_name, dep)
            for dep in graph.node[node_name]['includes']:
                if dep in graph.node:
                    graph.add_edge(node_name, dep)
                else:
                    # Shouldn't happen?
                    log.error("Module '%s': includes unexpected module '%s'",
                              node_name, dep)

        # Sanity check
        for n, r, yf in potential_modules:
            if n not in graph:
                log.warning('Requested module "%s" not added to digraph', n)

        return graph

    @staticmethod
    def _check_unique_prefixes(existing_prefixes={}, modules={}):
        """Verify that additional modules/prefixes don't collide with existing.

        Args:
          existing_prefixes (dict): map of ``{prefix: module}``.
            Will be updated with additional unique prefixes from ``modules``.
          modules (dict): map of ``{module: prefix}``

        Returns:
          list: of error messages, if any
        """
        errors = []
        for module, prefix in modules.items():
            if existing_prefixes.get(prefix, module) != module:
                errors.append(
                    'Prefix collision: This module or its dependencies import '
                    'both "{0}" and "{1}" under the same prefix "{2}", but '
                    'each prefix MUST uniquely identify a single module. '
                    'One possible cause is using the wrong revision(s) of '
                    "this module's dependencies."
                    .format(existing_prefixes[prefix], module, prefix))
            else:
                existing_prefixes[prefix] = module
        return errors
