#!/usr/bin/env python3
# coding: utf-8

import logging
import random

from sqlalchemy.orm import Session, scoped_session, sessionmaker

_logger = logging.getLogger(__name__)


class RoutingSession(Session):
    # http://docs.sqlalchemy.org/en/latest/orm/persistence_techniques.html
    # #custom-vertical-partitioning
    def __init__(self, primary_engine, standby_engines, **kwargs):
        super(RoutingSession, self).__init__(**kwargs)
        self.primary_engine = primary_engine
        self.standby_engines = list(standby_engines)

    def get_bind(self, mapper=None, clause=None):
        # return self.bind
        if self._flushing:
            return self.primary_engine
        if len(self.standby_engines) == 1:
            return self.standby_engines[0]
        return random.choice(self.standby_engines)


def get_session_klass(primary_interface, standby_interfaces):
    if not standby_interfaces:
        return primary_interface.session_klass
    kwargs = {
        'primary_engine': primary_interface.engine,
        'standby_engines': [x.engine for x in standby_interfaces],
    }
    factory = sessionmaker(class_=RoutingSession, **kwargs)
    return scoped_session(factory)

