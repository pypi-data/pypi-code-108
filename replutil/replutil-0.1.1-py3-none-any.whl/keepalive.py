from flask import Flask
from typing import Optional, List
from requests import Session, utils, Response
from multiprocessing import Process
from functools import partial
from logging import getLogger, Logger
from os import environ
from .util import *

logger: Logger = getLogger(__name__)


class ReplKeepAlive:
    def __init__(self, upr_key: str, *, port: int = get_port()) -> None:
        quiet()
        assert in_repl()

        self._app: Flask = self.build_app()
        self._session: Session = Session()
        self._upr: str = upr_key

        run_flask: partial = partial(self._app.run, host="0.0.0.0", port=port)
        self._process: Process = Process(target=run_flask, name=f"{self._app.name} run")

        self.start()

        self._id: int = self.register()

    def start(self) -> None:
        self._process.start()
        logger.info(f'Started ping handler on process "{self._process.name}"')

    def __enter__(self) -> "ReplKeepAlive":
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.close()

    def cleanup(self) -> None:
        url: str = "https://api.uptimerobot.com/v2/getMonitors"

        payload: str = f"api_key={utils.quote(self._upr)}&format=json&logs=1"
        headers: dict[str, str] = {"content-type": "application/x-www-form-urlencoded", "cache-control": "no-cache"}

        response: Response = self._session.request("POST", url, data=payload, headers=headers)

        loaded_json: dict = response.json()

        for monitor in loaded_json["monitors"]:
            if monitor["friendly_name"] == namespace() or monitor["url"] == instance_url():
                self.delete(monitor["id"])

    def register(self) -> int:
        self.cleanup()

        url: str = "https://api.uptimerobot.com/v2/newMonitor"

        payload: str = f"api_key={utils.quote(self._upr)}&format=json&type=1&url={instance_url()}&friendly_name={namespace()}"
        headers: dict[str, str] = {"cache-control": "no-cache", "content-type": "application/x-www-form-urlencoded"}

        response: Response = self._session.request("POST", url, data=payload, headers=headers)

        return response.json()["monitor"]["id"]

    def delete(self, id: int) -> bool:
        url: str = "https://api.uptimerobot.com/v2/deleteMonitor"

        payload: str = f"api_key={utils.quote(self._upr)}&format=json&id={id}"
        headers = {"cache-control": "no-cache", "content-type": "application/x-www-form-urlencoded"}

        response: Response = self._session.request("POST", url, data=payload, headers=headers)

        return response.status_code == 200

    def deregister(self) -> bool:
        return self.delete(self._id)

    def join(self, *, timeout: Optional[int] = None) -> None:
        return self._process.join(timeout=timeout)

    def close(self) -> None:
        self.deregister()
        self._process.terminate()

    def build_app(self) -> Flask:
        app: Flask = Flask(__name__)

        @app.route("/")
        def ping():
            logger.info("pinged")
            return "pong"

        return app


__all__: List[str] = ["ReplKeepAlive"]
