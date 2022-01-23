# -*- coding: utf-8 -*-
"""Implement unit tests for the module utils.
"""
import re
from tlsmate import utils
from tlsmate import tls

data = {
    "array": [1, 2, 3],
    "integer": 4,
    "object": {"a": 1, "b": 2},
    "string": "hello",
}

json = (
    "{\n"
    '    "array": [\n'
    "        1,\n"
    "        2,\n"
    "        3\n"
    "    ],\n"
    '    "integer": 4,\n'
    '    "object": {\n'
    '        "a": 1,\n'
    '        "b": 2\n'
    "    },\n"
    '    "string": "hello"\n'
    "}"
)

yaml = (
    "array:\n"
    "- 1\n"
    "- 2\n"
    "- 3\n"
    "integer: 4\n"
    "object:\n"
    "    a: 1\n"
    "    b: 2\n"
    "string: hello\n"
)


def test_get_random_value():
    val = utils.get_random_value()
    assert type(val) is bytearray
    assert len(val) == 32


def test_serialize_data_file(tmp_path):
    file_name = tmp_path / "output.txt"
    utils.serialize_data(data, file_name)
    content = file_name.read_text()
    assert content == yaml


def test_serialize_data_file_exists(tmp_path, capsys):
    file_name = tmp_path / "output.txt"
    file_name.touch()
    utils.serialize_data(data, file_name, replace=False)
    captured = capsys.readouterr()
    assert re.match(r"File .* existing\. .*-file not generated", captured.out)


def test_serialize_data_file_json(tmp_path):
    file_name = tmp_path / "output.txt"
    utils.serialize_data(data, file_name, use_json=True)
    content = file_name.read_text()
    assert content == json


def test_serialize_data_file_json_console(capsys):
    utils.serialize_data(data, use_json=True)
    captured = capsys.readouterr()
    assert captured.out == json + "\n"


def test_serialize_data_file_yaml_console(capsys):
    utils.serialize_data(data)
    captured = capsys.readouterr()
    assert captured.out == yaml + "\n"


def test_fold_string():
    string = "Hello world, this is a long string! Have fun!"
    assert utils.fold_string(string, 15) == [
        "Hello world, ",
        "this is a long ",
        "string! Have ",
        "fun!",
    ]


def test_filter_cipher_suites_key_exchange_supported():
    cipher_suites = [
        tls.CipherSuite.TLS_KRB5_WITH_DES_CBC_SHA,
        tls.CipherSuite.TLS_RSA_WITH_RC4_128_MD5,
    ]
    assert utils.filter_cipher_suites(cipher_suites, key_exchange_supported=True) == [
        tls.CipherSuite.TLS_RSA_WITH_RC4_128_MD5
    ]


def test_int_to_bytes():
    assert utils.int_to_bytes(0) == b"\0"
    assert utils.int_to_bytes(255) == b"\xff"
    assert utils.int_to_bytes(256) == b"\01\00"


def check_presence(cs_list, string_list):
    for cs in cs_list:
        match = False
        for string in string_list:
            if string in cs.name:
                match = True
                break
        assert match is True


def check_absence(cs_list, string):
    for cs in cs_list:
        assert string not in cs.name


def test_filter_cipher_suites():
    """Simple tests, only one filter condition at once
    """
    cs_all = tls.CipherSuite.all()
    cs_all.remove(tls.CipherSuite.TLS_EMPTY_RENEGOTIATION_INFO_SCSV)
    cs_all.remove(tls.CipherSuite.TLS_FALLBACK_SCSV)

    assert cs_all == utils.filter_cipher_suites(cs_all)

    tls13 = utils.filter_cipher_suites(cs_all, version=tls.Version.TLS13)
    assert set(tls13) == set(
        (
            tls.CipherSuite.TLS_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_AES_256_GCM_SHA384,
            tls.CipherSuite.TLS_CHACHA20_POLY1305_SHA256,
            tls.CipherSuite.TLS_AES_128_CCM_SHA256,
            tls.CipherSuite.TLS_AES_128_CCM_8_SHA256,
        )
    )

    tls12 = utils.filter_cipher_suites(cs_all, version=tls.Version.TLS12)
    assert set(tls12) & set(tls13) == set()
    assert set(tls12) | set(tls13) == set(cs_all)

    tls11 = utils.filter_cipher_suites(cs_all, version=tls.Version.TLS11)
    diff = set(tls12).difference(set(tls11))
    aead = utils.filter_cipher_suites(tls12, cipher_type=[tls.CipherType.AEAD])
    assert diff != set()
    assert set(aead) == set(diff)
    check_presence(aead, ["_GCM_", "_CCM", "_CHACHA20_POLY1305_"])
    check_absence(tls11, "_GCM_")
    check_absence(tls11, "_CCM")
    check_absence(tls11, "_CHACHA20_POLY1305_")

    ecdh_rsa = utils.filter_cipher_suites(
        cs_all, key_algo=[tls.KeyExchangeAlgorithm.ECDH_RSA], remove=True
    )
    check_presence(ecdh_rsa, ["_ECDH_RSA_"])
    check_absence(cs_all, "_ECDH_RSA_")

    cs_all = tls.CipherSuite.all()
    dh = utils.filter_cipher_suites(
        cs_all, key_exch=[tls.KeyExchangeType.DH], remove=True
    )
    check_presence(dh, ["_DH_", "_DHE_"])
    check_absence(cs_all, "_DH_")
    check_absence(cs_all, "_DHE_")

    cs_all = tls.CipherSuite.all()
    ecdsa = utils.filter_cipher_suites(
        cs_all, key_auth=[tls.KeyAuthentication.ECDSA], remove=True
    )
    check_presence(ecdsa, ["_ECDSA_"])
    check_absence(cs_all, "_ECDSA_")

    cs_all = tls.CipherSuite.all()
    ecdsa = utils.filter_cipher_suites(
        cs_all, cipher=[tls.SymmetricCipher.AES_128_CBC], remove=True
    )
    check_presence(ecdsa, ["_AES_128_CBC_"])
    check_absence(cs_all, "_AES_128_CBC_")

    cs_all = tls.CipherSuite.all()
    ecdsa = utils.filter_cipher_suites(
        cs_all, cipher_prim=[tls.CipherPrimitive.ARIA], remove=True
    )
    check_presence(ecdsa, ["_WITH_ARIA_"])
    check_absence(cs_all, "_WITH_ARIA_")

    cs_all = tls.CipherSuite.all()
    sha384 = utils.filter_cipher_suites(
        cs_all, mac=[tls.HashPrimitive.SHA384], remove=True
    )
    check_presence(sha384, ["_SHA384"])
    check_absence(cs_all, "_SHA384")

    cs_all = tls.CipherSuite.all()
    cs_all.remove(tls.CipherSuite.TLS_EMPTY_RENEGOTIATION_INFO_SCSV)
    cs_all.remove(tls.CipherSuite.TLS_FALLBACK_SCSV)
    cs_all2 = cs_all[:]
    full_hs = utils.filter_cipher_suites(cs_all, full_hs=True, remove=True)
    not_full_hs = utils.filter_cipher_suites(cs_all2, full_hs=False, remove=True)
    assert set(full_hs) != set()
    assert not_full_hs != set()
    assert cs_all == not_full_hs
    assert cs_all2 == full_hs
