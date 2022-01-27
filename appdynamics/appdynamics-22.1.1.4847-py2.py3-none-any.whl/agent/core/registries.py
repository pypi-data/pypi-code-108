# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Registries store information about the agent's state and configuration.

"""

from __future__ import unicode_literals
from appdynamics.agent.core.method_data_gatherer import MethodDataGatherer

from collections import namedtuple
from appdynamics.agent.interceptor.utils.MIDC_utils import patch_method_to_report_data, reset_patch

from appdynamics.lang import items, str
from appdynamics.lib import MissingConfigException, normalize_header

from appdynamics.agent.core import conditions, expressions, naming, pb
from appdynamics.agent.core.logs import setup_logger
from appdynamics.agent.models import errors, exitcalls
from appdynamics.config import BT_NAME_MAX_SIZE

logger = setup_logger('appdynamics.agent')


class TransactionRegistry(object):
    """Track transactions that have been discovered, configured, and excluded.

    """

    def __init__(self):
        super(TransactionRegistry, self).__init__()
        self.registered_bts = {}
        self.excluded_bts = set()

    def get_registered_id(self, entry_type, name):
        """Return the id for the named BT if it has been registered.

        Parameters
        ----------
        entry_type : int
            The entry point type for the BT, one of the ENTRY_xxx constants
            defined in :py:mod:`appdynamics.agent.models.transactions`.
        name : str
            The name of the BT.

        Returns
        -------
        id : long or None
            The id registered with the named BT, if any. If the BT has not been
            registered, then `None`.

        """
        return self.registered_bts.get((entry_type, name))

    def is_excluded(self, entry_type, name):
        """Return true if the named BT is excluded in the latest configuration.

        Parameters
        ----------
        entry_type : int
            The entry point type for the BT, one of the ENTRY_xxx constants
            defined in :py:mod:`appdynamics.agent.models.transactions`.
        name : str
            The name of the BT.
        """
        return (entry_type, name) in self.excluded_bts

    def update_config(self, tx_info):
        """Update the registry from configuration.

        Parameters
        ----------
        tx_info : appdynamics.agent.pb.TransactionInfo
            The transaction info from a `ConfigResponse`.

        """
        self.registered_bts = {}
        self.excluded_bts = set()

        for registered_bt in tx_info.registeredBTs:
            if registered_bt.btInfo.internalName and registered_bt.id:
                bt_info = registered_bt.btInfo
                key = (bt_info.entryPointType, str(bt_info.internalName))
                self.registered_bts[key] = registered_bt.id

        for excluded_bt in tx_info.blackListedAndExcludedBTs:
            if excluded_bt.internalName:
                key = (excluded_bt.entryPointType, str(excluded_bt.internalName))
                self.excluded_bts.add(key)


class BackendRegistry(object):
    """Track backends that have been registered.

    """
    __slots__ = (
        'backends',
        'registered_backends',
        'backend_to_component',
        'detection_config',
        'resolved_to_unresolved_backends'
    )

    URL_PROPERTY_MAX_LEN = 100
    HOST_PROPERTY_MAX_LEN = 50
    DB_NAME_PROPERTY_MAX_LEN = 50
    VENDOR_PROPERTY_MAX_LEN = 50
    db_backend_naming_format_string = '{HOST}:{PORT} - {DATABASE} - {VENDOR} - {VERSION}'

    subtype_to_config_definition = {
        exitcalls.EXIT_SUBTYPE_HTTP: 'http',
        exitcalls.EXIT_SUBTYPE_DB: 'db',
        exitcalls.EXIT_SUBTYPE_CACHE: 'cache',
        exitcalls.EXIT_SUBTYPE_MONGODB: 'mongodb'
    }

    property_to_config_field_name = {
        'HOST': 'host',
        'PORT': 'port',
        'URL': 'url',
        'DATABASE': 'database',
        'VERSION': 'version',
        'VENDOR': 'vendor',
        'SERVER POOL': 'serverPool',
        'QUERY STRING': 'queryString',
        'ROUTING KEY': 'routingKey',
        'EXCHANGE': 'exchange',
    }

    def __init__(self):
        super(BackendRegistry, self).__init__()
        self.detection_config = None
        self.backends = {}
        self.registered_backends = {}
        self.backend_to_component = {}
        self.resolved_to_unresolved_backends = set()

    @staticmethod
    def backend_hash(exit_call_type, exit_call_subtype, properties):
        """Return a unique identifier for this backend.

        Parameters
        ----------
        exit_call_type : exitcalls.EXIT_DB, exitcalls.EXIT_HTTP, etc...
            The type of the exit call being made.
        properties : dict
            A dict representing the backend properties.

        """
        return exit_call_type, exit_call_subtype, tuple(sorted(items(properties)))

    def get_backend_config(self, type):
        """Return the backend config for this exit call type.

        """
        return getattr(self.detection_config, '%sBackendConfig' % type)

    @staticmethod
    def get_match_rule(type, config_entry):
        """Return the match rule for this exit point type from the config.

        """
        return getattr(config_entry.matchRule, '%sMatchRule' % type)

    @staticmethod
    def get_naming_rule(type, config_entry):
        """Return the naming rule for this exit point type from the config.

        """
        return getattr(config_entry.namingRule, '%sNamingRule' % type)

    def get_backend(self, exit_call_type, exit_call_subtype, backend_properties, format_string):
        """Get a backend from its type and properties.

        After a config update, every unique backend has identifying properties
        re-generated based on the naming config.  If there is a registered
        backend which matches the generated identifying properties, it is
        returned.  Otherwise a new backend is created.

        Parameters
        ----------
        exit_call_type : exitcalls.EXIT_DB, exitcalls.EXIT_HTTP, etc...
            The type of the exit call being made.
        backend_properties : dict
            A dict of strings representing all the supported properties for a
            backend of the given exit call type.
        format_string : str
            A string defining the format of the backend name.  This is a
            simplified version of the 'Format String Syntax' as described
            in PEP-3101.  See exitcalls.BackendNamer for more details.

        Returns
        -------
        backend : exitcalls.Backend
            The backend. If no backend has been added to the registry of the
            specified type with the given identifying properties, a new
            backend is created and added to the registry.

        See Also
        --------
        get_db_backend

        """

        if self.detection_config is None:
            raise MissingConfigException

        backend_hash = self.backend_hash(exit_call_type, exit_call_subtype, backend_properties)
        try:
            backend = self.backends[backend_hash]
        except KeyError:
            backend_type = self.subtype_to_config_definition[exit_call_subtype]
            for entry in self.get_backend_config(backend_type):
                # If the discovery rule doesn't have a matchRule, name the
                # backend immediately.  Otherwise, use the first matched rule.
                if not entry.HasField('matchRule') or \
                        self.match_backend(backend_properties, self.get_match_rule(backend_type, entry)):

                    naming_rule = self.get_naming_rule(backend_type, entry)
                    identifying_properties = self.generate_identifying_properties(backend_properties, naming_rule,
                                                                                  entry.name)

                    try:
                        backend = self.registered_backends[self.backend_hash(exit_call_type, exit_call_subtype,
                                                                             identifying_properties)]
                    except KeyError:
                        # If the config entry has a match rule, is is a custom
                        # defined backend naming rule.
                        if entry.HasField('matchRule'):
                            prefix = entry.name
                        else:
                            prefix = None

                        display_name = exitcalls.BackendNamer().format(format_string, identifying_properties,
                                                                       custom_backend_prefix=prefix)
                        backend = exitcalls.Backend(exit_call_type, exit_call_subtype, identifying_properties,
                                                    display_name)

                    backend.correlation_enabled = entry.correlationEnabled
                    break
            else:
                # No rules matched the backend properties.
                backend = None

            self.backends[backend_hash] = backend
        return backend

    def get_api_backend(self, exit_call_type, exit_call_subtype, identifying_properties, display_name):
        """Get a backend from its type and identifying properties.

        This function is for use only by the agent API.  It does not perform
        any backend naming.  It uses the supplied identifying properties as-is.

        Parameters
        ----------
        exit_call_type : exitcalls.EXIT_DB, exitcalls.EXIT_HTTP, etc...
            The type of the exit call being made.
        identifying_properties : dict
            A dict of strings that uniquely identifies this backend.
        display_name : str
            The display name of this backend in the controller UI.

        Returns
        -------
        backend : exitcalls.Backend
            The backend. If no backend has been added to the registry of the
            specified type with the given identifying properties, a new
            backend is created and added to the registry.

        """

        # Properties get converted to `str` when sending them to the controller.
        # However, if we don't convert them here, we never match registered backends.
        identifying_properties = dict((str(k), str(v)) for k, v in items(identifying_properties))
        backend_hash = self.backend_hash(exit_call_type, exit_call_subtype, identifying_properties)
        try:
            backend = self.registered_backends[backend_hash]
        except KeyError:
            backend = exitcalls.Backend(exit_call_type, exit_call_subtype, identifying_properties, display_name)
            # Although this is not a registered backend, there is no distiction
            # since we do not alter the identifying properties.  We use the
            # registered backends cache as an optimization.
            self.registered_backends[backend_hash] = backend

        return backend

    def match_backend(self, backend_properties, match_rule):
        """Return True if the backend properties match the rule.

        """
        for key in backend_properties:
            field_name = self.property_to_config_field_name[key]
            if (match_rule.HasField(field_name) and
                    not conditions.match(str(backend_properties[key]), getattr(match_rule, field_name))):
                return False
        return True

    def generate_identifying_properties(self, backend_properties, naming_rule, rule_name):
        """Return identifying properties for this backend based on the rule.

        """
        identifying_properties = {}
        for key in backend_properties:
            field_name = self.property_to_config_field_name[key]
            value = expressions.evaluate(getattr(naming_rule, field_name), backend_properties)
            # Empty strings aren't valid identifying property values.
            if value:
                identifying_properties[key] = str(value)

        # CORE-51608 Empty identifying properties shouldn't be empty.
        if len(identifying_properties) == 0:
            identifying_properties['Configuration Name'] = rule_name

        return identifying_properties

    def get_component_for_registered_backend(self, backend_id):
        return self.backend_to_component.get(backend_id)

    def update_config(self, backend_info, backend_detection_config):
        """Update the registry with information from configuration.

        Parameters
        ----------
        backend_info : appdynamics.agent.pb.BackendInfo
            The backend info configuration from a
            :py:class:`appdynamics.agent.pb.ConfigResponse`.
        backend_detection_config : appdynamics.agent.pb.BackendConfig
            The backend detection configuration from a
            :py:class:`appdynamics.agent.pb.ConfigResponse`.

        """
        self.backends = {}
        self.registered_backends = {}
        self.resolved_to_unresolved_backends = set()
        self.detection_config = backend_detection_config.pythonDefinition

        for rb in backend_info.registeredBackends:
            backend_config = rb.registeredBackend
            exit_point_type = backend_config.exitPointType

            exit_call_info = rb.exitCallInfo
            identifying_properties = dict((p.name, p.value) for p in exit_call_info.identifyingProperties)
            exit_point_subtype = exit_call_info.exitPointSubtype

            backend = exitcalls.Backend(exit_point_type, exit_point_subtype, identifying_properties,
                                        exit_call_info.displayName)

            backend.registered_id = backend_config.backendID
            backend.component_id = backend_config.componentID
            backend.is_foreign_app = backend_config.componentIsForeignAppID

            self.registered_backends[
                self.backend_hash(exit_point_type, exit_point_subtype, identifying_properties)] = backend

            if backend.component_id and not backend.is_foreign_app:
                self.backend_to_component[backend.registered_id] = backend.component_id

        """
        Proxy sends backendId of all service proxy in backend_info.resolvedBackendsToBeUnresolved
        We store that backendID in our class variable which can be checked by upstream server while
        creating the correlation header for downstream server and based on that it will set
        do_not_resolve = True in base.py -> ExitCallInterceptor::make_correlation_header()
        """
        if len(backend_info.resolvedBackendsToBeUnresolved) > 0:
            logger.debug("Total service Proxy found: %d", len(backend_info.resolvedBackendsToBeUnresolved))
        for service_proxy in backend_info.resolvedBackendsToBeUnresolved:
            self.resolved_to_unresolved_backends.add(service_proxy.backendID)


class TransactionNamingMatch(object):
    """A match found by the :py:class:`NamingSchemeRegistry`.

    Instances of this object will have a `name` field set to a non-empty
    string, and then either one of its `custom_match_id` or `naming_scheme`
    attributes (but never both) set.

    Parameters
    ----------
    name : str
        The generated name of the BT.
    custom_match_id : int or None
        If the naming match occurred against a custom match rule, then the id
        of that rule is set on the match. If no custom match rule was matched,
        then `None` is set for this attribute.
    naming_scheme : str or None
        If the naming match occurred through discovery (instead of a custom
        match rule), then the naming scheme used for generating the BT's name
        is set on the match. If the BT matched a custom match rule, then
        `None` is set for this attribute.

    """
    __slots__ = ('name', 'custom_match_id', 'naming_scheme')

    def __init__(self, name, custom_match_id=None, naming_scheme=None):
        super(TransactionNamingMatch, self).__init__()

        if custom_match_id is naming_scheme or (custom_match_id is not None and naming_scheme):
            raise ValueError('a naming match must have either a custom_match_id or a naming_scheme (but not both)')

        # This makes using external APIs safe as the discovered names can be really long.
        self.name = name[:BT_NAME_MAX_SIZE]
        self.custom_match_id = custom_match_id
        self.naming_scheme = naming_scheme


EntryPointConfig = namedtuple('EntryPointConfig', ('naming_scheme', 'exclude_rules', 'custom_match_rules'))


class NamingSchemeRegistry(object):
    """Registry of configured naming schemes.

    """

    ENTRY_TYPES = {
        'pythonWeb': 'http',
    }

    def __init__(self):
        super(NamingSchemeRegistry, self).__init__()
        self.entry_point_configs = {}

    def match(self, entry_type, request, base_name=None):
        """Match a BT to its naming configuration and generate its name.

        This may return `None` if any of the following hold for the given
        entry type:

        1. There is no configuration, or
        2. BT reporting is disabled, or
        3. The BT does not match any custom match rules and either (a) BT
           discovery is disabled or (b) the BT matches an exclusion rule.

        Parameters
        ----------
        entry_type : int
            One of the ENTRY_xxx constants defined in
            :py:mod:`appdynamics.agent.models.transactions`.
        request : request object
            A request object that has the attributes `method`, `path`,
            `headers`, `args` (the query parameters), and `cookies`.

        Other Parameters
        ----------------
        base_name : str, optional
            If set to a non-empty string, this will be used for a discovered
            name's prefix instead of the prefix specified by the naming
            scheme.

        Returns
        -------
        match : (name, custom_match_id, naming_scheme) or None
            If the BT matches the discovery or custom match rule config of
            this registry, a `TransactionNamingMatch` named tuple is returned.
            If the BT is excluded (either explicitly or because discovery is
            disabled and no custom rule matches), or if there is no naming
            configuration for the given entry point, then `None` is returned,
            and no BT will be reported.

        """
        entry_type_name = pb.EntryPointType.Name(entry_type)
        entry_point_config = self.entry_point_configs.get(entry_type)

        if not entry_point_config:
            logger.debug('Skipping BT: entry point %s is disabled/unconfigured.', entry_type_name)
            return None

        for rule in entry_point_config['custom_definitions']:
            if conditions.match_http(request, rule['condition']):
                custom_naming_scheme = dict([(prop.name, prop.value) for prop in rule['condition'].properties])
                custom_bt_name = naming.get_http_bt_name(custom_naming_scheme, request, rule['name'], custom=True)
                match = TransactionNamingMatch(name=custom_bt_name, custom_match_id=rule['id'])
                return match

        if not entry_point_config['discovery_enabled']:
            logger.debug('Skipping BT: entry point %s, no custom match and discovery is disabled')
            return None  # Discovery disabled and no custom match rules matched.

        for rule in entry_point_config['exclude_rules']:
            if conditions.match_http(request, rule):
                logger.debug('Skipping BT: bt matched an exclude rule')
                return None  # Matched an exclusion rule

        # At this point, we need to generate a discovered name according to
        # the naming scheme for this type of BT.
        naming_scheme = entry_point_config['naming_scheme']
        name = naming.get_http_bt_name(naming_scheme['properties'], request, base_name)
        return TransactionNamingMatch(name=name, naming_scheme=naming_scheme['type'])

    def update_config(self, tx_config):
        """Update the naming configuration for transactions and backends.

        Parameters
        ----------
        tx_config : appdynamics.agent.pb.TransactionConfig
            The transaction naming configuration from a
            :py:class:`appdynamics.agent.pb.ConfigResponse`.

        """
        self.entry_point_configs = {}

        for field_name, entry_point_match_name in items(self.ENTRY_TYPES):
            pt_config = getattr(tx_config, field_name)

            if not pt_config.IsInitialized() or not pt_config.enabled:
                continue  # No config, or entry point is disabled

            entry_type = pt_config.entryPointType

            # Extract custom match rules.
            custom_definitions = []

            for rule in pt_config.customDefinitions:
                custom_definitions.append({
                    'id': rule.id,
                    'name': rule.btName,
                    'priority': rule.priority,
                    'condition': getattr(rule.condition, entry_point_match_name),
                })

            custom_definitions.sort(key=lambda r: r['priority'], reverse=True)

            discovery_config = pt_config.discoveryConfig
            exclude_rules = []
            naming_scheme = None

            if discovery_config.enabled:
                properties = dict((p.name, p.value) for p in discovery_config.namingScheme.properties)

                # Headers are case insensitive, so lowercase them so that we have consistent casing.
                if properties.get('uri-suffix-scheme') == 'header-value':
                    properties['suffix-key'] = properties.get('suffix-key', '').lower()

                naming_scheme = {
                    'type': discovery_config.namingScheme.type,
                    'properties': properties,
                }

                for rule in discovery_config.excludes:
                    exclude_rules.append(getattr(rule, entry_point_match_name))

            self.entry_point_configs[entry_type] = {
                'custom_definitions': custom_definitions,
                'discovery_enabled': discovery_config.enabled,
                'naming_scheme': naming_scheme,
                'exclude_rules': exclude_rules,
            }


class ErrorConfigRegistry(object):
    """Contains configuration of ignored errors/exceptions.

    """
    WILDCARD_PATTERN = '*'

    def __init__(self):
        super(ErrorConfigRegistry, self).__init__()
        self.error_threshold = errors.PY_ERROR
        self.should_detect_logged_errors = True
        self.logged_errors_should_cause_error_transaction = True
        self.ignored_exceptions = []
        self.ignored_messages = []
        self.http_status_codes = []

    def is_bt_error(self, has_logged_errors=False, exception=None):
        """Return True if the BT should be marked as error.

        Parameters
        ----------
        has_logged_errors : bool
            True if the BT has logged errors associated with iterator.
        exception : errors.ExceptionInfo
            An exception which may cause this BT to be marked as error.
        """
        if has_logged_errors and self.logged_errors_should_cause_error_transaction:
            return True
        if exception and not self.is_exception_ignored(exception):
            return True
        return False

    def is_exception_ignored(self, exc):
        """Returns true if this exception is ignored for error reporting.

        IMPORTANT NOTE: Ignored exceptions are still reported as part of the
        BT and backend. Ignoring an exception controls whether the exception
        flags the BT as having an error. This is confusing, but that's the
        terminology already used everywhere else.

        Parameters
        ----------
        exc : errors.ExceptionInfo

        Returns
        -------
        ignored : bool
            True if the ignored exception configuration in this registry
            specifies that the exception should be ignored.

        """
        return any(_match_exception(exc, rule) for rule in self.ignored_exceptions)

    def update_config(self, error_config):
        if error_config.HasField('errorDetection'):
            detection = error_config.errorDetection

            self.should_detect_logged_errors = bool(detection.detectErrors)
            self.logged_errors_should_cause_error_transaction = bool(self.should_detect_logged_errors and
                                                                     detection.markTransactionAsError)

            if detection.HasField('pythonErrorThreshold'):
                self.error_threshold = detection.pythonErrorThreshold

        self.ignored_exceptions = []
        for exc in error_config.ignoredExceptions:
            class_name = exc.classNames[0] if exc.classNames else self.WILDCARD_PATTERN
            class_name = class_name or self.WILDCARD_PATTERN
            match_condition = exc.matchCondition if exc.HasField('matchCondition') else None

            if class_name or match_condition:
                self.ignored_exceptions.append((class_name, match_condition))

        self.ignored_messages = []
        for err in error_config.ignoredMessages:
            if err.HasField('matchCondition'):
                self.ignored_messages.append(err.matchCondition)

        self.http_status_codes = error_config.httpStatusCodes


def _match_exception(exc, rule):
    ignored_name, match_condition = rule
    name_matches = False

    if ignored_name == ErrorConfigRegistry.WILDCARD_PATTERN:
        name_matches = True
    else:
        if ignored_name.startswith('exceptions.') and '.' not in exc.klass:
            # The builtin exceptions can be matched qualified or unqualified.
            # That is, "ValueError" matches "exceptions.ValueError" as well as
            # "ValueError". (This is because the builtins are defined in the
            # exceptions module in Python 2, so either way someone attempts to
            # match them should work.)
            options = (ignored_name, ignored_name[11:])
        else:
            options = (ignored_name,)

        for check in options:
            if exc.klass == check:
                name_matches = True
                break

    return name_matches and (
        match_condition is None or
        conditions.match(str(exc.message), match_condition) or
        conditions.match(str(exc.klass), match_condition)
    )


class DataGathererRegistry(object):
    """Data gatherers for snapshotting and analytics.

    Note: Type format of HttpDataGatherer namedTuple
    - cookies: (key, enabled_for_apm, enabled_for_analytics)
    - headers: (key, enabled_for_apm, enabled_for_analytics)
    - request_params: ((name, display_name), enabled_for_apm, enabled_for_analytics)
    """

    HttpDataGatherer = namedtuple('HttpDataGatherer', ('cookies', 'headers', 'request_params'))
    MethodInfo = namedtuple('MethodInfo', ('module', 'cls', 'method'))

    def __init__(self):
        super(DataGathererRegistry, self).__init__()
        # http_data_gatherers will be a map from data gatherer id tuple to data gatherer config
        self.http_data_gatherers = {}
        # method_data_gatherers will be a map from a MethodInfo tuple to array of MethodDataGatherer objects
        self.method_data_gatherers = {}
        self.data_gatherer_bt_entries = {}
        self.bt_http_gatherer_cache = {}

    def update_data_gatherers(self, data_gatherers):
        self.bt_http_gatherer_cache = {}
        self.http_data_gatherers = {}
        # Reset all the instrumentation to make sure that any method removed from
        # MIDC config by the user gets unpatched
        self.reset_method_data_gatherer_instrumentation()

        for dg in data_gatherers:
            if dg.type == pb.DataGatherer.HTTP and dg.HasField('httpDataGathererConfig'):
                self.http_data_gatherers[dg.gathererID] = dg.httpDataGathererConfig
            elif dg.type == pb.DataGatherer.METHOD and dg.HasField('methodDataGathererConfig'):
                method_data_gatherer_config = MethodDataGatherer(dg.methodDataGathererConfig,
                                                                 dg.gathererID)
                method_info = self.MethodInfo(method_data_gatherer_config.module,
                                              method_data_gatherer_config.cls,
                                              method_data_gatherer_config.method)
                if method_info not in self.method_data_gatherers:
                    self.method_data_gatherers[method_info] = [method_data_gatherer_config]
                else:
                    self.method_data_gatherers[method_info].append(method_data_gatherer_config)

        self.instrument_data_gatherer_methods()

    def reset_method_data_gatherer_instrumentation(self):
        for method_info, _ in items(self.method_data_gatherers):
            reset_patch(method_info)
        self.method_data_gatherers.clear()

    def instrument_data_gatherer_methods(self):
        for method_info, method_data_gatherers in items(self.method_data_gatherers):
            patch_method_to_report_data(method_info, method_data_gatherers)

    def update_data_gatherer_bt_entries(self, data_gatherer_bt_entries):
        self.bt_http_gatherer_cache = {}
        self.data_gatherer_bt_entries = {}

        for entry in data_gatherer_bt_entries:
            self.data_gatherer_bt_entries[entry.btID] = list(entry.gathererIDs)

    def get_http_data_gatherer(self, bt_id):
        try:
            return self.bt_http_gatherer_cache[bt_id]
        except KeyError:
            cookies = set()
            headers = set()
            request_params = set()

            for gatherer_id in self.data_gatherer_bt_entries.get(bt_id, ()):
                try:
                    http_gatherer = self.http_data_gatherers[gatherer_id]
                    for cookie_name in http_gatherer.cookieNames:
                        cookies.add((cookie_name,
                                     http_gatherer.enabledForApm,
                                     http_gatherer.enabledForAnalytics))

                    for header_name in http_gatherer.headers:
                        headers.add((normalize_header(header_name),
                                     http_gatherer.enabledForApm,
                                     http_gatherer.enabledForAnalytics))

                    for request_param in http_gatherer.requestParams:
                        request_params.add(((request_param.name, request_param.displayName),
                                            http_gatherer.enabledForApm,
                                            http_gatherer.enabledForAnalytics))
                except KeyError:
                    pass

            if not cookies and not headers and not request_params:
                gatherer = None
            else:
                gatherer = self.HttpDataGatherer(cookies=cookies, headers=headers, request_params=request_params)

            self.bt_http_gatherer_cache[bt_id] = gatherer
            return gatherer


class AnalyticsConfigRegistry(object):
    """Contains configuration for Analytics Service.

    """
    def __init__(self):
        super(AnalyticsConfigRegistry, self).__init__()
        self._enabled = False
        self.analytics_bt_ids = set()

    def update_config(self, analytics_config):
        if analytics_config.HasField('isEnabled'):
            self._enabled = analytics_config.isEnabled

        self.analytics_bt_ids.clear()
        for bt_id in analytics_config.analyticsBTIDs:
            self.analytics_bt_ids.add(bt_id)

    @property
    def enabled(self):
        return self._enabled

    def get_analytics_bt_ids(self):
        return self.analytics_bt_ids
