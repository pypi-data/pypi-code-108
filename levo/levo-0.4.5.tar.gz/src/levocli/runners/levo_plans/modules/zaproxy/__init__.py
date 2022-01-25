import ipaddress
import logging
import os
import socket
import subprocess
from contextlib import closing
from pathlib import Path
from uuid import uuid4

from attrs import Factory, define, field
from levo_commons.providers import ZaproxyProvider as ZaproxyProviderInterface

from levocli.logger import get_log_level, get_logger

logger = get_logger(name="ZAPROXY")


def get_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@define(slots=True, repr=False)
class ZaproxyProvider(ZaproxyProviderInterface):
    ip: str = field(
        default="127.0.0.1", validator=lambda _, __, v: ipaddress.ip_address(v)
    )
    port: int = Factory(get_port)
    home_directory: Path = Factory(lambda: Path(f"/tmp/levo_zap_{uuid4()}"))
    api_key: str = Factory(lambda: str(uuid4()))
    process: subprocess.Popen[bytes] = field(init=False)

    def start(self) -> None:
        self.home_directory.mkdir(parents=True, exist_ok=True)
        debug = get_log_level() == logging.DEBUG
        log_directory = Path("/home/levo/work/") if debug else self.home_directory
        log_file = log_directory / "levo_zap.log"
        logger.info(f"Writing ZAP Logs to {log_file}")
        zap_jar = next(
            Path(os.getenv("ZAP_INSTALL_DIR", "/modules/zaproxy/")).glob("zap-*.jar")
        )
        start_command: list[str] = [
            "java",
            f"-Dlevo.zap.log={str(log_file.resolve())}",
            "-jar",
            str(zap_jar),
            "-nostdout",
            "-daemon",
            "-host",
            self.ip,
            "-port",
            str(self.port),
            "-dir",
            str(self.home_directory.resolve()),
            "-config",
            f"api.key={self.api_key}",
        ]
        self.process = subprocess.Popen(
            start_command,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info(f"Started ZAP at {self.ip}:{self.port}.")

    def stop(self) -> None:
        logger.info("Shutting down ZAP.")
        self.process.terminate()
        self.process.wait()
        logger.info(f"Shut down ZAP.")

    def is_running(self) -> bool:
        # TODO: Does this need some more tests?
        poll = self.process.poll()
        return poll is None
