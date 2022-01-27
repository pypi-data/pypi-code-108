# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Models and mappers for business transactions.

Atttributes
-----------
ENTRY_WSGI : int, const
    A constant representing the WSGI entry point type.
ENTRY_FLASK : int, const
    A constant representing the Flask entry point type.
ENTRY_DJANGO : int, const
    A constant representing the Django entry point type.

Examples
--------
Transactions should be created using a transaction factory. To get a
transaction factory, you first need a timer factory such as the `timer` method
of an `Agent` instance:

    >>> from appdynamics.agent.core import Agent
    >>> agent = Agent()

Once you have the timer factory, create a transaction factory:

    >>> factory = make_transaction_factory(agent.timer)

You can now use `factory` to create transactions:

    >>> bt = factory()

The returned transaction has a timer that has not been started. You can start
the timer by calling `start` on it:

    >>> bt.timer.start()

To conveniently set attributes of the created transaction, pass keyword
arguments to the factory that correspond to the transaction's attributes:

    >>> bt = factory(name='my-custom-bt', registered_id=42)
    >>> bt.name
    'my-custom-bt'
    >>> bt.registered_id
    42

You can, of course, always set an attribute of a BT directly:

    >>> bt.entry_type = ENTRY_FLASK

You can convert transactions into variable dictionaries that can then be
packed into various protobufs:

    >>> bt_identifier = make_bt_identifier_dict(bt)
    {'type': 1, 'btID': 42}
    >>> from appdynamics.agent.core.pb import pb_from_dict
    >>> pb_from_dict(pb.BTIdentifier(), bt_identifier)

"""

from __future__ import unicode_literals
import time
import threading
import weakref

from appdynamics import config
from appdynamics.lang import items, long
from appdynamics.lib import (
    make_random_id,
    GREENLETS_ENABLED,
)

from appdynamics.agent.core import correlation, pb
from appdynamics.agent.core.logs import setup_logger
from appdynamics.agent.models import errors, exitcalls


if GREENLETS_ENABLED:
    import greenlet


ENTRY_PYTHON_WEB = pb.PYTHON_WEB
ENTRY_WSGI = ENTRY_PYTHON_WEB
ENTRY_CLI = ENTRY_PYTHON_WEB
ENTRY_TORNADO = ENTRY_PYTHON_WEB
ENTRY_ASGI = ENTRY_PYTHON_WEB


def make_transaction_factory(agent, timer_factory, is_bt_error):
    """Return a factory that creates transactions.

    Parameters
    ----------
    timer_factory : callable
        A callable with no required arguments that returns a timer object
        compatible with `appdynamics.agent.core.timer.Timer`.

    Returns
    -------
    factory : callable
        A callable with no positional arguments that returns a new `Transaction`
        instance when called. Any keyword arguments to this callable are set as
        attributes of the returned transaction.

    """
    def factory(**kwargs):
        bt = Transaction(agent, timer_factory, is_bt_error)

        for k, v in items(kwargs):
            setattr(bt, k, v)

        return bt

    return factory


class Transaction(object):
    """A business transaction.

    Parameters
    ----------
    timer_factory : callable
        A callable taking no parameters that returns a new instance of
        :py:class:`appdynamics.agent.core.timer.Timer` when called

    Attributes
    ----------
    lock : threading.Lock
        A lock that used to synchronize access to the BT for the purposes of
        marking it completed and reporting it
    request_id : long
        A random 64-bit identifier for identifying requests concerning this BT.
    timer : appdynamics.agent.core.timer.Timer
        A timer for keeping track of this BT's duration.
    entry_type : int or bytes
        If the BT originates with this application, one of the `ENTRY_xxx`
        constants defined in :py:mod:`appdynamics.agent.models.transactions`.
        Otherwise, a byte-string with the unparsed name of the entry point
        from the originating BT. (You shouldn't try to parse the entry point
        when it's a byte-string. Just pass it on unmodified.)
    name : str
        The name of this BT.
    registered_id : int or None
        If the BT is registered with the controller, the id it is registered
        with by the controller. Otherwise, `None`.
    naming_scheme_type : str or None
        The name of the naming scheme used to generate the BT name, if any.
        TODO: Describe why this can be `None`.
    incoming_correlation : correlation.CorrelationHeader or None
        If we detected that this BT is continuing a BT, the incoming
        correlation header is stored here. Otherwise, the BT originated at
        with this app, and this attribute is `None`.
    is_sent : bool
        True if this transaction's details have been reported. Otherwise,
        false.
    completed : bool
        True if this transaction has completed (i.e., `end_transaction` has
        been called for it), even if the transaction hasn't been sent.
    bt_info_request : dict or None
        A dict representation of the data for a `pb.BTInfoRequest` that was
        sent when transaction service sent the request. If a request has not
        yet been made for this transaction, then `None`.
    bt_info_response : pb.BTInfoResponse or None
        The response received after sending the `bt_info_request` via the
        transaction service. If the response hasn't been received yet, then
        `None`.
    continuing_snapshot_enabled : bool
        True if this BT is a continuing transaction, and the correlation
        header enabled snapshotting.
    errors : list[errors.ErrorInfo]
        A list of error logs that have been recorded during this BT.
    exceptions : list[errors.ExceptionInfo]
        A list of uncaught exceptions that have been recorded during this BT.
    custom_match_id : int or None
        The id of the custom match point that caused this BT to be matched, if
        any. If the BT was auto-discovered, this will be `None`.

    """

    def __init__(self, agent, timer_factory, is_bt_error):
        super(Transaction, self).__init__()
        self.agent = agent

        self.logger = setup_logger('appdynamics.agent')
        self.lock = threading.Lock()

        self.request_id = make_random_id()
        self._timer_factory = timer_factory
        self.timer = timer_factory()

        self.is_sent = False
        self.is_crossapp = False
        self.is_continue = False

        # Identificaiton of the BT.
        self.entry_type = None
        self.name = None
        self.registered_id = None
        self.naming_scheme_type = None
        self.custom_match_id = None
        self.url = None
        self.status_code = None
        self.request = None

        # Correlation
        self._incoming_correlation = None
        self.cross_app_correlation = None

        # Error and exception handling.
        self.has_errors = False
        self.logged_errors = []
        self.http_errors = []
        self.exceptions = []
        self._exception_set = set()
        self.is_bt_error = is_bt_error

        # Snapshotting.
        self.snapshotting = False
        self.snapshot_start_time_ms = None
        self.snapshot_guid = None
        self.snapshot_trigger = None
        self.sample_data = None
        self.snapshot_user_data = {}
        self.http_data_gatherer = None
        self.midc_data = []
        self.eum_guid = None
        self.correlation_hdr_snapshot_guid = None

        # Exit calls.
        self._exit_call_id = 0
        self._exit_calls = {}
        self._properties = {}
        self._active_exit_calls = set()

        # Proxy lifecycle stuff.
        self.bt_info_request = None
        self._bt_info_response = None
        self.started_on_time = True  # if we time out waiting for the bt info respsonse, this is False

        # Thread/greenlet context.
        self.thread = threading.current_thread()
        self.thread_id = self.thread.ident

        # Stalled transaction specific stuff
        self.is_stalled = False
        self.stall_message = None

        self._bt_info_response_event = threading.Event()

        if GREENLETS_ENABLED:
            gr = greenlet.getcurrent()
            self.greenlet_ref = weakref.ref(gr)
        else:
            self.greenlet_ref = None

    def __str__(self):
        return '%s %s: current duration %dms' % (self.thread, self.name, self.timer.duration_ms)

    @property
    def errors(self):
        errors = list(self.logged_errors)
        errors.extend(self.http_errors)
        return errors

    @property
    def is_auto_discovered(self):
        return self.naming_scheme_type is not None

    @property
    def bt_info_response(self):
        return self._bt_info_response

    @bt_info_response.setter
    def bt_info_response(self, response):
        self._bt_info_response = response
        if response:
            self._bt_info_response_event.set()

    def wait_for_bt_info_response(self, timeout_ms=10):
        """Wait (exactly once) for the BTInfoResponse or timeout.

        Only waits the first time it's called for this BT if there is no
        BTInfoResponse. If the BT already has a response, or if we have
        already waited, immediately returns.

        Other Parameters
        ----------------
        timeout_ms : int (optional)
            The timeout in milliseconds, defaults to 10ms.

        Returns
        -------
        bool
            True if a BTInfoResponse was received within the timeout, else
            False.

        """
        # check for `False` explicitly; on python <2.7 `wait` always returns `None`.
        if self._bt_info_response_event.wait(timeout=timeout_ms / 1000.0) is False:
            self.started_on_time = False
            self.logger.warning('Timed out waiting for BT info response - downstream correlation may be impacted.')

        self._bt_info_response_event.set()
        return self._bt_info_response is not None

    @property
    def continuing_snapshot_enabled(self):
        if self.cross_app_correlation:
            return self.cross_app_correlation[correlation.SNAPSHOT_ENABLED_KEY]

        return self._incoming_correlation and self._incoming_correlation[correlation.SNAPSHOT_ENABLED_KEY]

    @property
    def forced_snapshot_enabled(self):
        if not self.request or not self.request.headers.get('appdynamicssnapshotenabled'):
            return False

        current_time = time.time()
        if current_time - self.agent.last_forced_snapshot < config.FORCED_SNAPSHOT_INTERVAL:
            self.logger.warning("appdynamicssnapshotenabled header ignored.\n"
                                "If this is a legitimate synthetic request, decrease 'forced-snapshot-interval' in"
                                "your agent config.")
            return False

        self.agent.last_forced_snapshot = current_time
        return True

    @property
    def active_exit_calls(self):
        """
        Return a list of the currently active exit calls for this BT.

        Since the active exit calls are constantly changing we return
        a copy of the internal set. This allows consumers to iterate,
        or modify the list in any way they want.

        For instance, Snapshot service gets a copy of active exit calls,
        not the reference because the later's state may be changed at the time when
        make_call_graph is called while constructing call graph.

        """
        return list(self._active_exit_calls)

    @property
    def completed(self):
        # A transaction is complete if its timer was started and is currently stopped.
        return self.timer.has_stopped

    @property
    def incoming_correlation(self):
        return self._incoming_correlation

    @incoming_correlation.setter
    def incoming_correlation(self, hdr):
        if hdr and not hdr.is_cross_app:
            self.entry_type = hdr[correlation.BT_TYPE_KEY]
            self.name = hdr[correlation.BT_NAME_KEY]

            def to_long(x):
                try:
                    return long(x)
                except (TypeError, ValueError):
                    return None

            self.registered_id = to_long(hdr[correlation.BT_ID_KEY])
            self.naming_scheme_type = hdr[correlation.BT_MATCH_VALUE_KEY]

        self._incoming_correlation = hdr

    def start_exit_call(self, caller, backend, operation=None, params=None, category=None):
        """Mark the start of an exit call and set the active exit call.

        Parameters
        ----------
        caller : FrameInfo
            The Python frame that "initiated" this exit call
        backend : appydynamics.agent.models.exitcalls.Backend
            The backend to which the exit call is made
        operation : str, optional
            A string describing the operation that is being performed, such as
            the URL of an HTTP request or a SQL query for a DB
        params : iterable of strs, optional
            An iterable of strings that are parameters passed to the given
            operation, or `None` (the default) if there are no parameters for
            the operation
        category : str, optional
            A category name for grouping exit calls or `None` (the default) if
            the exit calls should not be explicitly grouped by the agent

        Returns
        -------
        exitcalls.ExitCall or None
            The exit call model or `None` if an exit call couldn't be started

        See Also
        --------
        end_exit_call

        """
        key = (caller, backend, operation)
        try:
            exit_call = self._exit_calls[key]
            exit_call.timer.reset()  # ExitCall accounts for min, max, and sum (total)
        except KeyError:
            timer = self._timer_factory()
            self._exit_call_id += 1

            if self.incoming_correlation:
                sequence_info = self.incoming_correlation[correlation.EXIT_GUID_KEY] + '|' + str(self._exit_call_id)
            else:
                sequence_info = str(self._exit_call_id)

            exit_call = exitcalls.ExitCall(sequence_info, timer, backend, category, params, caller, operation=operation)
            self._exit_calls[key] = exit_call

        self._active_exit_calls.add(exit_call)
        exit_call.timer.start()
        return exit_call

    def end_exit_call(self, exit_call, end_frame_info, exc_info=None):
        """End the active exit call.

        Parameters
        ----------
        exc_info : (exc_type, exc_value, exc_tb) or None
            If an uncaught exception occurred during the exit call, then this
            contains the exception info (as returned by `sys.exc_info()`). If
            no exception occurred, then `None`.

        """
        error_details = None
        if exc_info:
            self.add_exception(*exc_info)
            error_details = repr(exc_info[1])

        if exit_call in self._active_exit_calls:
            exit_call.add_call(error_details, end_frame_info)
            self._active_exit_calls.remove(exit_call)

    def add_logged_error(self, error_info):
        """Add an logged error to a BT.

        Parameters
        ----------
        error_info : errors.ErrorInfo
            An error info model to add to the BT's error list.

        See Also
        --------
        add_exception
            For reporting uncaught exceptions that occurred during the BT

        """
        self.has_errors = self.has_errors or self.is_bt_error(has_logged_errors=True)
        if self.has_errors:
            self.logged_errors.append(error_info)

    def add_http_error(self, error_info):
        """Add an http error to a BT.

        Parameters
        ----------
        error_info : errors.ErrorInfo
            An error info model to add to the BT's error list.

        See Also
        --------
        add_exception
            For reporting uncaught exceptions that occurred during the BT

        """
        self.http_errors.append(error_info)
        self.has_errors = True

    def _is_repeated_exception(self, exc_value):
        """Return True if we have already added this exception to the BT.

        The reason for the recursive nature of this function is due to code I
        have seen code which traps exceptions and wraps them in other classes
        e.g.::

            try:
                raise InnerException('Stop that!')
            except InnerException as e:
                raise MoreGenericException('An exception happened!', e)

        """
        if exc_value in self._exception_set:
            return True
        for arg in exc_value.args:
            if isinstance(arg, Exception):
                return self._is_repeated_exception(arg)
        return False

    def add_exception(self, exc_type, exc_value, exc_tb):
        """Add an exception to a BT.

        The arguments are those returned by sys.exc_info().

        Parameters
        ----------
        exc_type : type
            The type (class) of the raised exception
        exc_value
            The value of the raised exception
        exc_tb : traceback
            The traceback associated with the raised exception

        See Also
        --------
        add_http_error, add_logged_error
            For reporting errors logged during the BT

        """
        if exc_value is None:
            return

        # We may have added this exception already in an intercepted exit call.
        if self._is_repeated_exception(exc_value):
            return

        exception = errors.ExceptionInfo(exc_type, exc_value, exc_tb)

        if len(exception.stack_trace_frames):
            self.has_errors = self.has_errors or self.is_bt_error(exception=exception)
            if self.has_errors:
                self.exceptions.append(exception)
                self._exception_set.add(exc_value)
