#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import sys
import importlib
# from multiprocessing import Process
import logging

import socketserver


root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root_dir)
from context import InitContext
from base import BaseModel
import re
from lcyframe import ServicesFindet

logger = logging.getLogger(__name__)


def load_model(cls, model_dir=None):
    """
    import model class obj global
    warning: the class obj cant not start whit "__"
    :return:
    """
    model_dir = model_dir or cls.model_dir
    sys.path.append(model_dir)
    for m in [x for x in os.listdir(model_dir) if re.findall('[A-Za-z]\w+_model\.py$', x)]:
        m = m[:-3]
        if m == "__init__":
            continue
        for attr_name, value in importlib.import_module(m).__dict__.items():
            if attr_name.startswith("__"):
                continue

            if not hasattr(BaseModel, attr_name):
                setattr(BaseModel, attr_name, value)
                logging.debug("model [%s] register success!" % attr_name)

class Server(object):
    def __init__(self, **kwargs):
        self.ROOT = kwargs["ROOT"]
        self.socket_servers = kwargs['socket_servers']
        self.register()
        self.config = kwargs

    def register(self):
        pass

    def start(self):
        for server_conf in self.socket_servers:
            port = server_conf['port']
            mod, func = server_conf['path'].rsplit('.', 1)
            handler = getattr(importlib.import_module(mod), func)
            handler.config = self.config
            ServicesFindet(handler, BaseModel)(handler.config)
            load_model(handler, "model")
            socketserver.TCPServer.allow_reuse_address = True
            s = socketserver.ThreadingTCPServer(('0.0.0.0', port), handler)
            logger.warning("%s is start" % server_conf)
            s.serve_forever()
            # p = Process(target=s.serve_forever)
            # p.start()


if __name__ == '__main__':
    config = InitContext.get_context()
    server = Server(**config)
    server.start()
