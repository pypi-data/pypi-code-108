import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    for handler in logging.getLogger().handlers:
        logger.addHandler(handler)

import json
from .HTTPHelper import HTTP


class Client:
    class _Auth:
        token = None

        class _Token:
            text: str = None

            time: datetime.datetime = None

            def __init__(self, text: str, time: int):
                self.text = text
                self.time = datetime.timedelta(milliseconds=time) + datetime.datetime.now()
                logger.debug("Token:" + self.text)

            def _update(self, text: str, time: int):
                self.text = text
                self.time = datetime.timedelta(milliseconds=time) + datetime.datetime.now()

    _self = None
    key = None
    server = None
    allowUnsecure = None
    keep_alive = None

    auth: _Auth = _Auth()

    def __init__(self, server="https://cry-vs.herokuapp.com", allow_unsecure=False, keep_alive=True):
        from .emitter import Emitter
        self.Emitter = Emitter
        self.server = server
        self.allowUnsecure = allow_unsecure
        self.keep_alive = keep_alive
        logging.info("Client created")

    funcs = []
    this = ""

    def listen(self, func):
        self.funcs.append(func)

    def login(self, *args):
        server = self.server
        if not server.lower().startswith("https://cry-vs.herokuapp.com") and not server.lower().startswith(
                "https://beta-cry-vs.herokuapp.com"):
            logger.warning("This is not an official Crypto Versus server. Please proceed with caution")

        if server.lower().startswith("https://beta-cry-vs.herokuapp.com"):
            logger.warning(
                "This is the domain for the beta branch. Please switch to the main branch 'https://cry-vs.herokuapp.com' if you don't know what you're doing."
            )

        if server.lower().startswith("http://") and self.allowUnsecure is False:
            logger.critical(
                f"{server} could not be loaded as it is http. please change it to https or set allowUnsecure to True in the class parameters.")
            return

        def finish(r):
            logger.debug(self.funcs)
            self.auth.token = self._Auth._Token(r.text, int(r.headers["Expire"]))
            emitter = self.Emitter(funcs=self.funcs, client=self)
            emitter.enqueue(name="on_ready", args=r.headers["Expire"])
            emitter.queue()  # runs the event loop. this is an infinite function so anything that needs to be done should be done before this

        if len(args) == 0:
            logger.critical("No auth data provided. please provide a username and password, or an API key")
        elif len(args) == 1:
            logger.info("using API key")
            r = HTTP.send_request(
                method=HTTP.methods.POST,
                url=server + "/api/login",
                data=json.dumps({
                    "key": args[0]
                })
            )
            finish(r)
        elif len(args) == 2:
            logger.info("using username and password")
            r = HTTP.send_request(
                method=HTTP.methods.POST,
                url=server + "/api/login",
                data=json.dumps({
                    "username": args[0],
                    "password": args[1]
                })
            )
            finish(r)

    async def before_expire(self):
        r = HTTP.send_request(
            method=HTTP.methods.POST,
            url=self.server + "/api/refresh-token",
            data=json.dumps({
                "token": self.auth.token.text
            })
        )
        self.auth.token._update(r.text, int(r.headers["Expire"]))
        logger.info("Token refreshed")

    funcs.append(before_expire)
