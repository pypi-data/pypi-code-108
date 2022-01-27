# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Model calls made from the instrumented application to an external service.

"""

from __future__ import unicode_literals
from string import Formatter

from appdynamics.lang import bytes, items, values, str
from appdynamics.lib import make_name_value_pairs
from appdynamics.agent.core import pb
from appdynamics import config


EXIT_DB = pb.EXIT_DB
EXIT_HTTP = pb.EXIT_HTTP
EXIT_CACHE = pb.EXIT_CACHE
EXIT_QUEUE = pb.EXIT_RABBITMQ
EXIT_CUSTOM = pb.EXIT_CUSTOM

EXIT_SUBTYPE_DB = 'DB'
EXIT_SUBTYPE_HTTP = 'HTTP'
EXIT_SUBTYPE_CACHE = 'CACHE'
EXIT_SUBTYPE_QUEUE = 'RABBITMQ'
EXIT_SUBTYPE_MONGODB = 'Mongo DB'


def exit_point_type_name(exit_point_type):
    return pb.ExitPointType.Name(exit_point_type).replace('EXIT_', '')


class Backend(object):
    """A backend is the destination of an exit call.

    Parameters
    ----------
    exit_point_type : {EXIT_DB, EXIT_HTTP, EXIT_CACHE, EXIT_QUEUE}
        The type of the backend.
    exit_point_subtype : str
        The subtype of the backend.
    identifying_properties : dict
        A dictionary of properties that uniquely identify this backend.
    name : str
        The display name of the backend.
    registered_id : int, optional
        If this backend was registered, the id given to it. The default is
        `None`.
    component_id : int, optional
        Set when this backend is registered and has been resolved to either a
        tier or an app. In the case that it has resolved to a tier in the same
        app, then this is the id of that tier. If it has resolved to a
        different app, then this is the id of that app.
    is_foreign_app : bool, optional
        True if the component_id is the id of a foreign app.

    Attributes
    ----------
    backend_type_name : str
        The name of the exit point type constant as a str (e.g., `'EXIT_DB'`).
    """
    __slots__ = (
        'exit_point_type', 'exit_point_subtype', 'identifying_properties',
        'name', 'registered_id', 'component_id', 'is_foreign_app', 'correlation_enabled',
    )

    def __init__(self, exit_point_type, exit_point_subtype, identifying_properties, name, registered_id=None,
                 component_id=None, is_foreign_app=False, correlation_enabled=True):
        super(Backend, self).__init__()

        self.exit_point_type = exit_point_type
        self.exit_point_subtype = exit_point_subtype
        self.identifying_properties = identifying_properties

        # # This makes using external APIs safe as the discovered names can be really long.
        self.name = name[:config.EXIT_CALL_DISPLAY_NAME_MAX_SIZE]
        self.registered_id = registered_id
        self.component_id = component_id
        self.is_foreign_app = is_foreign_app
        self.correlation_enabled = correlation_enabled

    @property
    def sorted_identifying_properties(self):
        properties = items(self.identifying_properties)
        sorted_properties = sorted(properties, key=lambda p: p[0])
        return tuple(sorted_properties)

    @property
    def backend_type_name(self):
        return exit_point_type_name(self.exit_point_type)

    def __str__(self):
        return 'Backend: exit type={0}, exit subtype={1}, identifying properties={2}, name={3}'.format(
            self.backend_type_name, self.exit_point_subtype, self.identifying_properties, self.name)


class BackendNamer(Formatter):
    """A utility class for generating backend names from their properties.

    """
    def format(self, format_string, properties, custom_backend_prefix=None):
        """Format the input string using the supplied properties.

        This function is similar to the string formater described in PEP-3101.
        However there some important differences.  The behaviour is best
        illustrated with some examples::

            >>> format_string = 'http://{HOST}:{PORT}{URL}?{QUERY STRING}'
            >>> format(format_string, {'HOST': 'appdynamics.com'})
            'http://appdynamics.com'
            >>> format(format_string, {'HOST': 'appdynamics.com', 'PORT': '80'})
            'http://appdynamics.com:80'
            >>> format(format_string, {'QUERY STRING': 'name=tom'})
            'name=tom'
            >>> format(format_string, {'PORT': '80', 'QUERY STRING': 'foo=bar'})
            '80?foo=bar'
            >>> format(format_string, {'HOST': '', 'PORT': '', 'URL': '/path/'})
            '/path/''
            >>> format(format_string, {'HOST': 'tom.com'},
            ... custom_backend_prefix='BACKEND')
            'BACKEND - http://tom.com'
            >>> format('{SERVER POOL}', {'SERVER POOL': 'a\nb\nc'})
            'c'

        Some things to note:

        1)  Missing replacement fields are skipped, along with their preceeding
            literal text.
        2)  Apart from the first field, literal text preceeding a replacement
            field is skipped unless there is something in front of it in the
            output.
        3)  Empty properties are ignored.
        4)  If a custom prefix is provided, it is inserted at the front of the
            output, with a ' - ' separator.
        5)  'SERVER POOL' is a special case.  We take the last item in the
            newline separated string.

        """
        result = []

        for i, (literal_text, field_name, format_spec, conversion) in \
                enumerate(self.parse(format_string)):
            value = field_name and properties.get(field_name)
            if value:
                if result or i == 0:
                    # We only want to add the prefix if this is the very
                    # first item, or there is already text in the string.
                    result.append(literal_text)
                # SERVER POOL is newline separated, take the last item.
                if field_name == 'SERVER POOL':
                    value = value.split('\n')[-1]
                result.append(value)

        result = ''.join(result)
        result = ' - '.join(x for x in (custom_backend_prefix, result) if x)

        return result


class ExitCall(object):
    """A call from the instrumented application to an external service.

    An exit call may be to a database, web application/service, or any other
    supported type of backend (such as a cache or message queue).

    Parameters
    ----------
    exit_call_id : int
        The id assigned to this exit call.
    timer : appdynamics.agent.core.timer.Timer
        The timer for keeping track of the exit call's duration.
    backend : Backend
        The backend that is the destination of this exit call.
    category : str or None
        The category this call belongs to (an arbitrary string used for
        display/categorization purposes).
    params : list or None
        The parameters associated with the operation, if any.
    caller : appdynamics.agent.models.callgraph.FrameInfo
        Information about the caller that initiated this exit call.
    operation : str, optional
        The operation that was performed as part of the exit call. It can be
        a URL, a SQL query, etc.

    Attributes
    ----------
    id : int
        The id assigned to this exit call.
    num_calls : int
        The number of times this exit call occurred during the transaction.
    num_errors : int
        The number of errors that occurred when trying perform this exit call.
    time_taken_ms : int
        The total time taken (in milliseconds) by this exit call during the
        transaction.
    min_time_taken_ms : int
        The minimum time taken (in milliseconds) by this exit call during the
        transaction. If there was only one call, this is equivalent to both
        `time_taken_ms` and `max_time_taken_ms`.
    max_time_taken_ms : int
        The maximum time taken (in milliseconds) by this exit call during the
        transaction. If there was only one call, this is equivalent to both
        `time_taken_ms` and `min_time_taken_ms`.
    optional_properties : dict
        Any optional (non-identifying) properties associated with this
        exit call. These are visible in the UI, but not used to identify the
        backend.

    """
    __slots__ = (
        'sequence_info', 'timer', 'backend', 'category',
        'operation', 'params',
        'num_calls', 'num_errors',
        'time_taken_ms', 'min_time_taken_ms', 'max_time_taken_ms',
        'start_frame_info', '__weakref__', 'was_assigned', 'was_added', 'error_details',
        'end_frame_info', 'start_caller', 'end_caller', 'optional_properties',
    )

    def __init__(self, sequence_info, timer, backend, category, params, start_frame_info, operation=None):
        super(ExitCall, self).__init__()
        self.sequence_info = sequence_info
        self.timer = timer

        self.backend = backend
        self.category = str(category) if category is not None else None
        self.params = params

        # Truncate the operation string in case it is really huge. This could
        # be the case if we were putting some HTML in a cache or something.
        operation_max_length = config.EXIT_CALL_DETAILS_LENGTH
        if operation is not None:
            operation = str(operation)
            if len(operation) > operation_max_length:
                operation = operation[:operation_max_length] + '...'
        self.operation = operation

        self.num_calls = 0
        self.time_taken_ms = 0
        self.min_time_taken_ms = None
        self.max_time_taken_ms = 0

        self.num_errors = 0
        self.start_frame_info = start_frame_info
        self.was_assigned = False
        self.was_added = False
        self.error_details = ''
        self.end_frame_info = None
        self.start_caller = None
        self.end_caller = None
        self.optional_properties = {}

    def add_call(self, error_details, end_frame_info):
        time_ms = self.timer.stop()
        self.timer.reset()
        self.end_frame_info = end_frame_info
        self.num_calls += 1
        self.time_taken_ms += time_ms

        if error_details:
            self.error_details = error_details
            self.num_errors += 1

        if self.min_time_taken_ms is None or time_ms < self.min_time_taken_ms:
            self.min_time_taken_ms = time_ms

        if time_ms > self.max_time_taken_ms:
            self.max_time_taken_ms = time_ms


def make_backend_identifier_dict(backend):
    if backend.registered_id:
        identifier = {
            'type': pb.BackendIdentifier.REGISTERED,
            'registeredBackend': {
                'exitPointType': backend.exit_point_type,
                'backendID': backend.registered_id,
                'componentID': backend.component_id,
                'componentIsForeignAppID': backend.is_foreign_app,
            },
        }
    else:
        identifier = {
            'type': pb.BackendIdentifier.UNREGISTERED,
            'unregisteredBackend': {
                'exitCallInfo': {
                    'exitPointType': backend.exit_point_type,
                    'exitPointSubtype': backend.exit_point_subtype,
                    'displayName': bytes(backend.name),
                    'identifyingProperties': make_name_value_pairs(backend.identifying_properties),
                },
            },
        }

    identifier['exitPointSubtype'] = backend.exit_point_subtype
    return identifier


def make_backend_metrics_dicts(exit_calls):
    backends = {}

    for call in exit_calls:
        key = (call.backend.exit_point_type, call.backend.sorted_identifying_properties, call.category)
        if key in backends:
            stats = backends[key]
            stats['timeTaken'] += call.time_taken_ms
            stats['numOfCalls'] += call.num_calls
            stats['numOfErrors'] += call.num_errors
            stats['minCallTime'] = min(stats['minCallTime'], call.min_time_taken_ms)
            stats['maxCallTime'] = max(stats['maxCallTime'], call.max_time_taken_ms)
        else:
            backends[key] = {
                'category': call.category,
                'timeTaken': call.time_taken_ms,
                'numOfCalls': call.num_calls,
                'numOfErrors': call.num_errors,
                'minCallTime': call.min_time_taken_ms,
                'maxCallTime': call.max_time_taken_ms,
                'backendIdentifier': make_backend_identifier_dict(call.backend),
            }

    return list(values(backends))


def make_backend_reresolve_dict(backend_id):
    try:
        reresolution = {
            'backendId': int(backend_id),
        }
        return reresolution
    except:
        return None
