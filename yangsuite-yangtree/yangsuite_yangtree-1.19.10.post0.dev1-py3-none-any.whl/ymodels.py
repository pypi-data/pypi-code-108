# Copyright 2016-2021 Cisco Systems, Inc
"""Transform YANG models into a dict.

YSYangModels: Holds multiple YANG models in dict format in a list.
              This class allows message builders to construct multiple
              protocol messages in a single communication.

ParseYang: Parses a single YANG model into a dict.  Extracts relevant
           data of each YANG statement while maintaining the hierarchy
           of the model within children dict.

TreeWalker: Contains various functions that can extract targeted data
            from the dict created by ParseYang.
"""
import pyang
import itertools
from collections import OrderedDict
from yangsuite.logs import get_logger

log = get_logger(__name__)

ALL_NODETYPES = frozenset({
    'action',
    'anydata',
    'anyxml',
    'case',
    'choice',
    'container',
    'grouping',
    'identity',
    'input',
    'leaf',
    'leaf-list',
    'list',
    'module',
    'notification',
    'output',
    'rpc',
    'submodule',
    'typedef',
})

NON_SCHEMA_NODETYPES = frozenset({
    'grouping',
    'identity',
    'typedef',
})
"""Node types that are in neither the schema tree nor the data tree."""

NON_DATA_NODETYPES = frozenset(
    NON_SCHEMA_NODETYPES.union({
        'case',
        'choice',
        'input',
        'output',
    })
)
"""Node types that are not in the data tree."""

DEFAULT_INCLUDED_NODETYPES = frozenset(ALL_NODETYPES - NON_SCHEMA_NODETYPES)


class YSYangModels(object):
    """Object representing one or more ParseYang instances."""

    instances = {}

    @classmethod
    def get_instance(cls, key):
        """Get the instance cached under the given key.

        Returns:
          YSYangModels: instance, or None.
        """
        if cls.instances.get(key, None):
            return cls.instances.get(key, None)
        else:
            from ysyangtree.yangsettree import get_yangset_tree
            from ysyangtree.models import YangSetTree
            ysettree = get_yangset_tree(key, '', [], key)
            if ysettree and isinstance(ysettree, YangSetTree):
                return cls.instances.get(ysettree.user.username, None)
            else:
                return None

    @classmethod
    def store_instance(cls, inst, key):
        """Store the given instance under the given key.

        Args:
          inst (YSYangModels): instance to store
          key (str): Key to store the instance under for future reference.
        """
        if not isinstance(inst, cls):
            raise TypeError("Expected {0} but got {1}".format(cls, inst))
        if key in cls.instances and cls.instances[key] != inst:
            log.info('Replacing cached instance %s with %s under key "%s"',
                     cls.instances[key], inst, key)
        cls.instances[key] = inst

    @classmethod
    def forget_instance(cls, key):
        """Remove the instance under the given key from the cache."""
        if key in cls.instances:
            del cls.instances[key]

    def __init__(self, ctx, modulenames,
                 include_augmentees=True,
                 include_supermodules=True,
                 child_class=None,
                 included_nodetypes=DEFAULT_INCLUDED_NODETYPES):
        """Construct ParseYang instances for the given modules and user ctx.

        Args:
          ctx (YSContext): User context
          modulenames (list): One or more YANG modules to describe
          include_augmentees (bool): If True, automatically extend modulenames
            to include the module(s) augmented by these modules
          include_supermodules (bool): If True, if modulenames contains any
            submodules, automatically extend modulenames with the modules they
            belong to.
          child_class (class): Defaults to :class:`ParseYang`.
          included_nodetypes (set): Nodetype strings to include in
            the constructed instance trees.

        Raises:
          ValueError: if ``include_augmentees`` or ``include_supermodules`` is
            True but ``ctx.repository`` is not a :class:`YSYangSet` or similar
            class (e.g., a generic :class:`pyang.Repository` would trigger
            this error).
        """
        if not child_class:
            child_class = ParseYang
        self.ctx = ctx
        self.yangs = OrderedDict()
        self.nodeid = itertools.count(1)
        self._included_nodetypes = included_nodetypes
        all_modules = set(modulenames)
        if include_augmentees or include_supermodules:
            if not hasattr(ctx.repository, 'digraph'):
                raise ValueError("ctx.repository ({0}) doesn't have a digraph"
                                 .format(ctx.repository))
            dg = ctx.repository.digraph

            while True:
                new_modules = set()
                for name in all_modules:
                    try:
                        node = dg.node[name]
                    except KeyError:
                        continue
                    if include_augmentees:
                        new_modules.update(node['augments'])
                        for subname in node['includes']:
                            new_modules.update(dg.node[subname]['augments'])
                    if include_supermodules and node['kind'] == 'submodule':
                        new_modules.add(node['belongs-to'])

                new_modules -= all_modules
                if not new_modules:
                    break
                log.debug("Added %d extra modules %s to base modules %s "
                          "as augmentation targets and/or supermodules",
                          len(new_modules), new_modules, modulenames)
                all_modules |= new_modules

        # Make sure the ctx has loaded all of these modules
        loaded_modules = set(name for name, rev in ctx.modules)
        if not all(mod in loaded_modules for mod in all_modules):
            self.ctx.load_module_files(all_modules - loaded_modules)

        # Add requested modules first, followed by extras in sorted order
        for name in modulenames + sorted(all_modules.difference(modulenames)):
            # Fail gracefully if modules are somehow unavailable
            try:
                self.yangs[name] = child_class(
                    name, '', self.ctx, self.nodeid,
                    included_nodetypes=self.included_nodetypes)
            except ValueError:
                log.warning('Unable to locate module "%s" in context "%s"',
                            name, self.ctx)
                self.yangs[name] = None

    def __str__(self):
        """Return class name, YANG models parsed, and context instance."""
        return "{0} (YANG models {1}, context {2})".format(
            self.__class__.__name__,
            tuple(self.yangs.keys()),
            self.ctx)

    @property
    def modelnames(self):
        """Return sorted YANG model names parsed in class."""
        return sorted(self.yangs.keys())

    @property
    def jstree(self):
        """Dict with key 'data': list of trees for each contained ParseYang."""
        data = []
        for name, psy in self.yangs.items():
            if psy:
                data.append(psy.tree)
            else:  # Failed loading
                data.append({
                    'text': name,
                    'icon': "fas fa-lg fa-exclamation-triangle",
                    'data': {
                        'error': "Module not found or loading failed",
                    },
                    'a_attr': {'class': 'result-error',
                               'style': 'color:darkred'}})
        return {'data': data,
                'included_nodetypes': sorted(self.included_nodetypes)}

    @property
    def included_nodetypes(self):
        return self._included_nodetypes

    @included_nodetypes.setter
    def included_nodetypes(self, value):
        if value != self._included_nodetypes:
            for child in self.yangs.values():
                child.included_nodetypes = value
            self._included_nodetypes = value


class ParseYang(object):
    """Helper module to YSContext and pyang.

    The instance attribute :attr:`ParseYang.tree` provides a structured
    representation of a single module and its dependencies.

    .. seealso:: :attr:`tree`
    """

    MODULE_OPERATIONS = frozenset({
        'edit-config',
        'get',
        'get-config',
        'notification',
        'rpc',
    })
    """Operation values that may be seen on a root 'module' node."""

    NODE_OPERATIONS = frozenset({
        'edit-config',
        'get',
        'get-config',
        'input',          # RPC 'input' statement
        'notification',
        'output',         # RPC 'output' statement
        'rpc',
    })
    """Operation values that may be seen on any non-module node in the tree."""

    def __init__(self, name, revision, ctx,
                 nodeid=None, included_nodetypes=DEFAULT_INCLUDED_NODETYPES):
        """Construct a ParseYang for the given schema name and user ctx.

        Args:
          name (str): YANG schema name.
          revision (str): Revision string. Leave blank to get the latest
            revision available.
          ctx (YSContext): User context.
          nodeid (itertools.count): Existing iterator to use to assign node IDs
            within this instance's node tree. If not provided, a new iterator
            will be constructed to use node IDs beginning at 1.
          included_nodetypes (tuple): List of nodetype strings to include
            in the generated tree.

        Raises:
          ValueError: if the requested module is not available
        """
        self.name = name
        self.revision = revision
        self._included_nodetypes = included_nodetypes

        self.module = ctx.get_module(self.name, self.revision)
        """The root :class:`pyang.statements.Statement` for module 'name'."""
        if self.module is None:
            if name in ctx.invalid_modules:
                log.debug("Module '%s @ %s' failed loading in ctx '%s'",
                          name, revision, ctx)
                # TODO: grab ctx.errors[name][rev] and report it?
                raise RuntimeError(
                    "Module '{0} @ {1}' was not loaded successfully "
                    "by pyang or YSContext and so cannot be rendered."
                    .format(self.name, self.revision))
            else:
                # Neither valid nor invalid - missing altogether
                log.debug("Module '%s @ %s' not found in ctx %s",
                          name, revision, ctx)
                log.debug("ctx.modules: %s", sorted(ctx.modules.keys()))
                log.debug("ctx.revs: %s", sorted(ctx.revs.keys()))
                raise ValueError("Unable to locate module '{0} @ {1}' in {2}; "
                                 "has it been loaded?"
                                 .format(name, revision, ctx))

        self.ctx = ctx
        # Initialize and set default values for various attributes:
        if nodeid is None:
            self.nodeid = itertools.count(1)
        else:
            self.nodeid = nodeid
        self.pfx = ''
        self.namespace = ''

        self.missing_typedefs = set()
        """Missing typedefs that have already been reported to the user."""

        self.tree = {}
        """Dictionary representing the parsed module as a tree.

        This tree has a structured format analogous to the JSON data used by
        `jsTree`_, where each tree node is a dictionary with any or all
        of the following items:

        id : str
          Unique identifier of this node. In the current implementation,
          a monotonically increasing counter (:func:`itertools.count`), but
          users should not depend on this particular implementation.
        text : str
          Text label for this node
        icon : str
          `Font Awesome`_ class to represent this node.
          (May also be a path to an image file per `jsTree`_, but we don't use
          that option at present).
        a_attr : dict
          HTML attributes to add to the ``<a>...</a>`` element that `jsTree`_
          will generate from this node.
        data : dict
          YANG data associated with this node - specific to this application,
          and generally opaque to `jsTree`_ itself.
        children : list
          Direct children of this node, each represented as its own node
          dictionary like this one (with potential children of its own, etc.)

        Additional keys that `jsTree`_ recognizes but are not currently
        populated by this class include :attr:`state` and :attr:`li_attr`.

        .. _`Font Awesome`: https://fontawesome.com
        .. _jsTree: https://www.jstree.com/docs/json/

        .. seealso::

           :meth:`get_module_node_data`
             Contents of the ``data`` dict for the root-level node representing
             the module or submodule associated with this instance.

           :meth:`get_node_data`
             Contents of the ``data`` dict for all other tree nodes.
        """

        # Now populate the real values:
        self.tree = self.generate_tree()
        self.tw = TreeWalker(self.tree)

    @property
    def included_nodetypes(self):
        """Set of nodetype strings included in :attr:`self.tree`."""
        return self._included_nodetypes

    @included_nodetypes.setter
    def included_nodetypes(self, value):
        if value != self._included_nodetypes:
            self._included_nodetypes = value
            # Regenerate the tree with the new set of nodetypes
            self.tree = self.generate_tree()
            self.tw = TreeWalker(self.tree)

    @property
    def operations(self):
        """Set of operations allowed for this module"""
        if not self.tree:
            return set()
        return set(self.tree['data']['operations'])

    def generate_tree(self, node_callback=None):
        """(Re)generate a dictionary that can be used as :attr:`self.tree`.

        Args:
          node_callback (function): Function to call for each node in the tree
            in order to populate additional data into the tree. Must accept
            kwargs ``stmt``, ``node``, and ``parent_data``
            (which may be ``None``), and return ``node``.

        Returns:
          dict: See :attr:`self.tree`.
        """
        tree = self.get_module_node_data(node_callback=node_callback)

        modulechildren = []

        if 'identity' in self.included_nodetypes:
            for child in self.module.i_identities.values():
                modulechildren.append(self.get_node_data(
                    child, node_callback=node_callback, tree=tree))

        if 'typedef' in self.included_nodetypes:
            for child in self.module.i_typedefs.values():
                modulechildren.append(self.get_node_data(
                    child, node_callback=node_callback, tree=tree))

        if 'grouping' in self.included_nodetypes:
            for child in self.module.i_groupings.values():
                modulechildren.append(self.get_node_data(
                    child, node_callback=node_callback, tree=tree))

        for child in self.module.i_children:
            if child.keyword in self.included_nodetypes:
                modulechildren.append(self.get_node_data(
                    child, node_callback=node_callback, tree=tree))

        if len(modulechildren) > 0:
            tree['children'] = modulechildren

        return tree

    def get_module_node_data(self, node_callback=None):
        """Create the node dictionary for the module itself.

        Args:
          node_callback (function): Callback function, should take ``stmt``,
            ``node``, and ``parent_data`` (possibly ``None``) as kwargs and
            return the updated ``node`` dictionary.

        The base dictionary for all nodes are as described under :attr:`tree`;
        for this base node, the :attr:`data` sub-dictionary (actually an
        :class:`~collections.OrderedDict`) will have the following items, in
        the following order:

        module : str
          Name of this module, or, if this is a submodule, the name of the
          module it ``belongs-to``.
        submodule : str
          Name of this submodule, if it is a submodule.
        revision : str
          Latest revision date of this (sub)module.
        revision_info : str
          Any description string associated with the latest revision.
        description : str
          The description string for the (sub)module as a whole.
        organization : str
          The organization string for this (sub)module.
        imports : list
          List of "module-name" or "module-name revision" strings
          identifying the modules imported by this module.
        namespace : str
          Namespace string used by this module, such as
          "urn:ietf:params:xml:ns:yang:ietf-routing".
        prefix : str
          Namespace prefix string used by this module, such as "rt".
        namespace_prefixes : dict
          Sub-dictionary mapping namespace prefixes
          to the corresponding namespace strings for all namespaces known to
          this module. Example::

            {
              'rt':   "urn:ietf:params:xml:ns:yang:ietf-routing",
              'yang': "urn:ietf:params:xml:ns:yang:ietf-yang-types",
              'if':   "urn:ietf:params:xml:ns:yang:ietf-interfaces",
            }

        modtype : str
          Either "module" or "submodule"
        operations : list
          Strings representing the NETCONF operations supported by this module;
          see :const:`MODULE_OPERATIONS` for the possible values.

        Returns:
          dict: 'node' dictionary containing parsed data.
        """
        stmt = self.module
        node = {'id': next(self.nodeid), 'text': stmt.arg}
        data = OrderedDict()
        # Keys will typically be displayed in the insertion order by the UI, so
        # some thought has been put into this ordering:
        if stmt.keyword == "module":
            data['module'] = stmt.arg
            node['icon'] = 'fas fa-lg fa-cubes ystree-root'
        else:
            data['submodule'] = stmt.arg
            data['module'] = stmt.i_modulename
            node['icon'] = 'fas fa-cube ystree-root'

        data.update([
            # Immediately relevant to casual viewers
            ('revision', self.revision),
            ('revision_info', ''),
            ('description', self.get_subst_arg(stmt, 'description')),
            ('organization', ''),
            # Of interest to intermediate users
            ('imports', []),
            ('namespace', self.namespace),
            ('prefix', self.pfx),
            ('namespace_prefixes', {}),
            # Advanced / developer / API information
            ('modtype', stmt.keyword),
            ('operations', []),
        ])

        # Per RFC module MUST always have a namespace statement.
        # However, let's not error out unless we need to.
        # If no namespace, default data['namespace'] to self.namespace
        # (which in turn defaults to ''), rather than None.
        if stmt.keyword == "module":
            self.namespace = self.set_data_subst_arg(data, stmt, 'namespace',
                                                     default=self.namespace)
        else:
            mod = stmt.i_prefix
            try:
                rev = stmt.i_ctx.repository.digraph.node[mod]['revision']
            except:
                rev = None
            mod_stmt = self.ctx.get_module(mod, rev)
            self.namespace = self.set_data_subst_arg(data, mod_stmt,
                                                     'namespace',
                                                     data_key=stmt.i_prefix,
                                                     default=self.namespace)
        data['namespace'] = self.namespace

        # Likewise, mandatory prefix statement - defaulting to '' if missing.
        if stmt.i_prefix:
            self.pfx = stmt.i_prefix
        data['prefix'] = self.pfx

        nspdata = data['namespace_prefixes']

        # We may need namespace from identityref so make it available
        self.nspdata = nspdata

        all_i_prefixes = dict(stmt.i_prefixes.items())

        def add_prefix(pfx, mod, rev):
            """Add prefix-to-module mapping unless prefix is already used."""
            if pfx not in all_i_prefixes:
                all_i_prefixes[pfx] = (mod, rev)
            else:
                if (mod, rev) != all_i_prefixes[pfx]:
                    log.warning("Prefix %s is used for both %s and %s!",
                                pfx, all_i_prefixes[pfx], (mod, rev))

        def add_prefixes(stmt, base_pfx):
            """Add prefix-to-module mappings from the stmt's prefixes."""
            if stmt:
                for pfx, (mod, rev) in stmt.i_prefixes.items():
                    if pfx != base_pfx:
                        add_prefix(pfx, mod, rev)

        # Handle everything in stmt.i_prefixes, plus everything in
        # each augmenter's, deriver's, and submodule's i_prefixes
        for (pfx, (mod, rev)) in stmt.i_prefixes.items():
            if pfx != self.pfx:
                data['imports'].append("{0}{1}".format(
                    mod, (" @ " + rev) if rev else ""))

            for aug_mod in self.ctx.augmenters_of.get(mod, []):
                add_prefixes(self.ctx.get_module(aug_mod), pfx)

            for id_mod in self.ctx.identity_derivers_of.get(mod, []):
                add_prefixes(self.ctx.get_module(id_mod), pfx)

            for submod in self.ctx.submodules_of.get(mod, []):
                add_prefixes(self.ctx.get_module(submod), pfx)

        for (pfx, (mod, rev)) in sorted(all_i_prefixes.items()):
            mod_stmt = self.ctx.get_module(mod, rev)
            if not mod_stmt:
                log.warning("No module %s, can't get namespace for prefix %s",
                            mod, pfx)
                continue
            if mod_stmt.keyword == "submodule":
                mod = mod_stmt.i_prefix
                try:
                    rev = stmt.i_ctx.repository.digraph.node[mod]['revision']
                except:
                    rev = None
                mod_stmt = self.ctx.get_module(mod, rev)

            # Set nspdata[pfx] = namespace, if found
            self.set_data_subst_arg(nspdata, mod_stmt, 'namespace',
                                    data_key=pfx, default=None)

        self.set_data_subst_arg(data, stmt, 'organization')

        self.revision = self.set_data_subst_arg(data, stmt, 'revision',
                                                default=self.revision)
        rev = stmt.search_one('revision')
        self.set_data_subst_arg(data, rev, 'description',
                                data_key='revision_info')

        node['data'] = data

        if node_callback:
            node = node_callback(stmt=stmt, node=node)

        return node

    STMT_ICONS = {
        "action": 'fas fa-lg fa-bullseye ystree-root',
        "anydata": 'fas fa-lg fa-asterisk ystree-leaf',
        "anyxml": 'fas fa-lg fa-code ystree-leaf',
        "case": 'fas fa-lg fa-arrow-right ystree-node',
        "choice": 'fas fa-lg fa-code-branch ystree-node',
        "container": 'far fa-lg fa-folder-open ystree-node',
        "grouping": 'fas fa-lg fa-cube ystree-definition',
        "identity": 'fas fa-lg fa-info ystree-definition',
        "input": 'fas fa-lg fa-sign-in-alt ystree-node',
        "leaf": 'fas fa-lg fa-leaf ystree-leaf',
        "leaf-list": 'fab fa-lg fa-pagelines ystree-leaf',
        "list": 'fas fa-lg fa-list ystree-node',
        "module": 'fas fa-lg fa-cubes ystree-root',
        "notification": 'fas fa-lg fa-gift ystree-root',
        "output": 'fas fa-lg fa-sign-out-alt ystree-node',
        "rpc": 'far fa-lg fa-envelope ystree-root',
        "submodule": 'fas fa-cube ystree-root',
        "typedef": 'far fa-lg fa-star ystree-definition',
    }
    """Simple suggested Font Awesome node icons.

    These may (in fact, should) be overridden by more complex icons
    (with layering, badges, etc.) on the client side, but we can at least
    provide some not-too-ugly defaults in case the client declines to do so.
    """

    def get_node_data(self, stmt,
                      parent_data=None, node_callback=None, tree=None):
        """Create the node dictionary for a given Statement and its children.

        Args:
          stmt (pyang.statements.Statement): Child statement to process.
          parent_data (dict): Data previously constructed by this method
            for the stmt's parent statement.
          node_callback (function): Callback function, should take ``stmt``,
            ``node``, and ``parent_data`` as kwargs and return the updated
            ``node`` dictionary.

        Returns:
          dict: Node data, as described below.

        The base data for any node are as described under :attr:`tree`;
        for any statement node passed through this method, the :attr:`data`
        sub-dictionary (actually an :class:`~collections.OrderedDict`)
        will receive some or all of the following items in the following order:

        name : str
          The name (YANG identifier) of this node, such as "routing-state"
        nodetype : str
          The type (YANG keyword) of this node, such as "container", "list",
          "leaf", etc.
        deviation : str
          The string "not-supported", iff this node has been marked as
          not-supported by a deviation file.
        status : str
          The string "deprecated" or "obsolete" iff this node's status is
          marked as such. Note that this key is omitted to save room when
          the node's status is "current" (either explicitly or implicitly).
        datatype : str
          For ``leaf`` and ``leaf-list`` nodes, the associated data ``type``
          for this node. Otherwise absent.
        description : str
          The ``description`` string associated with this statement.
        module : str
          The module this statement belongs to
        revision : str
          The latest revision data of the owning module
        xpath : str
          `Data node`_ XPath to reach this node via the data tree,
          starting from the module root. Node names local to this module will
          not be prefixed, while those from other modules will be prefixed.
          Example:
          ``/interfaces/interface/subinterfaces/subinterface/vlan:vlan``
        prefix : str
          Module namespace prefix applicable to this node.
        namespace : str
          Module namespace of this node.
        mandatory : str
          The string "true", iff this node is mandatory
          (a ``leaf`` or ``choice`` with a ``mandatory`` substatement,
          or a ``list`` or ``leaf-list`` with non-zero ``min-elements``,
          or a ``container`` that has any of the above as children).
          Omitted (*not* "false") if non-mandatory.
        must : str
          Text of any ``must`` XPath expression associated with this node.
        when : str
          Text of any ``when`` XPath expression associated with this node.

        .. seealso::

          :meth:`get_stmt_specific_data`
            May populate additional item(s) into :attr:`data` at this point,
            depending on the particular statement keyword.
          :meth:`get_type_specific_data`
            Called from :meth:`get_stmt_specific_data` for ``leaf`` and
            ``leaf-list`` statements, may populate additional :attr:`data` here
            according to the statement's :attr:`datatype`.

        Finally the following items may be added as well by this method:

        access : str
          One of "read-only", "read-write", or "write"
        operations : list
          Operations that can be performed on this node.
          See :const:`NODE_OPERATIONS` for possible operations. Note that a
          node such as a ``choice`` or ``case`` may be "read-write" and yet
          have no applicable operations, as the operations apply
          specifically to its child nodes.
        xpath_pfx : str
          `Data node`_ identifier, as :attr:`xpath`, but
          prefixing all names, even those local to this module.
        schema_node_id : str
          `Schema node identifier`_, path to this node via the schema tree.
          May be identical to :attr:`xpath` but may also include non-data
          nodes not in :attr:`xpath`, as described in RFC 6020.

        .. _`Data node`: https://tools.ietf.org/html/rfc6020#section-3
        .. _`Schema node identifier`:
          https://tools.ietf.org/html/rfc6020#section-6.5
        """
        # Don't prefix locally defined node, do prefix node from other modules
        pfx = ''
        if stmt.i_module.i_prefix != self.pfx:
            pfx = stmt.i_module.i_prefix + ":"
        node = {'id': next(self.nodeid),
                'text': pfx + stmt.arg}

        node['icon'] = self.STMT_ICONS.get(stmt.keyword,
                                           'fas fa-lg fa-exclamation-triangle')

        # As data is an OrderedDict, the key insertion order will be stored.
        # Keys will typically be displayed in this same order by the UI, so
        # the insertion order should be chosen with care.
        data = OrderedDict()

        #
        # Initial data - self-explanatory and immediately relevant to users
        #

        data['name'] = stmt.arg
        data['nodetype'] = stmt.keyword

        if hasattr(stmt, 'i_this_not_supported'):
            data['deviation'] = 'not-supported'
            if 'a_attr' not in node:
                node['a_attr'] = {}
            node['a_attr']['class'] = "ystree-not-supported"

        status = stmt.search_one('status')
        if status and status.arg in ['deprecated', 'obsolete']:
            data['status'] = status.arg

        if stmt.keyword in ['leaf', 'leaf-list']:
            # reserve space in the order; populated by get_stmt_specific_data
            data['datatype'] = ''
            data['basetype'] = ''

        self.set_data_subst_arg(data, stmt, 'description', default='')

        data['module'] = stmt.i_module.arg
        data['revision'] = stmt.i_module.i_latest_revision

        #
        # Intermediate data - more complex, of interest to intermediate users
        #

        xpath = self.get_stmt_node_id(stmt, mode='data', prefix_all=False)
        if xpath:
            data['xpath'] = xpath

        data['prefix'] = stmt.i_module.i_prefix

        if not data['prefix']:
            self.set_data_subst_arg(data, stmt.i_module, 'namespace',
                                    default='')
        else:
            mod = stmt.i_module.i_prefix
            try:
                rev = stmt.i_module.i_ctx.repository.digraph.    \
                      node[mod]['revision']
            except:
                rev = None
            mod_stmt = self.ctx.get_module(mod, rev)
            self.set_data_subst_arg(data, mod_stmt,
                                    'namespace',
                                    default=self.namespace)

        if pyang.statements.is_mandatory_node(stmt):
            data['mandatory'] = 'true'
            node['icon'] = "fas fa-lg fa-exclamation-circle"

        must = stmt.search_one('must')
        if must:
            data['must'] = must.arg

        when = stmt.search_one('when')
        if when:
            data['when'] = when.arg

        node['data'] = data

        # Get any additional data based on the statement keyword
        self.get_stmt_specific_data(stmt, node)

        #
        # Advanced data for skilled users and/or programmatic APIs
        #

        if stmt.keyword not in NON_SCHEMA_NODETYPES:
            if parent_data and 'operations' in parent_data and any(
                    op in ['input', 'output', 'notification']
                    for op in parent_data['operations']):
                # Input/output/notification subtrees all have the same
                # access and operations as their parents, as they're not
                # part of the data tree.
                data['access'] = parent_data['access']
                data['operations'] = parent_data['operations']
            else:
                data['access'] = self.get_access(stmt)
                self.get_allowed_ops(stmt, data, tree)

        xpath_pfx = self.get_stmt_node_id(stmt, mode='data', prefix_all=True)
        if xpath_pfx:
            data['xpath_pfx'] = xpath_pfx

        schema_node_id = self.get_stmt_node_id(stmt, mode='schema',
                                               prefix_all=False)
        if schema_node_id:
            data['schema_node_id'] = schema_node_id

        # To reduce confusion but not clutter the tree too much,
        # we include not-supported nodes in the tree (so the user isn't
        # confused by their total absence), but do not descend
        # to their own child nodes if any.
        if not hasattr(stmt, 'i_this_not_supported'):
            # Recurse and add children of this Statement.
            children = []

            if 'typedef' in self.included_nodetypes and hasattr(stmt,
                                                                "i_typedefs"):
                for child in stmt.i_typedefs.values():
                    children.append(self.get_node_data(
                        child, parent_data=data, node_callback=node_callback,
                        tree=tree))

            # Unlike 'typedef', 'identity' can only exist at the
            # module/submodule level, so we don't need to check for
            # an i_identities attribute here.

            if ('grouping' in self.included_nodetypes and
                    hasattr(stmt, 'i_groupings')):
                for child in stmt.i_groupings.values():
                    children.append(self.get_node_data(
                        child, node_callback=node_callback, tree=tree))

            if hasattr(stmt, "i_children"):
                for child in self.i_children_ordered(stmt, data):
                    if child.keyword in self.included_nodetypes:
                        children.append(self.get_node_data(
                            child, parent_data=data,
                            node_callback=node_callback, tree=tree))

            # Append any children that were marked as not-supported by a
            # 'deviation' statement and so are not included in stmt.i_children.
            if hasattr(stmt, "i_not_supported"):
                for unsupported in stmt.i_not_supported:
                    if unsupported.keyword in self.included_nodetypes:
                        children.append(self.get_node_data(
                            unsupported, parent_data=data,
                            node_callback=node_callback, tree=tree))

            if children:
                node['children'] = children

        # Nodes only have a basetype if they have a derived (non-base) datatype
        # If no basetype is needed, delete the placeholder added above.
        if 'basetype' in node['data'] and not node['data']['basetype']:
            del node['data']['basetype']

        if node_callback:
            node = node_callback(stmt=stmt, parent_data=parent_data, node=node)

        return node

    def i_children_ordered(self, stmt, data):
        """Ordered list of child Statements of the given Statement.

        Helper method to :meth:`get_node_data`.

        Mostly we respect the order of statements provided by the module
        (and hence by pyang), but we have at least one exception:

          The list's key nodes are encoded as subelements to the list's
          identifier element, in the same order as they are defined within the
          "key" statement.

          The rest of the list's child nodes are encoded as subelements to the
          list element, after the keys. If the list defines RPC input or
          output parameters, the subelements are encoded in the same order as
          they are defined within the "list" statement. Otherwise, the
          subelements are encoded in any order.

          -- https://tools.ietf.org/html/rfc6020#section-7.8.5

        Therefore, we need to ensure that the key nodes are always the
        first children of a list node.

        Args:
          stmt (pyang.statements.Statement): Statement to check children of.
          data (dict): Data previously constructed for the given stmt.
        Returns:
          list: Child statements in the order to be processed.
        """
        child_statements = stmt.i_children
        if 'keys' in data:
            keys = data['keys']

            def sort_function(child):
                if child.arg in keys:
                    return keys.index(child.arg)
                return 1000

            child_statements = sorted(child_statements, key=sort_function)
        return child_statements

    def get_stmt_node_id(self, stmt, mode='schema', prefix_all=True):
        """Build the schema or data node identifier (XPath) for a statement.

        Helper method to :meth:`get_node_data`.

        .. seealso:: :meth:`pyang.statements.mk_path_str`

        Args:
          stmt (pyang.statements.Statement) Statement to process.
          mode (str): One of 'schema' or 'data'.
          prefix_all (bool): If True, add namespace prefixes to all
            identifiers, even those in the current module and submodules.
            If False, only external module identifiers will be prefixed.

        Returns:
          str: XPath for schema or data node identifier, or None for nodes
            not in the schema tree
        """
        if mode not in ['data', 'schema']:
            raise ValueError
        path_nodes = []
        # Iterate upwards from this statement until reaching the top
        while stmt.keyword not in ['module', 'submodule']:
            if stmt.keyword in NON_SCHEMA_NODETYPES:
                return None
            elif mode == 'schema' or stmt.keyword not in NON_DATA_NODETYPES:
                if prefix_all or stmt.i_module.i_prefix != self.pfx:
                    path_nodes.append(stmt.i_module.i_prefix + ":" + stmt.arg)
                else:
                    path_nodes.append(stmt.arg)
            stmt = stmt.parent

        path_nodes.reverse()
        return "/" + "/".join(path_nodes)

    #
    # Here and below are helper functions to the above - not generally to be
    # called directly from elsewhere.
    #

    def get_subst_arg(self, stmt, keyword, default=''):
        """Find a substatement and return its arg value, or default.

        .. seealso:: :meth:`set_data_subst_arg`

        Args:
          stmt (pyang.statements.Statement): Parent statement
          keyword (str): Substatement keyword to find
          default (str): Value to return if substatement is not found

        Returns:
          str: The substatement arg string, or default value
        """
        if stmt:
            subst = stmt.search_one(keyword)
            if subst:
                return subst.arg
        return default

    def set_data_subst_arg(self, data, stmt, keyword,
                           data_key=None, default=None):
        """Find a substatement and set its arg value into the data.

        .. seealso:: :meth:`get_subst_arg`

        Args:
          data (dict): Dict to store the resulting value into
          stmt (pyang.statements.Statement): Parent statement
          keyword (str): Substatement keyword to find
          data_key (str): Key to store the value under, if different from
            the ``keyword``.
          default (str): Value to set in data if substatement is not found.
            A value of ``None`` means to not set anything (omit data_key).

        Returns:
          str: The value being set, or None
        """
        val = self.get_subst_arg(stmt, keyword, default=default)
        if val is not None:
            if not data_key:
                data_key = keyword
            data[data_key] = val
        return val

    def get_stmt_specific_data(self, stmt, node):
        """Get node data fields specific to certain statement types.

        Helper to :meth:`get_node_data`.

        Args:
          stmt (pyang.statements.Statement): A statement of any type.
          node (dict): Node to store information into

        May set any of the following items under the :attr:`node`'s "data"
        sub-dictionary:

        base : str
          for ``identity`` statements
        basetype : str
          for ``typedef`` statements
        datatype : str
          for ``leaf`` and ``leaf-list`` statements
        default : str
          for statements with a default value (``leaf``, ``choice``,
          ``leaf-list``, ``typedef``)
        key : str
          The string "true", iff this is a ``leaf`` acting as a list key.
        keys : list
          For a ``list`` statement with keys, list of the leaf name(s)
          acting as keys.
        options : list
          - for a ``choice`` statement, list of case names, with prefixes as
            needed for cases defined elsewhere, e.g.
            ``['rfc5277', 'yp:update-filter']``
          - for a ``leaf`` or ``leaf-list`` statement, see
            :meth:`get_type_specific_data`
        presence : str
          The string "true", iff this is a "presence" ``container`` statement.
        units : str
          Units associated with a ``leaf``, ``leaf-list``, or ``typedef``

        May also update the node's :attr:`icon` value.

        .. seealso::

          :meth:`get_type_specific_data`
            Called from this method for ``leaf`` and ``leaf-list`` statements,
            may populate additional :attr:`data` according to the statement's
            :attr:`datatype`.
        """
        data = node['data']
        if stmt.keyword == 'anydata':
            pass  # No special processing at this time
        elif stmt.keyword == 'anyxml':
            pass  # No special processing at this time
        elif stmt.keyword == 'case':
            pass  # No special processing at this time
        elif stmt.keyword == 'choice':
            if hasattr(stmt, "i_default_str"):
                if stmt.i_default_str:
                    data['default'] = stmt.i_default_str
            data['options'] = []
            for case in stmt.search('case', stmt.i_children):
                if case.i_module == stmt.i_module:
                    data['options'].append(case.arg)
                else:
                    data['options'].append(case.i_module.i_prefix + ":" +
                                           case.arg)

        elif stmt.keyword == 'container':
            if stmt.search_one('presence'):
                data['presence'] = 'true'

        elif stmt.keyword == 'grouping':
            pass  # No special processing at this time

        elif stmt.keyword == 'identity':
            self.set_data_subst_arg(data, stmt, 'base')

        elif stmt.keyword == 'input':
            pass  # No special processing at this time

        elif stmt.keyword == 'leaf':
            if hasattr(stmt, "i_default_str") and stmt.i_default_str:
                data['default'] = stmt.i_default_str
            self.set_data_subst_arg(data, stmt, 'type', data_key='datatype')
            if data.get('datatype') == 'leafref':
                node['icon'] = 'fas fa-lg fa-external-link-square-alt'
            self.set_data_subst_arg(data, stmt, 'units', data_key='units')
            self.get_type_specific_data(stmt.search_one('type'), data)
            if stmt.parent.keyword == 'list':
                keystmt = stmt.parent.search_one('key')
                if keystmt is not None:
                    # Key argument is a space-separated list
                    keys = keystmt.arg.split(" ")
                    if stmt.arg in keys:
                        node['icon'] = "fas fa-lg fa-key"
                        data['key'] = 'true'

        elif stmt.keyword == 'leaf-list':
            if hasattr(stmt, "i_default_str") and stmt.i_default_str:
                data['default'] = stmt.i_default_str
            self.set_data_subst_arg(data, stmt, 'type', data_key='datatype')
            self.set_data_subst_arg(data, stmt, 'units', data_key='units')
            self.get_type_specific_data(stmt.search_one('type'), data)

        elif stmt.keyword == 'list':
            keystmt = stmt.search_one('key')
            if keystmt is not None:
                # Key argument is a space-separated list,
                # but pyang keeps it as a string. So we split it here:
                data['keys'] = keystmt.arg.split(" ")

        elif stmt.keyword == 'notification':
            pass  # No special processing at this time
        elif stmt.keyword == 'output':
            pass  # No special processing at this time
        elif stmt.keyword == 'rpc':
            pass  # No special processing at this time

        elif stmt.keyword == 'typedef':
            self.set_data_subst_arg(data, stmt, 'type', data_key='basetype')
            if hasattr(stmt, "i_default_str") and stmt.i_default_str:
                data['default'] = stmt.i_default_str
            self.set_data_subst_arg(data, stmt, 'units', data_key='units')
            self.get_type_specific_data(stmt.search_one('type'), data)

        else:
            # Unknown/unhandled stmt type
            node['icon'] = 'fas fa-lg fa-exclamation-triangle'

    def get_type_specific_data(self, stmt, data):
        """Populate data for a leaf/leaf-list based on the given type.

        Helper method to :meth:`get_stmt_specific_data`.

        Args:
          stmt (pyang.statements.Statement): A 'type' statement.
          data (dict): Dict to populate with additional type-specific data.

        May populate any of the following items into the :attr:`data` dict,
        depending on the given statement type:

        base : str
          The base identity of an ``identityref``
        basetype : str
          If the type is a derived type, the base type (such as "string",
          "enumeration", "union") of this type
        bits : list
          For type ``bits``, the bit names, e.g., ``['SYN', 'ACK', 'RST']``
        fraction_digits : int
          For type ``decimal64``, the number of decimal digits permitted,
          as in the ``fraction-digits`` YANG statement
        leafref_path : str
          The path of a ``leafref``, such as "../interface/name"
        max : str
          Maximum valid value for any integer type (``[u]int[8|16|32|64]``)
          or type ``decimal64``
        min : str
          Minimum valid value for any integer type (``[u]int[8|16|32|64]``)
          or type ``decimal64``
        members : list
          For type ``union``, a list of sub-dictionaries corresponding to each
          member type of the union, for example::

            [{
               'datatype': 'enumeration',
               'options': ['yes', 'no'],
             }, {
               'datatype': 'enumeration',
               'options': ['alpha', 'beta'],
             }, {
               'datatype': 'bits',
               'bits': ['SYN', 'ACK'],
             }]

        options : list
          Depending on the given type.

          - for type ``boolean``, the list ``['true', 'false']``
          - for type ``enumeration``, the enum name strings, for example,
            ``['TRUE', 'FALSE', 'FILE_NOT_FOUND']``
          - for type ``identityref``, the target names, for example,
            ``['ianaift:ethernetCsmacd', 'ianaift:gigabitEthernet']``

        ranges : list
          For an int type or decimal64 with more than one defined range of
          valid values, a list of ``min, [max]`` pairs, such as
          ``[(1, 199), (1300, 2699)]`` or ``[(512, None), (1024, None)]``
        typespec : dict
          .. warning::
            The "typespec" key is frozen and should be considered deprecated.
            We MUST NOT add any new typespec entries as older versions of
            :mod:`ysnetconf` WILL demonstrate unexpected and undesirable
            behavior on encountering these!

          A dict, if necessary, with key "name" and value of the
          type string, plus at least one of the following:

          - for type 'enumeration', a key "values", with a list of enum
            (name, value) tuples, e.g. ``[('yes', 1), ('no', 0)]``
            For backwards compatibility only - consumers of the node data
            generally only need the ``name``, which can be accessed more easily
            from the ``options`` key above.

          - for type 'identityref', a key "iref", with a list of dicts of form
            ``{namespace:... prefix:... name:...}``.
            For backwards compatibility only - the ``name`` is accessible more
            easily via ``options`` above, the ``prefix`` is trivial to extract
            from the ``name``, and the ``namespace`` can be identified from
            this tree's root node's 'namespace_prefixes` data.

          - for nodes of any int type (``[u]int[8|16|32|64]``), the keys
            "min" and "max", describing the minimum and maximum valid values.
            For backwards compatibility only - these keys are also available
            directly on the ``data`` dictionary itself now.
        """
        if stmt is None:
            return
        if not hasattr(stmt, 'i_type_spec') or stmt.i_type_spec is None:
            # This happens if pyang was unable to find the base typedef
            # for this type.
            if stmt.arg not in self.missing_typedefs:
                log.warning("No typedef found for type %s (used at %s) --"
                            " yangset may be incomplete or may contain"
                            " incompatible module versions",
                            stmt.arg,
                            self.get_stmt_node_id(stmt.parent))
                self.missing_typedefs.add(stmt.arg)
            return

        # Otherwise, let's handle various built-in types as appropriate:
        spec = OrderedDict()
        if isinstance(stmt.i_type_spec, pyang.types.BitTypeSpec):
            data['bits'] = [name for name, pos in stmt.i_type_spec.bits]
        elif isinstance(stmt.i_type_spec, pyang.types.BooleanTypeSpec):
            data['options'] = ['true', 'false']
        elif isinstance(stmt.i_type_spec, pyang.types.EnumTypeSpec):
            spec['values'] = stmt.i_type_spec.enums
            data['options'] = [name for (name, val) in spec['values']]
        elif isinstance(stmt.i_type_spec, pyang.types.IdentityrefTypeSpec):
            data['base'] = self.get_subst_arg(stmt, 'base')
            if not data['base']:
                # Might be identityref in a typedef so check idbases
                if stmt.i_type_spec.idbases:
                    base = stmt.i_type_spec.idbases[0]
                    data['base'] = base.arg
            data['options'] = self._get_identityrefs(stmt, data)
        elif isinstance(stmt.i_type_spec, pyang.types.IntTypeSpec):
            data['min'] = str(stmt.i_type_spec.min)
            data['max'] = str(stmt.i_type_spec.max)
            spec['min'] = data['min']
            spec['max'] = data['max']
        elif isinstance(stmt.i_type_spec, pyang.types.PathTypeSpec):
            if hasattr(stmt.i_type_spec, 'i_expanded_path'):
                data['leafref_path'] = stmt.i_type_spec.i_expanded_path
            # Treat the target leaf as the base type
            subtype_data = {}
            if hasattr(stmt.i_type_spec, 'i_target_node'):
                target_type = stmt.i_type_spec.i_target_node.search_one('type')
                self.get_type_specific_data(target_type, subtype_data)
                if 'typespec' in subtype_data:
                    data['basetype'] = subtype_data['typespec']['name']
                    del subtype_data['typespec']
                if 'leafref_path' in subtype_data:
                    # Leafref to a leafref - keep the original, don't overwrite
                    del subtype_data['leafref_path']
            data.update(subtype_data)
        elif isinstance(stmt.i_type_spec, pyang.types.UnionTypeSpec):
            data['members'] = []
            for subtype in stmt.i_type_spec.types:
                subspec = OrderedDict()
                self.get_type_specific_data(subtype, subspec)
                if 'typespec' in subspec:
                    # union has never had typespec, let's not add it now.
                    del subspec['typespec']
                subspec['datatype'] = subtype.arg
                data['members'].append(subspec)

            if not data['members']:
                del data['members']
        elif isinstance(stmt.i_type_spec, pyang.types.RangeTypeSpec):
            data['min'] = str(stmt.i_type_spec.min)
            data['max'] = str(stmt.i_type_spec.max)
            if len(stmt.i_type_spec.ranges) > 1:
                # Complex set of ranges, beyond just 'min..max'
                ranges = []
                for rmin, rmax in stmt.i_type_spec.ranges:
                    rmin = str(rmin)
                    rmax = str(rmax)
                    ranges.append((rmin, rmax))
                data['ranges'] = ranges
            if hasattr(stmt.i_type_spec, 'fraction_digits'):
                data['fraction_digits'] = stmt.i_type_spec.fraction_digits

        elif isinstance(stmt.i_type_spec, pyang.types.Decimal64TypeSpec):
            data['min'] = str(stmt.i_type_spec.min)
            data['max'] = str(stmt.i_type_spec.max)
            data['fraction_digits'] = stmt.i_type_spec.fraction_digits

        elif isinstance(stmt.i_type_spec, pyang.types.EmptyTypeSpec):
            pass

        elif isinstance(stmt.i_type_spec, pyang.types.PatternTypeSpec):
            data['patterns'] = [r[-1] for r in stmt.i_type_spec.res]

        elif isinstance(stmt.i_type_spec, pyang.types.StringTypeSpec):
            # NX-OS has its own custom pattern annotation,
            # which pyang doesn't recognize but we want to do so.
            # When pyang parses the YANG model, type constraints
            # "bubble up" from base types to the derived types; in order to
            # get the same behavior here (starting from the derived type)
            # we have to "drill down" until we reach the base type that has
            # the pattern-posix annotation on it.
            patterns_posix = []
            type_stmt = stmt
            while type_stmt:
                patterns_posix = type_stmt.search(('Cisco-NX-OS-mtx',
                                                   'pattern-posix'))
                if patterns_posix:
                    break
                if not type_stmt.i_typedef:
                    break
                type_stmt = type_stmt.i_typedef.search_one("type")

            if patterns_posix:
                data['patterns'] = [pstmt.arg for pstmt in patterns_posix]

        elif isinstance(stmt.i_type_spec, pyang.types.LengthTypeSpec):
            if len(stmt.i_type_spec.lengths) > 1:
                log.warning("Complex LengthTypeSpec encountered; "
                            "not yet fully handled by YANG Suite")
            data['minLength'] = stmt.i_type_spec.lengths[0][0]
            data['maxLength'] = stmt.i_type_spec.lengths[0][1]

        elif isinstance(stmt.i_type_spec, pyang.types.BinaryTypeSpec):
            # base64 encoding/decoding
            pass

        else:
            log.warning("Unfamiliar typespec (%s) encountered, unhandled",
                        type(stmt.i_type_spec))

        if spec:
            spec['name'] = stmt.i_type_spec.name
            data['typespec'] = spec

        if 'datatype' in data and stmt.i_type_spec.name != data['datatype']:
            data['basetype'] = stmt.i_type_spec.name

        # TODO: handle union with a single member (roll up)
        # see Cisco-IOS-XE-sla leaf url type union { type string }

    def _add_nspdata(self, stmt):
        """Helper function to add prefix/namespace if not already there."""
        for pfx, mod_rev in stmt.i_module.i_prefixes.items():
            if pfx in self.nspdata:
                continue
            mod, _ = mod_rev
            module = self.ctx.get_module(mod)
            if module:
                ns = module.search_one('namespace')
                if ns:
                    self.nspdata[pfx] = ns.arg

    def _get_identityrefs(self, stmt, data):
        """Helper method to :meth:`get_type_specific_data`."""
        base_list = []
        pfx = ''

        base = stmt.search_one('base')
        if not base:
            # This might be a typedef
            if stmt.i_type_spec.idbases:
                base = stmt.i_type_spec.idbases[0]
                ids = self.ctx.identities.get(
                    base.i_module.arg, {}
                )
                if ids:
                    self._add_nspdata(base)
                    base_list = ids.get(base.arg, [])
                return sorted(base_list)
            else:
                # all identityref should have a base
                log.error('{0} identityref without a base'.format(stmt.arg))
                return base_list

        if ':' in base.arg:
            pfx, base_idt = base.arg.split(':')
        else:
            base_idt = base.arg

        if not pfx or pfx == stmt.i_module.i_prefix:
            base = stmt
            ids = self.ctx.identities.get(stmt.i_module.arg, {})
        else:
            mod, _ = base.i_module.i_prefixes[pfx]
            ids = self.ctx.identities.get(mod, {})

        if ids:
            base_list = ids.get(base_idt, [])
            self._add_nspdata(base)

        return sorted(base_list)

    def get_access(self, stmt):
        """Get a string describing the access type of the given Statement.

        Args:
          stmt (pyang.statements.Statement): Statement to inspect.
        Returns:
          str: One of 'read-only', 'read-write', or 'write'
        """
        if stmt.keyword in ['rpc', 'input', 'action']:
            return 'write'
        elif stmt.keyword in ['notification', 'output']:
            return 'read-only'
        elif hasattr(stmt, 'i_config') and stmt.i_config is True:
            return 'read-write'
        else:
            return 'read-only'

    _OPS_NONE = ()
    _OPS_ACTION = ('action', )
    _OPS_RPC = ('rpc', )
    _OPS_NOTIFICATION = ('notification', )
    _OPS_INPUT = ('input', )
    _OPS_OUTPUT = ('output', )
    _OPS_READONLY = ('get', )
    _OPS_DEFAULT = ('edit-config', 'get-config', 'get')

    def get_allowed_ops(self, stmt, data, tree=None):
        """Get the set of data operations applicable to this node and module.

        Args:
          stmt (pyang.statements.Statement): Node being inspected
          data (dict): Data dictionary to set key 'operations' on
          tree (dict): Root of node data tree containing the ``data``.
            If given, ``tree['data']['operations']`` may be updated.
        """
        if stmt.keyword in ['choice', 'case']:
            # These statements are not part of the data tree, only schema tree.
            data['operations'] = self._OPS_NONE
        elif stmt.keyword in ['action']:
            data['operations'] = self._OPS_ACTION
        elif stmt.keyword in ['rpc']:
            data['operations'] = self._OPS_RPC
        elif stmt.keyword in ['notification']:
            data['operations'] = self._OPS_NOTIFICATION
        elif stmt.keyword in ['input']:
            data['operations'] = self._OPS_INPUT
        elif stmt.keyword in ['output']:
            data['operations'] = self._OPS_OUTPUT
        elif data['access'] == 'read-only':
            data['operations'] = self._OPS_READONLY
        else:
            data['operations'] = self._OPS_DEFAULT

        if tree:
            # Also update the module-level set of operations if needed.
            # The input and output operations are sub-operations of the
            # rpc operation and so are not applicable to the module as a whole.
            new_ops = (set(tree['data']['operations'])
                       .union(data['operations'])
                       .difference({'input', 'output'}))
            if new_ops != self.operations:
                tree['data']['operations'] = sorted(new_ops)

    def __unicode__(self):
        """Return YANG model name parsed by class."""
        return self.name


class TreeWalker(object):
    """Utility class used by ParseYang to walk the jstree."""

    def __init__(self, tree):
        """Save jstree.

        Args:
          tree (dict): contains dict created by ParseYang
        """
        self.tree = tree

    def _walk_child(self, child, **kwargs):
        """Descend through the provided subtree until the given node is found.

        Args:
          child (dict): jstree or subtree thereof
          xpath (str): XPath string to match on
          node_id (str): Node ID value to match on
          parents (list): List to populate with node IDs of nodes encountered
            en route to successfully locating the child.
        Returns:
          dict: node matching the requested xpath/node_id, or None
        """

        xpath = kwargs.get('xpath', '')
        node_id = int(kwargs.get('node_id', '0'))
        parents = kwargs.get('parents', [])
        no_prefix = kwargs.get('no_prefix', False)

        if xpath:
            if 'data' in child and 'xpath' in child['data']:
                if no_prefix:
                    ch_path = ''
                    for token in child['data']['xpath'].split('/'):
                        if token.count(':') == 1:
                            token = token.split(':')[1]
                        if token:
                            ch_path += '/' + token
                    if ch_path == xpath:
                        return child
                elif child['data']['xpath'] == xpath:
                    return child
        elif 'id' in child and child['id'] == node_id:
            return child

        if 'children' in child:
            for ch in child['children']:
                match = self._walk_child(ch, **kwargs)
                if match:
                    parents.append(ch['id'])
                    return match
        return None

    def _walk_tree(self, *args, **kwargs):
        return self._walk_child(self.tree, **kwargs)

    def get_node_by_xpath(self, xpath, **kwargs):
        """Walk the jstree and return node that matches the xpath.

        Args:
          xpath (str): Xpath of the node in the tree to match.
          parents (list): optional list object passed in to be populated
                          with the node IDs of the parents relating to the
                          node that matches the Xpath.

        Returns:
          dict: contains all the data specific to the node constructed
          by ParseYang.
        """

        # remove prefixes in xpath when no_prefix=True
        if kwargs.get('no_prefix', False):
            xpath_tokens = xpath.split("/")
            for i in range(len(xpath_tokens)):
                if xpath_tokens[i].count(':') == 1:
                    xpath_tokens[i] = xpath_tokens[i].split(':')[1]
            xpath = "/".join(xpath_tokens)

        node = self._walk_tree(xpath=xpath, **kwargs)
        parents = kwargs.get('parents', [])

        if parents:
            # first node ID in the list is the matched node so remove it
            parents.pop(0)

        return node

    def get_node_by_id(self, node_id, parents=[]):
        """Walk the jstree and return node that matches the xpath.

        Args:
          node_id (str, int): node ID of the node in the tree to match.
          parents (list): optional list object passed in to be populated
                          with the node IDs of the parents relating to the
                          node that matches the Xpath.

        Returns:
          dict: contains all the data specific to the node constructed
          by ParseYang.
        """
        node = self._walk_tree(node_id=node_id, parents=parents)

        if parents:
            # first node ID in the list is the matched node so remove it
            parents.pop(0)

        return node

    def get_dataset(self, child, items=[], *addons):
        """Return xpath plus optional add-ons.

        Args:
          child (dict): Root of jstree compiled by ParseYang (can be self.tree)
          items (list) or (set): Container to place results in.
          addons (tuple): Optional desired data

        Example usage:

        >>> from ysyangtree import YSContext, YSYangModels
        >>> ctx = YSContext.get_instance('admin', 'admin+miott-csr-no-mib')
        >>> models = YSYangModels(ctx, ['Cisco-IOS-XE-native'])
        >>> parser = models.yangs['Cisco-IOS-XE-native']
        >>> dataset = parser.tw.get_dataset(
        ...     parser.tw.tree, [], 'nodetype', 'datatype'
        ... )
        >>> dataset[0]
        ['/native', 'container', '']
        >>> dataset[1]
        ['/native/default', 'container', '']
        >>> dataset[2]
        ['/native/default/crypto', 'container', '']
        >>> dataset[3]
        ['/native/default/crypto/ikev2', 'container', '']
        >>> dataset[4]
        ['/native/default/crypto/ikev2/proposal', 'leaf', 'empty']
        >>>
        >>> dataset2 = parser.tw.get_dataset(
        ...     parser.tw.tree, set(), 'nodetype', 'datatype'
        ... )
        >>> dataset2.pop()
        ('/native/spanning-tree/ios-stp:extend', 'container', '')
        >>>

        Returns:
          (list): Multidimensional list or strings containing interesting data.
          (set): Set of tuples containing interesting data.
        """
        if child and 'data' in child and 'xpath' in child['data']:
            nodedata = [child['data']['xpath']]
            for item in addons:
                if item in child['data']:
                    nodedata.append(child['data'][item])
                else:
                    nodedata.append('')

            if hasattr(items, 'add'):
                # set cannot add lists so combine into a single string
                items.add(tuple(nodedata))
            else:
                items.append(nodedata)

        if 'children' in child:
            for ch in child['children']:
                self.get_dataset(ch, items, *addons)

        return items

    def get_dataset_using_key(self, node, key, items, xpath='', *addons):
        """Return xpath plus optional add-ons and submodule tag.

        Args:
          node (dict): Root of jstree compiled by ParseYang (can be self.tree)
          key (string): Key in the data node
          items (list) or (set): Container to place results in.
          xpath (xpath) : xpath for the data node
          addons (tuple): Optional desired data

        Example usage:

        >>> from ysyangtree import YSContext, YSYangModels
        >>> ctx = YSContext.get_instance('admin', 'admin+miott-csr-no-mib')
        >>> models = YSYangModels(ctx, ['Cisco-IOS-XE-logging'])
        >>> parser = models.yangs['Cisco-IOS-XE-']
        >>> dataset = parser.tw.get_dataset_using_key(
        ...     parser.tw.tree, 'name', [], '', 'module', 'nodetype'
        d)
        >>> dataset[0]
        ['/logging/discriminator/name',
          '',
          'Cisco-IOS-XE-logging',
          'leaf',
          'submodule']
        >>> dataset[1]
        ['/logging/discriminator/severity/drops',
         '',
         'Cisco-IOS-XE-logging',
         'leaf',
         'submodule']
        >>> dataset[2]
        ['/logging/discriminator/severity/includes',
         '',
         'Cisco-IOS-XE-logging',
         'leaf',
         'submodule']
        >>>

        Returns:
          (list): Multidimensional list or strings containing interesting data.
          (set): Set of tuples containing interesting data.
        """
        if node and 'data' in node and key in node['data']:
            data = node['data']
            if 'nodetype' in data and 'name' in data:
                if data['nodetype'] not in NON_DATA_NODETYPES:
                    xpath += '/' + data['name']
            nodedata = [xpath]

            for item in addons:
                if item in data:
                    nodedata.append(data[item])
                else:
                    nodedata.append('')
            nodedata.append('submodule')

            # Filter out xpaths from non-data nodetypes
            itemappend = True
            if 'nodetype' in data:
                if data['nodetype'] in NON_DATA_NODETYPES:
                    itemappend = False
                else:
                    if data['nodetype'] == 'container':
                        if 'presence' in data and data['presence'] != 'true':
                            itemappend = False
                        else:
                            if 'presence' not in data:
                                itemappend = False

            if itemappend:
                if hasattr(items, 'add'):
                    # set cannot add lists so combine into a single string
                    items.add(tuple(nodedata))
                else:
                    items.append(nodedata)

        if 'children' in node:
            for child in node['children']:
                self.get_dataset_using_key(child, key, items, xpath, *addons)

        return items
