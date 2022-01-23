# -*- coding: utf-8 -*-
"""Implements a class to test the text server profile worker.
"""
import pathlib
import sys

from tlsmate.workers.server_profile import ReadProfileWorker
from tlsmate.workers.text_server_profile import TextProfileWorker
from tlsmate.config import Configuration
from tlsmate.tlsmate import TlsMate
from tlsmate.structs import ConfigItem
from tlsmate import command
from tlsmate.tlssuite import TlsSuiteTester, TlsLibrary
from tlsmate.tlsmate import TLSMATE_DIR

RECORDINGS_PATH = pathlib.Path(__file__).resolve().parent / "recordings"
SERVER_PROFILE = RECORDINGS_PATH / "profile_text_openssl3_0_0.yaml"


class NoTestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-expired-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL -serverpref -prioritize_chacha "
        "-cert_chain "
    ) + f"{TLSMATE_DIR}/ca/chains/server-invalid-sequence-rsa.chn"
    library = TlsLibrary.openssl3_0_0

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        cmd = (
            f"tlsmate scan localhost --port={self.config.get('port')} "
            f"--format=yaml --write-profile={SERVER_PROFILE}"
        )
        sys.argv = cmd.split()
        command.main()


def test_server_profile(style_file):
    config = Configuration()
    config.register(ConfigItem("read_profile"))
    config.register(ConfigItem("style", type=str, default=str(style_file)))
    config.register(ConfigItem("color", type=bool, default=True))
    config.set("read_profile", str(SERVER_PROFILE))
    tlsmate = TlsMate(config)
    ReadProfileWorker(tlsmate).run()
    TextProfileWorker(tlsmate).run()


if __name__ == "__main__":
    NoTestCase().entry(is_replaying=False)
