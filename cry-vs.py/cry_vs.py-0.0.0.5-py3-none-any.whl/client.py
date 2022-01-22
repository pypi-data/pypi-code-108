import logging

# check if logging is configured
import sys

if not logging.getLogger().handlers:
    print(
        """---- BEGIN IMPORTANT MESSAGE ----\n"""
        """This module uses python's built in logging module. Please configure it before using this module.\n"""
        """simply run the following code before importing any other modules:\n\n"""
        """\timport sys\n\timport logging\n\tlogging.basicConfig(encoding="utf-8", stream=sys.stdout, level=logging.INFO)\n\n"""
        """since this has not been configured, cry-vs.py will use a basic configuration.\n"""
        """https://docs.python.org/3/howto/logging.html for more info\n"""
        """---- END IMPORTANT MESSAGE ------\n"""
    )
    logging.basicConfig(encoding="utf-8", stream=sys.stdout, level=logging.INFO)
    logging.info("logging was not been configured, using basic configuration")

import atexit
import json

from .emitter import Emitter
from .HTTPHelper import HTTP


class Client:
    key = None
    server = None
    allowUnsecure = None

    def __init__(self, key, server="https://cry-vs.herokuapp.com", allowUnsecure=False):
        self.key = key
        self.server = server
        self.allowUnsecure = allowUnsecure
        logging.info("Client created")

    funcs = []
    this = ""

    def listen(func):
        Client.funcs.append(func)

    def login(self):
        server = self.server
        if not server.lower().startswith("https://cry-vs.herokuapp.com") and not server.lower().startswith("https://beta-cry-vs.herokuapp.com"):
            logging.warning("This is not an official Crypto Versus server. Please proceed with caution")

        if server.lower().startswith("https://beta-cry-vs.herokuapp.com"):
            logging.warning(
                "This is the domain for the beta branch. Please switch to the main branch 'https://cry-vs.herokuapp.com' if you don't know what you're doing."
            )

        if server.lower().startswith("http://") and self.allowUnsecure is False:
            logging.critical(
                f"{server} could not be loaded as it is http. please change it to https or set allowUnsecure to True in the function parameters.")
            return

        r = HTTP.sendRequest(
            method=HTTP.Methods.POST,
            url=server + "/api/login",
            data=json.dumps({
                "key": self.key
            })
        )

        emitter = Emitter(funcs=self.funcs, expire=r.headers["Expire"])
        emitter.enqueue(name="on_ready", args=r.headers["Expire"])
        emitter.queue()  # runs the event loop. this is an infinite function so anything that needs to be done should be done before this

        atexit.register()
