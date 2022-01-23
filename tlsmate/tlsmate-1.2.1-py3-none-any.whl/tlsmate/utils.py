# -*- coding: utf-8 -*-
"""Module defining some utilities
"""
# import basic stuff
import time
import logging
import json
import os
import sys
import argparse
from typing import List, Optional, Type, Any, Tuple, Union

# import own stuff
import tlsmate.mappings as mappings
import tlsmate.pdu as pdu
import tlsmate.structs as structs
import tlsmate.tls as tls

# import other stuff
import yaml
import pathlib


class BooleanOptionalAction(argparse.Action):
    """Class to support --flag and --no-flag arguments.

    Will be natively supported by Python3.9
    """

    def __init__(
        self,
        option_strings: List[str],
        dest: str,
        default: Optional[str] = None,
        type: Type = None,
        choices: List[str] = None,
        required: bool = False,
        help: Optional[str] = None,
        metavar: Optional[str] = None,
    ) -> None:

        _option_strings = []
        for option_string in option_strings:
            _option_strings.append(option_string)

            if option_string.startswith("--"):
                option_string = "--no-" + option_string[2:]
                _option_strings.append(option_string)

        if help is not None and default is not None:
            help += f" (default: {default})"

        super().__init__(
            option_strings=_option_strings,
            dest=dest,
            nargs=0,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in self.option_strings:
            setattr(namespace, self.dest, not option_string.startswith("--no-"))

    def format_usage(self) -> str:
        return " | ".join(self.option_strings)


def serialize_data(
    data: Any,
    file_name: Optional[str] = None,
    replace: bool = True,
    use_json: bool = False,
    indent: int = 4,
) -> None:
    """Serialize the data object to JSON or yaml.

    Arguments:
        data: the serializable data structure
        file_name: the file to write the serialized data to. If not given, the
            serialized object is printed on STDOUT.
        replace: If True, allow overwriting an existing file. Defaults to True.
            This argument is only evaluated if a file_name is given.
        json: If True, use JSON, else use Yaml.
        indent: The indentation to apply.
    """

    if file_name is not None:
        if not replace and pathlib.Path(file_name).exists():
            form = "JSON" if use_json else "Yaml"
            print(f"File {file_name} existing. {form}-file not generated")
            return

        with open(file_name, "w") as fd:
            if use_json:
                json.dump(data, fd, indent=indent, sort_keys=True)

            else:
                yaml.dump(data, fd, indent=indent)
    else:
        if use_json:
            print(json.dumps(data, indent=indent, sort_keys=True))

        else:
            print(yaml.dump(data, indent=indent))


def deserialize_data(file_name: str) -> Any:
    """Deserialize from a JSON- or Yaml-file.

    Arguments:
        file_name: the full file name

    Returns:
        the deserialized object
    """

    with open(file_name) as fd:
        return yaml.safe_load(fd)


def fold_string(text: str, max_length: int, sep: str = " ") -> List[str]:
    """Splits a string into lines of the given length.

    Arguments:
        text: the string to split
        length: the maximum length of the line
        sep: the separator where splitting the text is allowed

    Returns:
        list: the list of strings
    """

    ret_lines = []
    tokens: List[str] = []
    length = 0
    sep_len = len(sep)

    for token in text.split(sep):
        token_len = len(token)
        if length + token_len + sep_len > max_length:
            if tokens:
                ret_lines.append(sep.join(tokens) + sep)
                tokens = [token]
                length = token_len

            else:
                ret_lines.append(token + sep)
                tokens = []
                length = 0

        else:
            tokens.append(token)
            length += token_len + sep_len

    if tokens:
        ret_lines.append(sep.join(tokens))

    return ret_lines


def get_cipher_suite_details(
    cipher_suite: tls.CipherSuite,
) -> Optional[structs.CipherSuiteDetails]:
    """Get details for a given cipher suite

    Arguments:
        cipher_suite: The given cipher suite.

    Returns:
        The structure with the detailed info regarding the given cipher suite.
    """

    cs = mappings.supported_cipher_suites.get(cipher_suite)
    if cs is None:
        return None

    ciph = mappings.supported_ciphers[cs.cipher]
    key = mappings.key_exchange.get(cs.key_ex)
    if key is not None:
        key_ex_supp = key.key_ex_supported

    else:
        key_ex_supp = False

    mac_struct = mappings.supported_macs.get(cs.mac)

    return structs.CipherSuiteDetails(
        cipher_suite=cipher_suite,
        full_hs=(key_ex_supp and ciph.cipher_supported),
        key_exchange_supported=key_ex_supp,
        key_algo=cs.key_ex,
        key_algo_struct=key,
        cipher=cs.cipher,
        cipher_struct=ciph,
        mac=cs.mac,
        mac_struct=mac_struct,
    )


def filter_cipher_suites(
    cs_list: List[tls.CipherSuite],
    key_exch: Optional[List[tls.KeyExchangeType]] = None,
    key_auth: Optional[List[tls.KeyAuthentication]] = None,
    key_algo: Optional[List[tls.KeyExchangeAlgorithm]] = None,
    cipher_type: Optional[List[tls.CipherType]] = None,
    cipher_prim: Optional[List[tls.CipherPrimitive]] = None,
    cipher: Optional[List[tls.SymmetricCipher]] = None,
    mac: Optional[List[tls.HashPrimitive]] = None,
    version: Optional[tls.Version] = None,
    full_hs: Optional[bool] = None,
    key_exchange_supported: Optional[bool] = None,
    remove: bool = False,
) -> List[tls.CipherSuite]:
    """Filters a list of cipher suites.

    Various match conditions can be specified. A cipher suite is filtered, if all
    given conditions match (AND-logic). All filtered cipher suites are returned in
    a list.

    Arguments:
        cs_list: A list of cipher suites to be filtered.
        key_algo: Optional match condition. If the key_algo (a combination of
            key_exch and key_auth, e.g. "DHE_RSA") of a cipher suite is in the
            given list, it is a match.
        key_exch: Optional match condition. If the key_exch (e.g. "ECDH") of a
            cipher suite is in the given list, it is a match.
        key_auth: Optional match condition. If the key_auth (e.g. "ECDSA") of a
            cipher suite is in the given list, it is a match.
        cipher_type: Optional match condition. If the cipher_type (e.g.
            "STREAM") of a cipher suite is in the list, it is a match.
        cipher_prim: Optional match condition. If the cipher_prim (e.g. "AES")
            of a cipher suite is in the given list, it is a match.
        cipher: Optional match condition. If the cipher (e.g. "AES_256_CCM_8")
            of a cipher suite is in the given list, it is a match.
        mac: Optional match condition. If the mac (e.g. "SHA384") of a cipher
            suite is in the give list, it is a match.
        version: Optional match condition. Cipher suites supported by the given
            TLS version are a match. This is rather rudimentary implemented:
            AEAD ciphers only for TLS1.2, specific ciphers only for TLS1.3.
        full_hs: Optional match condition. If the implementation supports a
            full handshake with a cipher suite, i.e. an encrypted connection
            can successfully established, it is a match. It means the key
            exchange, the symmetric cipher and the hash primitive are all
            supported.
        key_exchange_supported: Optional match condition. If the key exchange
            for a cipher suite is supported, it is a match. Note, that this
            does not mean that the symmetric cipher is supported as well.
        remove: An indication if the filtered cipher suites shall be removed
            from the original list of cipher suites. Defaults to False.

    Returns:
        The list of cipher suites that match all the given conditions.
    """

    filter_funcs = []
    if key_algo is not None:
        filter_funcs.append(lambda cs: cs.key_algo in key_algo)  # type: ignore

    if key_exch is not None:
        filter_funcs.append(
            lambda cs: getattr(cs.key_algo_struct, "key_ex_type", None)
            in key_exch  # type: ignore
        )

    if key_auth is not None:
        filter_funcs.append(
            lambda cs: getattr(cs.key_algo_struct, "key_auth", None)
            in key_auth  # type: ignore
        )

    if cipher_type is not None:
        filter_funcs.append(
            lambda cs: getattr(cs.cipher_struct, "c_type", None)
            in cipher_type  # type: ignore
        )

    if cipher_prim is not None:
        filter_funcs.append(
            lambda cs: getattr(cs.cipher_struct, "primitive", None)
            in cipher_prim  # type: ignore
        )

    if cipher is not None:
        filter_funcs.append(lambda cs: cs.cipher in cipher)  # type: ignore

    if mac is not None:
        filter_funcs.append(lambda cs: cs.mac in mac)  # type: ignore

    if version in [tls.Version.SSL30, tls.Version.TLS10, tls.Version.TLS11]:
        filter_funcs.append(
            lambda cs: cs.key_algo is not tls.KeyExchangeAlgorithm.TLS13_KEY_SHARE
            and (
                cs.cipher_struct is None
                or cs.cipher_struct.c_type is not tls.CipherType.AEAD
            )
        )

    if version is tls.Version.TLS12:
        filter_funcs.append(
            lambda cs: cs.key_algo is not tls.KeyExchangeAlgorithm.TLS13_KEY_SHARE
        )

    if version is tls.Version.TLS13:
        filter_funcs.append(
            lambda cs: cs.key_algo is tls.KeyExchangeAlgorithm.TLS13_KEY_SHARE
        )

    if full_hs is not None:
        filter_funcs.append(lambda cs: cs.full_hs is full_hs)

    if key_exchange_supported is not None:
        filter_funcs.append(
            lambda cs: cs.key_exchange_supported is key_exchange_supported
        )

    if tls.CipherSuite.TLS_FALLBACK_SCSV in cs_list:
        cs_list.remove(tls.CipherSuite.TLS_FALLBACK_SCSV)

    if tls.CipherSuite.TLS_EMPTY_RENEGOTIATION_INFO_SCSV in cs_list:
        cs_list.remove(tls.CipherSuite.TLS_EMPTY_RENEGOTIATION_INFO_SCSV)

    filtered = []
    for cs in cs_list:
        cs_details = get_cipher_suite_details(cs)
        if cs_details is None:
            continue

        match = True
        for filt_func in filter_funcs:
            if not filt_func(cs_details):
                match = False
                break

        if match:
            filtered.append(cs)

    if remove:
        for cs in filtered:
            cs_list.remove(cs)

    return filtered


def int_to_bytes(number: int) -> bytes:
    """Convert an integer to a byte string

    Arguments:
        number: the integer to convert

    Returns:
        just as many bytes as needed to represent the integer as an octet string
    """

    if number:
        return number.to_bytes((number.bit_length() + 7) // 8, "big")

    else:
        return b"\0"


def set_logging_format() -> None:
    """Initializes the format of log messages
    """

    logging.basicConfig(format="%(levelname)s: %(message)s")


def set_logging_level(level: str) -> None:
    """Sets the logging level

    Arguments:
        level: The logging level to use.
    """

    logging.getLogger().setLevel(level.upper())


class Log(object):
    """A class which implements relative time stamps.
    """

    start_time = None

    @classmethod
    def time(cls) -> str:
        """returns a time stamp relative to the time of the first call to this method.

        Returns:
            the time in seconds with 3 positions after the decimal point.
        """

        timestamp = time.time()
        if cls.start_time is None:
            cls.start_time = timestamp

        diff = timestamp - cls.start_time
        return f"Timestamp {diff:.3f}"


class Table(object):
    """Helper class for printing text in a table

    Attributes:
        indent: the indentation level, i.e. how many blanks shall be added on
            the left side of the table
        sep: the separator to print between adjacent columns within a row
    """

    def __init__(self, indent: int = 0, sep: str = ": ") -> None:
        self._indent = indent
        self._sep = sep
        self._nbr_columns = 0
        self._rows: List[List[Tuple[str, int]]] = []

    def row(self, *args: Union[Tuple[str, int], str]) -> None:
        """Register a row

        Arguments:
            args: a complete row, one string for each column
        """
        self._nbr_columns = max(self._nbr_columns, len(args))
        cols = [col if type(col) is tuple else (col, len(col)) for col in args]
        self._rows.append(cols)  # type: ignore

    def dump(self) -> None:
        """Print the table
        """

        if not self._nbr_columns:
            return

        cols = [1] * self._nbr_columns
        for row in self._rows:
            for idx, col in enumerate(row):
                cols[idx] = max(cols[idx], col[1])

        cols[-1] = 1
        for row in self._rows:
            print(" " * self._indent, end="")
            print(
                self._sep.join(
                    [
                        f"{col[0]:{cols[idx] + len(col[0]) - col[1]}}"
                        for idx, col in enumerate(row)
                    ]
                )
            )


def get_random_value() -> bytes:
    """Get a value suitable for a ClientHello or ServerHello

    Returns:
        32 bytes of almost random data
    """

    random = bytearray()
    random.extend(pdu.pack_uint32(int(time.time())))
    random.extend(os.urandom(28))
    return random


def exit_with_error(error: str) -> None:
    """Abort tlsmate with an error message

    Arguments:
        error: the error message to print on stderr
    """

    sys.stderr.write(f"Error: {error}\n")
    sys.stderr.flush()
    sys.exit(1)
