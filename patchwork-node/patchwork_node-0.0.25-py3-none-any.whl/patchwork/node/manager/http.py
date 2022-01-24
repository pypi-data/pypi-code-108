# -*- coding: utf-8 -*-

import asyncio

from aiohttp import web

from .base import Manager


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000


class HttpManager(Manager):
    """
    HTTP manager for the application.
    Supports:
    * prometheus metrics expose
    * cancelling current working tasks
    * config changes though app config provider
    * application termination
    * liveness and rediness probe
    """

    class Config(Manager.Config):
        listen_on: str = f"{DEFAULT_HOST}:{DEFAULT_PORT}"

    server_task: asyncio.Future

    async def _start(self):
        host, port = self.settings.listen_on.split(":")
        if not host:
            host = DEFAULT_HOST

        if not port:
            port = DEFAULT_PORT
        else:
            port = int(port)

        app = web.Application()
        self._setup_http_app(app)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        self.logger.info(f"HTTP manager is listening at {host}:{port}")
        self.server_task = self.app_loop.create_task(self._http_server_wait(site, runner))
        self.server_task.add_done_callback(self._on_server_task_done)

    async def _stop(self):
        self.server_task.cancel()
        await self.server_task

    def _on_server_task_done(self, fut):
        exc = fut.exception()
        if exc:
            self.logger.error(f"HTTP manager server terminated with exception {exc.__class__.__name__}({exc})")

    async def _http_server_wait(self, site, runner):
        try:
            await site._server.wait_closed()
        except asyncio.CancelledError:
            await runner.cleanup()

            if not self._is_stopping:
                # server cancelled but component is not stopping? something got wired...
                self.logger.error("HTTP manager server stopped, but manager itself is not stopping")
                # stop the manager
                await self.terminate()

    def _setup_http_app(self, app: web.Application):
        app.router.add_get('/liveness', self._handle_liveness_probe)
        app.router.add_get('/rediness', self._handle_rediness_probe)
        app.router.add_get('/state', self._handle_state)

    async def _handle_liveness_probe(self, request: web.Request) -> web.Response:

        state, details = self.get_health(include_starting=True)
        return web.json_response(details, status=(200 if state else 503))

    async def _handle_rediness_probe(self, request: web.Request) -> web.Response:

        # app is ready if all components are live and not starting
        state, details = self.get_health(include_starting=False)
        resp = web.json_response(details, status=(200 if state else 503))
        return resp

    async def _handle_state(self, request: web.Request) -> web.Response:
        return web.json_response(self.worker.get_state())

    def __repr__(self):
        res = super().__repr__()
        return f"<{res[1:-1]} [{self.settings.listen_on}]>"
