#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in Modules
import logging

# Third Party Modules
import psycopg2

# Logging
logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn, connect_timeout=5)
        if self.conn.get_dsn_parameters()['port'] == "5000":
            read_only = False
        else:
            read_only = True
        self.conn.set_session(isolation_level="read uncommitted",
                              readonly=read_only,
                              autocommit=False)