# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Context for YANG model parsing and result streams."""
import os.path
from collections import defaultdict, deque
import pyang
from pyang import error as pyang_err

from . import ymodels
from yangsuite import get_logger
from yangsuite.paths import get_base_path
from ysfilemanager import (
    YSYangSet, name_and_revision_from_file, split_user_set,
)


parseyang = {}
log = get_logger(__name__)


def get_parse_yang(user):
    """Get the ParseYang instance associated with the given user.

    Args:
      user (str): Username to look up. TODO: rename to 'index' or 'key'
    Returns:
      ymodels.ParseYang: instance, or None
    """
    global parseyang
    psy = parseyang.get(user, {})
    return psy.get('parseyang', None)


def reset_parse_yang(yp, user):
    """Set the ParseYang instance associated with the given user.

    Args:
      yp (ymodels.ParseYang): Instance to set
      user (str): Username to set yp for. TODO: rename to 'index' or 'key'
    """
    if not isinstance(yp, ymodels.ParseYang):
        raise TypeError("Expected ParseYang instance, got {0}".format(yp))
    global parseyang
    psy = parseyang.get(user, {})
    psy['parseyang'] = yp
    parseyang[user] = psy


def get_result_stream(user):
    """Create or retrieve from cache a StringIO instance for the given user.

    Args:
      user (str): Key to locate/store the desired results stream.
        TODO: rename to 'index' or 'key'
    Returns:
      io.StringIO: Results stream object.
    """
    global parseyang
    psy = parseyang.get(user, {})
    results = psy.get('results', deque())
    psy['results'] = results
    parseyang[user] = psy
    return results


def set_result_stream(key, log):
    """Set result stream with your own logger.

    Args:
      key (str): Index to set result to.
      log (object):
        Class that provides results.
        Object must have these functions::

            __len__ : Returns length of result queue.
            popleft : Returns next message in queue to process.
            append  : Set new message at proper location in queue.
    """
    global parseyang
    psy = parseyang.get(key, {})
    psy['results'] = log
    parseyang[key] = psy


def reset_result_stream(user):
    """TODO: rename user to 'index' or 'key'."""
    global parseyang
    psy = parseyang.get(user, {})
    results = psy.get('results', None)
    if results is not None:
        psy['results'] = deque()
        parseyang[user] = psy


class YSContext(pyang.Context):
    """Extend pyang.Context with a few useful features.

    .. automethod:: __init__
    """

    _instances = {}

    @classmethod
    def get_instance(cls, ref, yangset=None):
        """Retrieve cached YSContext instance or create a new one.

        First call to this method instantiates a YSContext and caches it in
        shared storage using yangset name as the index.  The clients may not
        want to block it's execution waiting for it to finish building, thus,
        multiple calls for the same yangset context may occur and each client
        can begin to use the context when load status is set to "ready".

        Args:
          ref (object): Label identifying caller that will use the context.
          yangset (str): YANG set owner+name also used as index for storage in
                         the cache.

            1. if no cached context exists, create a new one and store it
               with a reference.

            2. if a cached context is available, but the associated yangset
               has changed, discard it from the cache and create a new one.

        Returns:
          YSContext: Cached YSContext, or None.

        Raises:
          ValueError: if 'yangset' is an improperly formed string
          OSError: if the requested YANG set doesn't exist
        """
        if not yangset:
            log.info("Using private context.")
            return cls.get_private_instance(ref)

        ctx = cls._instances.get(yangset, None)
        owner, setname = split_user_set(yangset)
        ys = YSYangSet.load(owner, setname)

        if ctx:

            repo = ctx.repository
            if not isinstance(repo, YSYangSet):
                # Not a yangset - how'd we get here?
                log.warning("Cached context for %s has a non-YSYangSet "
                            "repository?", yangset)
                cls.discard_instance(yangset, ref)
                ctx = None
            elif not ys == repo:   # YSYangSet may be missing __ne__ logic.
                log.info("Discarding cached context for %s due to change of "
                         "YANG set from %s to %s", yangset, repo, ys)
                cls.discard_instance(yangset, ref)
                ctx = None
            elif repo.is_stale:
                log.info("Discarding cached context for %s as its view of the "
                         "repository contents is stale", yangset)
                cls.discard_instance(yangset, ref)
                ctx = None
            else:
                ctx.reference.add(ref)
                log.debug("Cached ctx has same yangset")

        if not ctx:
            ctx = cls(ys, yangset, [], ref)
            assert ctx.ready

        return ctx

    @classmethod
    def get_private_instance(cls, key, yangset=None):
        """Retrieve cached YSContext instance or create a new one.

        First call to this method instantiates a YSContext and caches it in
        private storate using key as the index.  The clients may not
        want to block it's execution waiting for it to finish building, thus,
        multiple calls for the same yangset context may occur and each client
        can begin to use the context when load status is set to "ready".

        Args:
          key (str): index to private context
          yangset (str): YANG set owner+name.

            1. if no cached context exists, create a new one and store it
               at key index.

            2. if a cached context is available, but the associated yangset
               has changed, discard it from the cache and create a new one.

        Returns:
          YSContext: Cached YSContext, or None.
        """
        ctx = cls._instances.get(key, None)

        if not yangset:
            return ctx

        owner, setname = split_user_set(yangset)
        ys = YSYangSet.load(owner, setname)

        if ctx:
            repo = ctx.repository
            if not isinstance(repo, YSYangSet):
                # Not a yangset - how'd we get here?
                log.warning("Cached context for %s has a non-YSYangSet "
                            "repository?", yangset)
                cls.discard_instance(key)
                ctx = None
            elif not ys == repo:   # YSYangSet may be missing __ne__ logic.
                log.info("Discarding cached context for %s due to change of "
                         "YANG set from %s to %s", key, repo, ys)
                cls.discard_instance(key)
                ctx = None
            elif repo.is_stale:
                log.info("Discarding cached context for %s as its view of the "
                         "repository contents is stale", yangset)
                cls.discard_instance(key)
                ctx = None
            else:
                log.debug("Cached ctx has same key")

        if not ctx:
            ctx = cls(ys, key, [])
            assert ctx.ready

        return ctx

    @classmethod
    def discard_instance(cls, key, ref=None):
        """Forget about the given instance if all references have been removed.

        Args:
          key (str): index of YSContext to discard
          ref (object): Reference to shared context (optional)
        """
        log.info("Check cached context reference %s for %s", str(ref), key)
        ctx = cls._instances.get(key, None)
        if ctx:
            if ctx.reference and ref in ctx.reference:
                ctx.reference.remove(ref)
                log.info("Cached context dereferenced %s", str(ref))

                if len(ctx.reference) == 0:
                    cls._instances.pop(key, None)
                    log.info("Discarding context %s", key)
            else:
                cls._instances.pop(key, None)
                log.info("Discarding context %s", key)
        else:
            log.warning('Cached instance not found, key %s ref %s',
                        key, str(ref))

    def __init__(self, path_or_repo, key=None, modulenames=None, ref=None):
        """Instantiate and begin loading the module(s) from the repository.

        - If caller does not send a key, the context is not cached.
        - If caller sends a key but no ref, context is cached and first call
          to discard_reference with the correct key will remove the context.
        - If caller sends both key and ref, the context is considered shared
          and cannot be discarded until all references are removed.

        :meth:`get_instance` handles shared case.
        :meth:`get_private_instance` handles not shared case.
        :meth:`discard_instance` used for both shared and private.

        Caller responsible for calling :meth:`discard_instance`.

        Args:
          path_or_repo (str): Path to directory containing YANG files **OR**
            path to JSON file describing a YSYangSet **OR**
            an instance of pyang.Repository or subclass (including YSYangSet)
          key (str): Optional key to cache this YSContext for later use with
            :meth:`get_instance` (if ref is usedU :meth:`get_private_instance`
            (if no ref is used).
          modulenames (list): Name(s) of module(s) to load (along with their
            dependencies). If unspecified, the legacy behavior of loading
            all modules in the repository is preserved, but is not recommended
            due to memory usage concerns. To create a YSContext but defer
            loading any modules, pass an empty list for this parameter.
          ref (object): Optional reference to be used in conjunction with the
            key. The key is used to find the cached context and each ref added
            signifies an active user of the context, so, each call to
            :meth:`discard_instance` will remove the ref only until all ref
            have been removed, then discard the context.

        Raises:
          OSError: if path does not exist or is otherwise invalid.
        """
        if not path_or_repo:
            raise ValueError("must specify a path or a YSYangSet instance")
        log.info("Initializing context for path '%s'", path_or_repo)

        self.reference = set()

        if key:
            YSContext._instances[key] = self
            if ref:
                self.reference.add(ref)
                log.info("Context stored with reference '%s'", str(ref))
        else:
            log.info('Context not stored')

        self.load_status = {
            'ready': False,
            'count': 0,
            'total': 0,
            'info': 'initializing...'
        }
        if isinstance(path_or_repo, pyang.Repository):
            super(YSContext, self).__init__(path_or_repo)
        elif os.path.isdir(str(path_or_repo)):
            super(YSContext, self).__init__(
                pyang.FileRepository(str(path_or_repo), use_env=False))
        else:
            super(YSContext, self).__init__(
                YSYangSet.from_file(str(path_or_repo)))

        self.identities = {}
        """Dict mapping identity arg strings to corresponding Statements.

        Aggregate of the ``i_identities`` from each module loaded in this
        Context. Used to construct the :attr:`identities` dict once all
        modules have been loaded.
        """

        self.invalid_modules = []
        """List of modules that were found but failed loading altogether."""

        self.augmenters_of = {}
        """Dict mapping modules to list of modules that (may) augment it."""

        self.identity_derivers_of = {}
        """Dict: modules to list of modules that (may) derive identities."""

        self.submodules_of = {}
        """Dict: modules to list of submodules included in this module."""

        self.load_module_files(modulenames)
        # Done
        self.load_status['ready'] = True
        self.load_status['info'] = 'ready'
        if key:
            log.info("Context '%s' now fully loaded and ready", key)
        else:
            log.info("Context finished loading for '%s', now ready",
                     path_or_repo)

    def __str__(self):
        """String representation of a YSContext."""
        return "YSContext (repository {0}) with {1} modules loaded".format(
            self.repository, len(self.modules))

    @property
    def ready(self):
        """Test if YSContext finished loading all module files."""
        return self.load_status['ready']

    def get_module(self, modulename, revision=None):
        """Get the Statement corresponding to the given module.

        Args:
          modulename (str): Name of the module to request.
          revision (str): Specific revision to request. None or '' implies
            latest available revision.
        Returns:
          pyang.statements.Statement: or None if not found.
        """
        # Context.get_module doesn't recognize revision='' as synonymous
        # with revision=None, but we want to do so:
        if not revision:
            revision = None
        return super(YSContext, self).get_module(modulename, revision)

    def get_yang_parser(self, name, revision=None):
        """Create a ParseYang instance for the given module in this context.

        Args:
          name (str): YANG model name
          revision (str): YANG model revision, or None for latest available.
        Returns:
          ymodels.ParseYang: newly constructed instance.
        Raises:
          ValueError: see ParseYang.__init__()
        """
        return ymodels.ParseYang(name, revision, self)

    def load_module_files(self, modulenames=None):
        """Load and parse the given module(s) and dependencies.

        Args:
          modulenames (list): YANG model name(s). If omitted (i.e. ``None``),
            all modules in the repository will be loaded.
            An empty list means to load no additional modules at this time.
        """
        if modulenames is None:
            modules_to_load = set(name for name, _, _
                                  in self.repository.modules)
        elif len(modulenames) == 0:
            log.debug("No module loading requested.")
            return
        else:
            log.debug("Loading module(s) %s from repository %s",
                      modulenames, self.repository)
            if hasattr(self.repository, 'modules_using'):
                # Method on YSYangSet, but not on base pyang.Repository
                modules_to_load = set()
                for mn in modulenames:
                    modules_to_load |= self.repository.modules_using(mn)
                log.debug("Will load upstream modules as well: %s",
                          sorted(modules_to_load))
                modules_to_load |= set(modulenames)
            else:
                modules_to_load = set(modulenames)
        if len(modules_to_load) > 50:
            log.warning("Loading %d YANG modules. This may take some time "
                        "and consume significant amounts of system memory.",
                        len(modules_to_load))

        self.load_status['total'] = 0
        self.load_status['count'] = 0
        self._load_modules(modules_to_load)

        if hasattr(self.repository, 'modules_augmenting'):
            self.load_status['info'] = "Checking augmenters..."
            for mod, _ in self.modules:
                self.augmenters_of[mod] = \
                    self.repository.modules_augmenting(mod)

        if hasattr(self.repository, 'modules_deriving_identities_from'):
            self.load_status['info'] = "Checking identity derivation..."
            for mod, _ in self.modules:
                self.identity_derivers_of[mod] = \
                    self.repository.modules_deriving_identities_from(mod)
                if self.identity_derivers_of[mod]:
                    log.debug("Found identity derivers of %s: %s",
                              mod, self.identity_derivers_of[mod])

        # Additionally, load identity derivers of ALL modules loaded thus far
        # (but not augmenters) to make sure we have the full set of identities.
        extra_mods = set()
        for base, derivers in self.identity_derivers_of.items():
            extra_mods |= set(derivers)
        extra_mods -= set(modules_to_load)
        if extra_mods:
            log.debug("Found %d additional modules that derive identities: %s",
                      len(extra_mods), sorted(extra_mods))
            self._load_modules(extra_mods)

        for (name, _), module in self.modules.items():
            if module.i_including_modulename:
                if module.i_including_modulename not in self.submodules_of:
                    self.submodules_of[module.i_including_modulename] = []
                self.submodules_of[module.i_including_modulename].append(name)

        self.get_identity_bases()

    def _load_modules(self, module_list):
        """Helper to :meth:`load_module_files`.

        Actually load the given module list, without further evaluation.

        Args:
          module_list (list): List of module names to load, or None to load
            all available modules
        """
        if not module_list:
            return

        entries = self.repository.modules
        modules_to_load = set(module_list)
        self.load_status['total'] += len(modules_to_load)
        deviations = []
        modules_loading = []

        for entry in entries:
            # Each entry is something like:
            # ('yang-types', '20xx-mm-dd', '/path/to/yang-types.yang')
            (name, rev, handle) = entry
            if name not in modules_to_load:
                continue
            if 'deviation' in name:
                # Load deviations last
                deviations.append(entry)
            else:
                modules_loading.append(entry)

        for entry in modules_loading + deviations:
            (name, rev, handle) = entry
            if name not in modules_to_load:
                continue
            self.load_status['info'] = "parsing {0}...".format(name)

            # Calling get_module_from_handle() + add_module() *should*
            # be faster than calling search_module()
            ref, fmt, text = self.repository.get_module_from_handle(handle)
            module = self.add_module(ref, text, fmt, name, rev)

            if module is None:
                log.warning("Unable to load module %s due to "
                            "critical parsing errors", name)
                self.invalid_modules.append(name)
            else:
                log.debug("Successfully loaded %s", name)

            modules_to_load.remove(name)
            self.load_status['count'] += 1

        # Was any module just not seen at all?
        for name in sorted(modules_to_load):
            log.warning("Module %s not found in the repository", name)
            self.load_status['count'] += 1

        if (self.load_status['total'] !=
                self.load_status['count']):      # pragma: no cover
            log.warning("Possible internal error - count of modules processed "
                        "(%d) does not match expected total (%d)",
                        self.load_status['count'],
                        self.load_status['total'])

        log.debug("Have now loaded %d modules, of %d available in repository",
                  len(self.modules), len(self.repository.modules))
        self.load_status['info'] = "Module loading complete"

    def get_identity_bases(self):
        """Get the i_identities for all modules we have loaded.

        This function deals with built-in type "identityref"
        https://tools.ietf.org/html/rfc6020#section-9.10

        The identity statement can be defined in a YANG module and
        is used to create a global abstract entity. identityref is
        a pointer to the global entity.

        Where it gets tricky is the identity refers to a base and
        the base can be another base which then refers to another
        base and so on.  If you end up trying to configure an RPC,
        you need to have all the relevent information to form the
        XML tag.  The identity is sometimes defined in a different
        module than the identityref is defined.  That means you
        will need the namespace of that module.  The most notorious
        identity base is iana-interface-type defined iniana-if-type.

        Example RPC tag needed for ietf-interfaces module::

            <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">\
ianaift:ethernetCsmacd</type>

        This functon will extract the namespace prefix, and base from
        the pyang.statements.Statement structure and construct a python dict.
        ::

            {moduleone: {base1: [identity1, identity2],
                         base2: [identity3, identity4]},
             moduletwo: {base3: [identity5, identity6],
                         base4: [identity7, identity8]}}

        """
        self.load_status['info'] = "Checking identity bases..."
        for module in self.modules.values():
            if hasattr(module, 'i_identities'):
                bases = {}
                pfx = module.i_prefix
                mod = module.arg
                ref_mods = {}
                # Collect identityrefs from all modules first
                for idt_stmt in module.i_identities.values():
                    idt = idt_stmt.arg
                    base = idt_stmt.search_one('base')
                    if not base:
                        # No base so this is an identity not identityref
                        continue

                    while base:
                        if not base.i_identity:
                            break
                        # Could be base of a base of a base etc...
                        # Find the real base
                        bref = base.i_identity.search_one('base')
                        if bref:
                            # The base may already be in list of identityrefs.
                            # This happens so infrequent, instead of looping
                            # through all possible identities to find them
                            # ahead of time, just remove them from the list.
                            base_idt = base.i_module.i_prefix + ':' + base.arg
                            for mod, bases in ref_mods.items():
                                for base, idts in bases.items():
                                    if base_idt in idts:
                                        idts.remove(base_idt)
                            base = bref
                            continue
                        break

                    base_idt = base.arg
                    if ':' in base.arg:
                        base_pfx, base_idt = base.arg.split(':')
                        if base_pfx != idt_stmt.i_module.i_prefix:
                            # base should be in another module
                            if base_pfx in module.i_prefixes:
                                mod, _ = module.i_prefixes[base_pfx]
                            else:
                                log.error(
                                    "Identityref base module {0}:{1}".format(
                                        base_pfx, "some_module - not found."
                                    )
                                )

                    idt = pfx + ':' + idt

                    if mod not in ref_mods:
                        new_idt = set()
                        new_idt.add(idt)
                        ref_mods[mod] = {base_idt: new_idt}
                    elif base_idt not in ref_mods[mod]:
                        new_idt = set()
                        new_idt.add(idt)
                        ref_mods[mod][base_idt] = new_idt
                    else:
                        # Identity could have been removed earlier
                        ref_mods[mod][base_idt].add(idt)

                # Add refs to existing ones
                for mod, bases in ref_mods.items():
                    if mod in self.identities:
                        for base, idts in bases.items():
                            if base in self.identities[mod]:
                                self.identities[mod][base].update(idts)
                            else:
                                self.identities[mod][base] = idts
                    else:
                        self.identities[mod] = bases

    VALIDATE_RESULT_TEMPLATE = {
        'name': '',
        'revision': '',
        'found': False,
        'usable': False,
        'errors': None,
        'warnings': None,
    }

    PYANG_ERROR_LEVELS = {
        1: 'CRITICAL ERROR',
        2: 'MAJOR ERROR',
        3: 'MINOR ERROR',
        4: 'WARNING',
    }

    def validate(self):
        """Validate our loaded modules and report on the results.

        This function returns a list of dicts, where each dict represents
        the results of validating a single schema in the given path.
        We return this structure, instead of a dict of dicts, because in
        the future we may provide an iterative API. This API would allow us
        to report results for each schema as it is loaded and validated
        instead of as one monolithic block at the end.

        Each dict has the following structure::

            {
                name: 'ietf-interfaces',
                revision: '2014-05-08',
                found: True,
                usable: True,
                errors: ['error message', 'error message two'],
                warnings: None,
            }

        In case of a global error (such as invalid parameters passed to this
        function), the only entry will have empty name and revision strings.

        If a module is available in the yangset, 'found' will be True.
        If so, then if the module could be loaded, despite any errors
        or warnings, then the 'usable' key will also be True.
        Otherwise these keys will be False.

        Returns:
          list: List of dicts, each describing a schema and its result.
          Sorted by module name and then by revision.
        """
        # Dict of name -> revision -> results
        # Before we're done, we'll transform this into a flat list of results
        schemas = defaultdict(lambda: defaultdict(dict))

        # self.modules has the set of modules that were parsed at least
        # somewhat successfully, while self.invalid_modules has the names
        # that failed parsing and aborted.
        # self.errors includes errors for missing dependencies - include those
        # Note that our repository may have multiple sources for a given
        # module.

        for entry in self.repository.get_modules_and_revisions(self):
            name, rev, path = entry
            if (name, rev) in self.modules or name in self.invalid_modules:
                if schemas[name][rev]:
                    # We shouldn't encounter this case
                    log.warning("Multiple sources exist for %s", (name, rev))
                    # Take the best 'usable' value
                    schemas[name][rev]['usable'] |= (
                        (name, rev) in self.modules)
                else:
                    schemas[name][rev]['usable'] = (
                        (name, rev) in self.modules)
                schemas[name][rev]['found'] = True
            else:
                # Since we load all available modules at present (TODO!),
                # a module that neither loaded successfully nor failed to load
                # is an indication something is wrong.
                log.error("Module %s@%s appears not to have been parsed "
                          "despite being a member of repository %s",
                          name, rev, self.repository)

        for error in self.errors:
            epos, reason, args = error
            if reason == 'MODULE_NOT_FOUND':
                name = str(args)
                rev = 'unknown'
            elif reason == "MODULE_NOT_FOUND_REV":
                name = str(args[0])
                rev = str(args[1])
            else:
                continue
            if schemas[name][rev] and schemas[name][rev]['found']:
                log.error('Got a "%s" error for (%s, %s) but already have a'
                          ' previous "found" entry: %s',
                          name, rev, schemas[name][rev])
            schemas[name][rev]['found'] = False
            schemas[name][rev]['usable'] = False

        # Each entry in self.errors consists of:
        # 1) a pyang.error.Position object specifying where the error happened
        # 2) a string tag representing the error type
        # 3) A tuple of additional args associated with this error
        #
        # Here we remap flat list of self.errors into a dict[dict[dict[list]]],
        # indexed by module name, then by revision, then by line number.
        # Each entry is a list because one line can report several errors.
        ctx_errors = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(list)))
        base_path = get_base_path()
        for error in self.errors:
            epos, reason, args = error

            # Within the Position, epos.ref gives the file path, but what we
            # prefer is the module name being parsed, which is in epos.top.arg.
            # For certain egregious errors this may not be available, in which
            # case we can fall back to guessing the module from the filename.
            #
            # The Position never directly states the revision, so, if we are
            # lucky enough to only have one revision for this module,
            # we use that, otherwise we just guess it from the filename.

            name = None
            revision = None

            if epos.top and epos.top.arg in schemas:
                name = epos.top.arg
                if len(schemas[name]) == 1:
                    revision = list(schemas[name].keys())[0]

            if not name or not revision:
                _name, _revision = name_and_revision_from_file(
                    epos.ref, assume_correct_name=False)

                if not name:
                    # Either pyang couldn't determine the name, or the name
                    # that pyang determined was different than the name that
                    # our repository thinks. Either way, fall back to the
                    # module name guessed by quickparser.
                    name = _name

                if not revision:
                    revision = _revision

            if args and isinstance(args, tuple):
                # Don't leak information about the system base path
                args = tuple(arg.replace(base_path, '...')
                             if isinstance(arg, str) else arg
                             for arg in args)

            line = int(epos.line)
            level = pyang_err.err_level(reason)
            err_string = "{tag} line {line}: {msg}".format(
                tag=self.PYANG_ERROR_LEVELS[level], line=line,
                msg=pyang_err.err_to_str(reason, args))
            ctx_errors[name][revision][line].append([level, err_string])

        # Successful schemas won't appear in ctx_errors, but if we have errors
        # for modules or revisions we don't know of, we need to report on that!
        missing_schemas = set(ctx_errors.keys()) - set(schemas.keys())
        if missing_schemas:
            log.warning("pyang reported errors for the following modules "
                        "that were not known to our repository: %s",
                        missing_schemas)

        for name in ctx_errors.keys():
            missing_revisions = (set(ctx_errors[name].keys()) -
                                 set(schemas[name].keys()))
            if missing_revisions:
                log.warning("pyang reported errors for revisions of module %s "
                            "that were not known to our repository: %s",
                            name, missing_revisions)

        # Now, use the schemas plus the errors to construct the result list
        results = []
        for name in sorted(schemas.keys()):
            for rev in sorted(schemas[name].keys()):
                status = schemas[name][rev]
                result = self.VALIDATE_RESULT_TEMPLATE.copy()
                result['name'] = name
                result['revision'] = rev
                result['usable'] = status['usable']
                result['found'] = status['found']
                for line in sorted(ctx_errors[name][rev].keys()):
                    for level, err_string in ctx_errors[name][rev][line]:
                        # How severe of an issue is this?
                        # Pyang defines levels 1 through 4 from CRITICAL ERROR
                        # down to WARNING - we map the first two levels as
                        # 'errors' and the latter two as 'warnings'
                        # in our result structure
                        if level <= 2:
                            if result['errors'] is None:
                                result['errors'] = []
                            result['errors'].append(err_string)
                        else:
                            if result['warnings'] is None:
                                result['warnings'] = []
                            result['warnings'].append(err_string)

                results.append(result)

        return results
