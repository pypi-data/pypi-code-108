# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

""" Agent Module handles communication and instrumentation, this
is the main class.
"""

from __future__ import unicode_literals

from tcell_agent.config.configuration import get_config, set_config, TCellAgentConfiguration
from tcell_agent.events.startup_events import get_startup_events
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.loggers.python_logger import PythonLogger
from tcell_agent.policies.policies_manager import PoliciesManager
from tcell_agent.policies.policy_polling import PolicyPolling
from tcell_agent.routes.route_discovery import RouteTable
from tcell_agent.rust.native_agent import create_native_agent
from tcell_agent.rust.native_library import load_native_lib
from tcell_agent.tcell_logger import get_module_logger, set_native_agent


class TCellAgent(object):
    tCell_agent = None

    def __init__(self):
        self.policies_manager = PoliciesManager(None)

    def create_native_agent(self, framework_details):
        self.native_agent = create_native_agent(framework_details)
        set_native_agent(self.native_agent)

        if get_config().enabled:
            self.policies_manager.update_native_agent(self.native_agent)
            self.policy_polling = PolicyPolling(self.policies_manager, get_config())
            self.route_table = RouteTable()

    def send_startup_events(self):
        initial_events = get_startup_events()
        self.native_agent.send_sanitized_events(initial_events)

    def send_event(self, event):
        get_module_logger(__name__).debug(
            "Sending event {} to libtcellagent".format(event)
        )
        self.native_agent.send_sanitized_events([event])

    def send_events(self, events):
        get_module_logger(__name__).debug(
            "Sending events {} to libtcellagent".format(events)
        )
        self.native_agent.send_sanitized_events(events)

    def ensure_polling_thread_running(self):
        self.policy_polling.ensure_polling_thread_running(self.native_agent)

    def is_polling_thread_running(self):
        self.policy_polling.is_polling_thread_running()

    def set_extra_diagnostics_config(self):
        self.native_agent.set_extra_diagnostics_config(get_config())

    @classmethod
    def init_agent(cls):
        if cls.tCell_agent:
            return

        try:
            set_config(TCellAgentConfiguration())
            load_native_lib()
            cls.tCell_agent = TCellAgent()

        except Exception as e:
            PythonLogger().log_message("error", "Exception while creating agent {}".format(e), __name__)

    @classmethod
    def startup(cls, framework_details):
        agent = cls.get_agent()
        agent.create_native_agent(framework_details)

        if get_config().enabled:
            agent.ensure_polling_thread_running()
            agent.send_startup_events()
            get_module_logger(__name__).info("TCellAgent Started")
            return True

        return False

    @classmethod
    def get_agent(cls):
        return cls.tCell_agent

    @classmethod
    @catches_generic_exception(__name__, "Error sending event")
    def send(cls, event):
        cls.get_agent().send_event(event)

    @classmethod
    def get_policy(cls, policy_type):
        return cls.get_agent().policies_manager.get(policy_type)

    @classmethod
    def request_metric(cls,
                       route_id,
                       request_time,
                       remote_address,
                       user_agent,
                       reverse_proxy_header_value,
                       session_id=None,
                       user_id=None):
        cls.get_agent().native_agent.report_metrics(request_time,
                                                    route_id,
                                                    session_id,
                                                    user_id,
                                                    user_agent,
                                                    remote_address,
                                                    reverse_proxy_header_value)

    @classmethod
    def discover_routes(cls, routes_info):
        cls.get_agent().route_table.discover_routes(routes_info, cls.get_agent().send_events)

    @classmethod
    def discover_database_fields(cls, database, schema, table, fields, route_id=None):
        cls.get_agent().route_table.discover_database_fields(database,
                                                             schema,
                                                             table,
                                                             fields,
                                                             route_id,
                                                             cls.get_agent().send_event)
