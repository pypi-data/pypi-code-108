#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, os
import platform
from lcyframe import App
from lcyframe import yaml2py
from context import InitContext

config = InitContext.get_context()
# InitContext.init_db()

config["api_schema"] = yaml2py.load_api_schema("api_schema")
# config["wsgi"]["port"] = config["wsgi"]["port"] if len(sys.argv) == 1 else int(sys.argv[1])
# config["mqtt_config"]["client_id_name"] = "app_%s_%s" % (platform.node(), config["wsgi"]["port"])

app = App(**config)
app.start()
