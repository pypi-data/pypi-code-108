# -*- coding: utf-8 -*-
"""Implements a class to test the scanner info workers.
"""
import pathlib
import time
import datetime
from tlsmate import tls
from tlsmate import msg
from tlsmate import utils
from tlsmate.plugin import Worker
from tlsmate.workers.scanner_info import ScanStart, ScanEnd
from tlsmate.tlssuite import TlsSuiteTester, TlsLibrary
from tlsmate.version import __version__


def flip_msb(data):
    data[0] = data[0] ^ 0x80
    return data


def flip_lsb(data):
    data[-1] = data[-1] ^ 0x01
    return data


class MalfunctionWorker(Worker):
    name = "server_malfunction"
    prio = 100

    def run(self):
        self.client.set_profile(tls.Profile.INTEROPERABILITY)
        self.client.profile.support_session_id = False
        self.client.profile.support_session_ticket = False
        self.client.profile.versions = [tls.Version.TLS12]
        self.client.profile.cipher_suites = utils.filter_cipher_suites(
            self.client.profile.cipher_suites,
            cipher_type=[tls.CipherType.BLOCK],
            full_hs=True,
        )
        with self.client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            conn.wait(msg.Certificate, optional=True)
            conn.wait(msg.ServerKeyExchange, optional=True)
            conn.wait(msg.ServerHelloDone)
            conn.send(msg.ClientKeyExchange)
            conn.send(msg.ChangeCipherSpec)
            conn.send(msg.Finished)
            conn.wait(msg.ChangeCipherSpec)
            conn.wait(msg.Finished, mac_cb=flip_msb)

        with self.client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            conn.wait(msg.Certificate, optional=True)
            conn.wait(msg.ServerKeyExchange, optional=True)
            conn.wait(msg.ServerHelloDone)
            conn.send(msg.ClientKeyExchange)
            conn.send(msg.ChangeCipherSpec)
            conn.send(msg.Finished)
            conn.wait(msg.ChangeCipherSpec)
            conn.wait(msg.Finished, padding_cb=flip_msb)

        with self.client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            conn.wait(msg.Certificate, optional=True)
            conn.wait(msg.ServerKeyExchange, optional=True)
            conn.wait(msg.ServerHelloDone)
            conn.send(msg.ClientKeyExchange)
            conn.send(msg.ChangeCipherSpec)
            conn.send(msg.Finished)
            conn.wait(msg.ChangeCipherSpec)
            conn.wait(msg.Finished, data_cb=flip_msb)

        with self.client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            conn.wait(msg.Certificate, optional=True)
            conn.wait(msg.ServerKeyExchange, optional=True)
            conn.wait(msg.ServerHelloDone)
            conn.send(msg.ClientKeyExchange)
            conn.send(msg.ChangeCipherSpec)
            conn.send(msg.Finished)
            conn.wait(msg.ChangeCipherSpec)
            conn.wait(msg.Finished, data_cb=flip_lsb)


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_sig_algos_openssl3_0_0"
    recorder_yaml = "recorder_scan_info"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl3_0_0

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        start_timestamp = time.time()
        ScanStart(tlsmate).run()
        MalfunctionWorker(tlsmate).run()
        ScanEnd(tlsmate).run()
        end_timestamp = time.time()
        date = datetime.datetime.fromtimestamp(int(start_timestamp))
        date_str = date.strftime("%Y-%m-%d")
        profile = server_profile.make_serializable()
        assert profile["scan_info"]["version"] == __version__
        assert type(profile["scan_info"]["command"]) == str
        assert profile["scan_info"]["run_time"] < 2
        assert profile["scan_info"]["start_timestamp"] >= start_timestamp
        assert profile["scan_info"]["stop_timestamp"] <= end_timestamp
        assert date_str in profile["scan_info"]["start_date"]
        assert date_str in profile["scan_info"]["stop_date"]

        assert profile["server"]["ip"] == "127.0.0.1"
        assert profile["server"]["sni"] == "localhost"
        assert profile["server"]["port"] == self.config.get("port")
        assert profile["server"]["name_resolution"]["domain_name"] == "localhost"
        assert len(profile["server"]["name_resolution"]["ipv4_addresses"]) == 1
        assert profile["server"]["name_resolution"]["ipv4_addresses"][0] == "127.0.0.1"

        assert (
            profile["server_malfunctions"][0]["issue"]["name"] == "RECORD_MAC_INVALID"
        )
        assert (
            profile["server_malfunctions"][1]["issue"]["name"]
            == "RECORD_WRONG_PADDING_BYTES"
        )
        assert (
            profile["server_malfunctions"][2]["issue"]["name"]
            == "ILLEGAL_PARAMETER_VALUE"
        )
        assert (
            profile["server_malfunctions"][3]["issue"]["name"] == "VERIFY_DATA_INVALID"
        )


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
