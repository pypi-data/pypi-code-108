# -*- coding: utf-8 -*-
"""Module scanning for CBC padding oracle vulnerabilities

Specifically, we will scan for the following vulnerabilities:

    * POODLE
        In SSL30, the content of the padding bytes was not specified. Resolved with
        TLS1.0. Scanning for POODLE is not required, just check if SSL30 is enabled
        with at least one CBC-cipher suite.

    * TLS POODLE
        Padding bits are not checked, even for TLS1.0 and above.
        We will only scan for the handshake protocol (Finished), as there are
        implementations in the wild, where AppData are not affected.
        We won't scan every cipher suite, but we do scan each TLS protocol version.
        There are implementations, which check only certain bits of the padding, we
        regard those implementations as vulnerable to TLS POODLE as well, although for
        (SSL) POODLE, no bits are checked at all.

    * Lucky-Minus-20 (aka. OpenSSL Padding Oracle vuln.): CVE-2016-2107
        padding length spans the complete record, so that there is no "room" for the
        MAC and the data
        vector: no data, no mac, valid padding
        fingerprint: server responds with RECORD_OVERFLOW-Alert
        - https://web-in-security.blogspot.com/2016/05/curious-padding-oracle-in-openssl-cve.html  # noqa
        - https://blog.cloudflare.com/yet-another-padding-oracle-in-openssl-cbc-ciphersuites/  # noqua

For other CBC padding oracle vulnerabilities the definition is not exactly
clear (to me).
This includes:

    * Zombie POODLE: The researcher says, an alert is sent in case the padding is
      correct, but the MAC is not. What, if instead of an alert the TCP connection
      is closed or reset? Still Zombie POODLE?
    * GOLDENDOODLE: Similar question here: What, if an implementation checks only
      dedicated bits of the mac? Still GOLDENDOODLE?
    * Sleeping POODLE: Is any different behavior for the different TLS records protocols
      considered as sleeping, or are there specific patterns?
    * 0-length Openssl vulnerability (CVE-2019-1559)
      vector: no data, invalid mac, valid padding
      fingerprint: Hm, according to
      https://www.usenix.org/system/files/sec19-merget.pdf, the typical behaviour
      is a timeout on the server (after sending two Alerts), but SSLLABS seems to
      consider any other distinguishable behavior as well.

    As it is not exactly defined which fingerprints are related to which vulnerability,
    we will use the following approach:

    Base reference is https://www.usenix.org/system/files/sec19-merget.pdf.
    We will use the four vectors #6, #7, #8, #11 from table 1. If there is any
    difference in the response, we will in addition use #17 and a vector where each
    bit of the MAC is flipped as a reference.

    We will report, if oracles are detected for #6, #7, #8, #11. For each
    cipher suite fingerprint we will list the affected (version, cipher suite,
    protocol) combination, the exploitability (visible or not), and the strength
    (based on #17).
"""
# import basic stuff
from typing import NamedTuple, Callable
import enum
import logging

# import own stuff
import tlsmate.msg as msg
import tlsmate.pdu as pdu
import tlsmate.plugin as plg
import tlsmate.server_profile as server_profile
import tlsmate.tls as tls
import tlsmate.utils as utils

# import other stuff


class _ResponseEvent(tls.ExtendedEnum):
    ALERT = enum.auto()
    MSG = enum.auto()
    TIMEOUT = enum.auto()
    TCP_CLOSE = enum.auto()
    TCP_RESET = enum.auto()


class _ResponseFingerprint(object):
    def __init__(self, version, cipher_suite):
        self.events = []
        self.version = version
        self.cipher_suite = cipher_suite

    def add_event(self, event, data=None):
        self.events.append((event, data))

    def __eq__(self, other):
        return self.events == other.events

    def __ne__(self, other):
        return not self.__eq__(other)

    def visible_difference(self, other):
        if len(self.events) != len(other.events):
            return True
        return any(i[0] != j[0] for i, j in zip(self.events, other.events))

    def __str__(self):
        parts = []
        for event, info in self.events:
            if event is _ResponseEvent.ALERT:
                parts.append(f"A({info.value})")
            elif event is _ResponseEvent.MSG:
                parts.append(f"M({info})")
            elif event is _ResponseEvent.TIMEOUT:
                parts.append("T")
            elif event is _ResponseEvent.TCP_CLOSE:
                parts.append("C")
            elif event is _ResponseEvent.TCP_RESET:
                parts.append("R")
        return "".join(parts)


class CipherSuiteFingerprint(object):
    def __init__(self):
        self.strong = tls.ScanState.UNDETERMINED
        self.observable = tls.ScanState.UNDETERMINED
        self.oracle_types = []

    def get_fingerprint_id(self):
        return hash((self.strong, self.observable, tuple(self.oracle_types)))


class _RecordLayerCallbacks(NamedTuple):
    data: Callable
    mac: Callable
    padding: Callable


class _Accuracy(NamedTuple):
    accuracy: tls.OracleScanAccuracy
    all_cs: bool
    all_protocols: bool


# basic modifications


def _raw_bytes(bytestring):
    def cb(data):
        return bytestring

    return cb


def _xor_byte(pos, val):
    def cb(data):
        data[pos] = data[pos] ^ val
        return data

    return cb


def _flip_all_bits():
    def cb(data):
        return bytes([x ^ 0xFF for x in data])

    return cb


# padding modifications


def _padding_valid(length):
    def cb(padding):
        return pdu.pack_uint8(length - 1) * length

    return cb


def _padding_flip_msb(block_size):
    def cb(padding):
        if padding == b"\0":
            padding = pdu.pack_uint8(block_size) * (block_size + 1)

        padding[0] = padding[0] ^ 0x80
        return padding

    return cb


# definition of test vectors


def _vector_invalid_mac(block_size, mac_len):
    """Vector used to determine the invalid MAC behaviour as a reference."""

    return _RecordLayerCallbacks(data=None, mac=_flip_all_bits(), padding=None)


def _vector_tls_poodle(block_size, mac_len):
    """Vector to check for TLS POODLE.

    Valid data, valid MAC, MSB of padding invalid
    """

    return _RecordLayerCallbacks(
        data=None, mac=None, padding=_padding_flip_msb(block_size)
    )


def _vector_6_padding_fills_record(block_size, mac_len):
    """Padding length equal to record length

    Reference: https://www.usenix.org/system/files/sec19-merget.pdf,
    malformed record #6
    """

    return _RecordLayerCallbacks(
        data=_raw_bytes(b""), mac=_raw_bytes(b""), padding=_raw_bytes(b"\x4f" * 80)
    )


def _vector_7_padding_overflow(block_size, mac_len):
    """Padding length exceeds record length

    Reference: https://www.usenix.org/system/files/sec19-merget.pdf,
    malformed record #7
    """

    return _RecordLayerCallbacks(
        data=_raw_bytes(b""), mac=_raw_bytes(b""), padding=_raw_bytes(b"\xff" * 80)
    )


def _vector_8_invalid_padding_bit(block_size, mac_len):
    """No data, valid MAC, first padding bit flipped

    Reference: https://www.usenix.org/system/files/sec19-merget.pdf,
    malformed record #8
    """

    pad_len = 80 - mac_len
    pad_val = pad_len - 1
    padding = pdu.pack_uint8(pad_val ^ 0x80) + pdu.pack_uint8(pad_val) * pad_val

    return _RecordLayerCallbacks(
        data=_raw_bytes(b""), mac=None, padding=_raw_bytes(padding)
    )


def _vector_11_no_data_invalid_mac_msb(block_size, mac_len):
    """No data, first bit of mac flipped, valid padding

    Reference: https://www.usenix.org/system/files/sec19-merget.pdf,
    malformed record #11
    """

    return _RecordLayerCallbacks(
        data=_raw_bytes(b""),
        mac=_xor_byte(0, 0x80),
        padding=_padding_valid(80 - mac_len),
    )


def _vector_17_invalid_short_padding_msb(block_size, mac_len):
    """Data present, mac valid, 6 bytes padding, first bit flipped

    Reference: https://www.usenix.org/system/files/sec19-merget.pdf,
    malformed record #17
    """

    data_len = 80 - mac_len - 6
    return _RecordLayerCallbacks(
        data=_raw_bytes(b" " * data_len),
        mac=None,
        padding=_padding_flip_msb(block_size),
    )


class ScanPaddingOracle(plg.Worker):
    name = "scan_padding_oracles"
    descr = "scan for CBC padding oracles"
    prio = 40

    accuracy_map = {
        "low": _Accuracy(
            accuracy=tls.OracleScanAccuracy.LOW, all_cs=False, all_protocols=False,
        ),
        "medium": _Accuracy(
            accuracy=tls.OracleScanAccuracy.MEDIUM, all_cs=True, all_protocols=False,
        ),
        "high": _Accuracy(
            accuracy=tls.OracleScanAccuracy.HIGH, all_cs=True, all_protocols=True,
        ),
    }

    @staticmethod
    def _response_fingerprint(conn):
        fp = _ResponseFingerprint(conn.version, conn.cipher_suite)
        done = False
        while not done:
            try:
                rec_msg = conn.wait(msg.Any, timeout=1000, fail_on_timeout=False)
                if rec_msg is None:
                    fp.add_event(_ResponseEvent.TIMEOUT)
                    done = True

                else:
                    if isinstance(rec_msg, msg.Alert):
                        fp.add_event(_ResponseEvent.ALERT, rec_msg.description)

                    else:
                        fp.add_event(_ResponseEvent.MSG, rec_msg.msg_type)

            except tls.TlsConnectionClosedError as exc:
                if exc.exc is None:
                    fp.add_event(_ResponseEvent.TCP_CLOSE)

                else:
                    fp.add_event(_ResponseEvent.TCP_RESET)

                done = True

        return fp

    @staticmethod
    def _handshake_scenario(conn, vector):
        conn.send(msg.ClientHello)
        conn.wait(msg.ServerHello)
        conn.wait(msg.Certificate, optional=True)
        conn.wait(msg.ServerKeyExchange, optional=True)
        cert_req = conn.wait(msg.CertificateRequest, optional=True)
        conn.wait(msg.ServerHelloDone)
        if cert_req:
            conn.send(msg.Certificate)

        conn.send(msg.ClientKeyExchange)
        if cert_req:
            conn.send(msg.CertificateVerify)

        conn.send(msg.ChangeCipherSpec)

        callback = vector(
            conn.cs_details.cipher_struct.block_size, conn.cs_details.mac_struct.mac_len
        )
        conn.send(
            msg.Finished,
            data_cb=callback.data,
            mac_cb=callback.mac,
            padding_cb=callback.padding,
        )

    @staticmethod
    def _app_data_scenario(conn, vector):
        conn.handshake()

        callback = vector(
            conn.cs_details.cipher_struct.block_size, conn.cs_details.mac_struct.mac_len
        )
        conn.send(
            msg.AppData(b""),
            data_cb=callback.data,
            mac_cb=callback.mac,
            padding_cb=callback.padding,
        )

    @staticmethod
    def _alert_scenario(conn, vector):
        conn.handshake()
        callback = vector(
            conn.cs_details.cipher_struct.block_size, conn.cs_details.mac_struct.mac_len
        )
        conn.send(
            msg.Alert(
                level=tls.AlertLevel.WARNING,
                description=tls.AlertDescription.CLOSE_NOTIFY,
            ),
            data_cb=callback.data,
            mac_cb=callback.mac,
            padding_cb=callback.padding,
        )

    def _vector_fingerprint(self, protocol, vector):
        with self.client.create_connection() as conn:
            if protocol is tls.ContentType.HANDSHAKE:
                self._handshake_scenario(conn, vector)

            elif protocol is tls.ContentType.APPLICATION_DATA:
                self._app_data_scenario(conn, vector)

            elif protocol is tls.ContentType.ALERT:
                self._alert_scenario(conn, vector)

            return self._response_fingerprint(conn)
        return None

    def _store_cs_fingerprint(self, fp, version, cipher_suite, protocol):
        fp_id = fp.get_fingerprint_id()
        if fp_id not in self.fingerprints:
            self.fingerprints[fp_id] = {"fp": fp, "entries": []}
        self.fingerprints[fp_id]["entries"].append((version, cipher_suite, protocol))

    def _scan_record_protocol(self, protocol):
        cs_fp = CipherSuiteFingerprint()
        fps = [
            self._vector_fingerprint(protocol, vector)
            for vector in [
                _vector_6_padding_fills_record,
                _vector_7_padding_overflow,
                _vector_8_invalid_padding_bit,
                _vector_11_no_data_invalid_mac_msb,
            ]
        ]
        (
            fp_6_padding_fills_record,
            fp_7_padding_overflow,
            fp_8_padding_invalid_padding_bit,
            fp_11_padding_no_data_invalid_mac_msb,
        ) = fps
        logging.debug(f"fp_6_padding_fills_record {fp_6_padding_fills_record}")
        logging.debug(f"fp_7_padding_overflow {fp_7_padding_overflow}")
        logging.debug(
            f"fp_8_padding_invalid_padding_bit {fp_8_padding_invalid_padding_bit}"
        )
        logging.debug(
            f"fp_11_padding_no_data_invalid_mac_msb "
            f"{fp_11_padding_no_data_invalid_mac_msb}"
        )
        if not all(fps):
            return

        if not all(x == fps[0] for x in fps):
            fp_invalid_mac = self._vector_fingerprint(protocol, _vector_invalid_mac)
            logging.debug(f"fp_invalid_mac: {fp_invalid_mac}")
            if not fp_invalid_mac:
                return

            if (
                fp_6_padding_fills_record != fp_invalid_mac
                and fp_6_padding_fills_record.events[0][1]
                is tls.AlertDescription.RECORD_OVERFLOW
            ):
                cs_fp.oracle_types.append(tls.SPCbcPaddingOracle.LUCKY_MINUS_20)
                self.lucky_minus_20 = True

            else:
                if fp_6_padding_fills_record != fp_invalid_mac:
                    cs_fp.oracle_types.append(
                        tls.SPCbcPaddingOracle.PADDING_FILLS_RECORD
                    )

                if fp_7_padding_overflow != fp_invalid_mac:
                    cs_fp.oracle_types.append(
                        tls.SPCbcPaddingOracle.PADDING_EXCEEDS_RECORD
                    )

            if fp_8_padding_invalid_padding_bit != fp_invalid_mac:
                cs_fp.oracle_types.append(tls.SPCbcPaddingOracle.INVALID_PADDING)

            if fp_11_padding_no_data_invalid_mac_msb != fp_invalid_mac:
                cs_fp.oracle_types.append(tls.SPCbcPaddingOracle.INVALID_MAC)

            cs_fp.observable = tls.ScanState(
                any(fp_invalid_mac.visible_difference(fp) for fp in fps)
            )
            fp_17_invalid_short_padding_msb = self._vector_fingerprint(
                protocol, _vector_17_invalid_short_padding_msb
            )
            logging.debug(
                f"fp_17_invalid_short_padding_msb {fp_17_invalid_short_padding_msb}"
            )
            if not fp_17_invalid_short_padding_msb:
                cs_fp.strong = tls.ScanState.UNDETERMINED
            else:
                cs_fp.strong = tls.ScanState(
                    fp_17_invalid_short_padding_msb != fp_invalid_mac
                )

            self._store_cs_fingerprint(
                cs_fp, fp_invalid_mac.version, fp_invalid_mac.cipher_suite, protocol
            )

    def _scan_cipher_suite(self):
        if self.all_protocols:
            self._scan_record_protocol(tls.ContentType.HANDSHAKE)
            self._scan_record_protocol(tls.ContentType.APPLICATION_DATA)
            self._scan_record_protocol(tls.ContentType.ALERT)

        else:
            self._scan_record_protocol(tls.ContentType.APPLICATION_DATA)

    def _tls_poodle_handshake(self):
        fp = self._vector_fingerprint(tls.ContentType.HANDSHAKE, _vector_tls_poodle)
        if fp and fp.events[0][1] is tls.CCSType.CHANGE_CIPHER_SPEC:
            self.tls_poodle = True

    def _scan_version(self, values, tls_poodle=False):
        if values.versions:
            cbc_ciphers = utils.filter_cipher_suites(
                values.cipher_suites, cipher_type=[tls.CipherType.BLOCK], full_hs=True,
            )
            if not cbc_ciphers:
                return

            self.applicable = True
            self.client.init_profile(profile_values=values)
            if tls_poodle:
                self.client.profile.cipher_suites = cbc_ciphers
                self._tls_poodle_handshake()

            else:
                combo_list = []
                for cipher in cbc_ciphers:
                    if not self.all_cs:
                        det = utils.get_cipher_suite_details(cipher)
                        combo = (det.cipher_struct.primitive, det.mac)
                        if combo in combo_list:
                            continue
                        combo_list.append(combo)

                    self.client.profile.cipher_suites = [cipher]
                    self._scan_cipher_suite()

    def _scan_poodle(self):
        values = self.server_profile.get_profile_values([tls.Version.SSL30])
        cbc_ciphers = utils.filter_cipher_suites(
            values.cipher_suites, cipher_type=[tls.CipherType.BLOCK],
        )
        return tls.ScanState(bool(cbc_ciphers))

    def _scan_tls_poodle(self):
        for version in [tls.Version.TLS10, tls.Version.TLS11, tls.Version.TLS12]:
            values = self.server_profile.get_profile_values([version])
            self._scan_version(values, tls_poodle=True)

            if self.tls_poodle:
                break

    def run(self):
        accuracy = self.config.get("oracle_accuracy")
        mapping = self.accuracy_map.get(accuracy, self.accuracy_map["medium"])

        self.accuracy = mapping.accuracy
        self.all_cs = mapping.all_cs
        self.all_protocols = mapping.all_protocols
        self.lucky_minus_20 = False
        self.tls_poodle = False

        self.server_profile.allocate_vulnerabilities()
        self.server_profile.vulnerabilities.poodle = self._scan_poodle()
        self._scan_tls_poodle()
        self.fingerprints = {}
        self.applicable = False
        versions = [tls.Version.TLS10, tls.Version.TLS11, tls.Version.TLS12]
        for version in versions:
            values = self.server_profile.get_profile_values([version])
            self._scan_version(values)

        oracle_info = server_profile.SPCbcPaddingOracleInfo()
        oracle_info.accuracy = self.accuracy
        if not self.applicable:
            tls_poodle = tls.ScanState.NA
            lucky_minus_20 = tls.ScanState.NA
            oracle_info.vulnerable = tls.ScanState.NA

        else:
            tls_poodle = tls.ScanState(self.tls_poodle)
            lucky_minus_20 = tls.ScanState(self.lucky_minus_20)
            oracle_info.vulnerable = tls.ScanState(bool(self.fingerprints))
            oracle_info.oracles = []
            if self.fingerprints:
                for entry in self.fingerprints.values():
                    item = entry["fp"]
                    sp_oracle = server_profile.SPCbcPaddingOracle(
                        observable=item.observable, strong=item.strong
                    )
                    sp_oracle.types = item.oracle_types
                    sp_oracle.cipher_group = [
                        server_profile.SPCipherGroup(
                            version=version,
                            cipher_suite=cipher_suite,
                            record_protocol=protocol,
                        )
                        for version, cipher_suite, protocol in entry["entries"]
                    ]
                    oracle_info.oracles.append(sp_oracle)

        self.server_profile.vulnerabilities.tls_poodle = tls_poodle
        self.server_profile.vulnerabilities.lucky_minus_20 = lucky_minus_20
        self.server_profile.vulnerabilities.cbc_padding_oracle = oracle_info
