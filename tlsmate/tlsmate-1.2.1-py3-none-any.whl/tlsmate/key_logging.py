# -*- coding: utf-8 -*-
"""Module for logging to a key log file

Reference: https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS/Key_Log_Format
"""
# import basic stuff
from typing import Optional, TextIO

# import own stuff

# import other stuff


class KeyLogger(object):
    """Class to log to a key log file
    """

    _fd: Optional[TextIO] = None

    @classmethod
    def open_file(cls, file_name: str) -> None:
        """Opens the key logging file in "append" mode.

        Arguments:
            file_name (str): the file name of the key logging file
        """

        cls._fd = open(file_name, "a")

    @classmethod
    def close(cls) -> None:
        """Closes the key logging file.
        """

        assert cls._fd
        cls._fd.close()

    @classmethod
    def _log(cls, log_type: str, client_random: bytes, secret: bytes) -> None:
        """Adds a log to the key logging file.

        Arguments:
            log_type: the type of the log, first element of the log entry
            client_random: the random value from the ClientHello
            secret: the secret to log
        """

        if cls._fd:
            cls._fd.write(f"{log_type} {client_random.hex()} {secret.hex()}\n")
            cls._fd.flush()

    @classmethod
    def master_secret(cls, client_random: bytes, secret: bytes) -> None:
        """Generates a CLIENT_RANDOM log.

        Arguments:
            client_random: the random value from the ClientHello
            secret: the secret to log
        """

        cls._log("CLIENT_RANDOM", client_random, secret)

    @classmethod
    def client_early_tr_secret(cls, client_random: bytes, secret: bytes) -> None:
        """Generates a CLIENT_EARLY_TRAFFIC_SECRET log.

        Arguments:
            client_random: the random value from the ClientHello
            secret: the client early traffic secret
        """

        cls._log("CLIENT_EARLY_TRAFFIC_SECRET", client_random, secret)

    @classmethod
    def client_hs_tr_secret(cls, client_random: bytes, secret: bytes) -> None:
        """Generates a CLIENT_HANDSHAKE_TRAFFIC_SECRET log.

        Arguments:
            client_random: the random value from the ClientHello
            secret: the client handshake traffic secret
        """

        cls._log("CLIENT_HANDSHAKE_TRAFFIC_SECRET", client_random, secret)

    @classmethod
    def server_hs_tr_secret(cls, client_random: bytes, secret: bytes) -> None:
        """Generates a SERVER_HANDSHAKE_TRAFFIC_SECRET log.

        Arguments:
            client_random: the random value from the ClientHello
            secret: the server handshake traffic secret
        """

        cls._log("SERVER_HANDSHAKE_TRAFFIC_SECRET", client_random, secret)

    @classmethod
    def client_tr_secret_0(cls, client_random: bytes, secret: bytes) -> None:
        """Generates a CLIENT_TRAFFIC_SECRET_0 log.

        Arguments:
            client_random: the random value from the ClientHello
            secret: the client traffic secret
        """

        cls._log("CLIENT_TRAFFIC_SECRET_0", client_random, secret)

    @classmethod
    def server_tr_secret_0(cls, client_random: bytes, secret: bytes) -> None:
        """Generates a SERVER_TRAFFIC_SECRET_0 log.

        Arguments:
            client_random: the random value from the ClientHello
            secret: the server traffic secret
        """

        cls._log("SERVER_TRAFFIC_SECRET_0", client_random, secret)
