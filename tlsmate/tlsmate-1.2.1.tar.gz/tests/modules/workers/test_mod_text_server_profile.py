# -*- coding: utf-8 -*-
"""Implement unit tests for the module utils.
"""
import io
import re
from tlsmate.workers.text_server_profile import (
    FontStyle,
    Color,
    merge_styles,
    get_dict_value,
    get_styled_text,
    TextProfileWorker,
)
from tlsmate import utils
import pytest
import yaml


def test_FontStyle_html():
    FontStyle.html = True
    style = FontStyle(color=Color.GREEN, bold=True)
    txt = "hello word"
    styled_txt = style.decorate(txt)
    assert styled_txt == f"<font color=green><b>{txt}</b></font>"


def test_FontStyle_orig_length():
    FontStyle.html = True
    style = FontStyle(color=Color.GREEN, bold=True)
    txt = "hello word"
    styled_txt = style.decorate(txt, with_orig_len=True)
    assert styled_txt == (f"<font color=green><b>{txt}</b></font>", len(txt))


def test_merge_styles():
    with pytest.raises(ValueError, match="cannot merge styles"):
        merge_styles([])


def test_get_dict_value_no_profile():
    assert get_dict_value(None, default="test") == "test"


def test_get_dict_value_not_found():
    profile = {"there": 0}
    assert get_dict_value(profile, "not_there", default="test") == "test"


def test_get_styled_text():
    FontStyle.html = True
    assert get_styled_text(None) == "<font color=red><b>???</b></font>"


def test_empty_profile(tlsmate, style_file, capsys):
    tlsmate.server_profile.load({})
    tlsmate.config.set("style", str(style_file))
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert "Scanned host" not in captured.out
    assert "TLS protocol versions" not in captured.out
    assert "Cipher suites" not in captured.out
    assert "Supported groups" not in captured.out
    assert "Signature algorithms" not in captured.out
    assert "DH groups (finite field)" not in captured.out
    assert "Features" not in captured.out
    assert "Certificate chains" not in captured.out
    assert "Vulnerabilities" not in captured.out
    assert "Severe server implementation flaws" not in captured.out


def test_only_versions(tlsmate, style_file, capsys):
    FontStyle.html = False
    yaml_data = """
versions:
-   support: UNDETERMINED
    version:
        id: 512
        name: SSL20
"""
    data = yaml.safe_load(io.StringIO(yaml_data))
    tlsmate.server_profile.load(data)
    tlsmate.config.set("style", str(style_file))
    tlsmate.config.set("color", False)
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert "Scanned host" not in captured.out
    assert "Cipher suites" not in captured.out
    assert "Supported groups" not in captured.out
    assert "Signature algorithms" not in captured.out
    assert "DH groups (finite field)" not in captured.out
    assert "Features" not in captured.out
    assert "Certificate chains" not in captured.out
    assert "Vulnerabilities" not in captured.out
    assert "Severe server implementation flaws" not in captured.out


def test_host(tlsmate, style_file, capsys):
    FontStyle.html = False
    yaml_data = """
server:
    ip: 127.0.0.1
    name_resolution:
        domain_name: localhost
        ipv4_addresses:
        - 127.0.0.1
        ipv6_addresses:
        - ff01::0
        - abc0:6432:54af:0:3333:dead:beef:bad
    port: 44330
    sni: localhost
"""
    data = yaml.safe_load(io.StringIO(yaml_data))
    tlsmate.server_profile.load(data)
    tlsmate.config.set("style", str(style_file))
    tlsmate.config.set("color", False)
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert re.match(r".*host +localhost", captured.out, re.DOTALL)
    assert re.match(r".*port +44330", captured.out, re.DOTALL)
    assert re.match(r".*SNI +localhost", captured.out, re.DOTALL)
    assert re.match(r".*IPv4 addresses +127\.0\.0\.1", captured.out, re.DOTALL)


def test_host_no_name_resolution(tlsmate, style_file, capsys):
    FontStyle.html = False
    yaml_data = """
server:
    ip: 127.0.0.1
    port: 44330
    sni: 127.0.0.1
"""
    data = yaml.safe_load(io.StringIO(yaml_data))
    tlsmate.server_profile.load(data)
    tlsmate.config.set("style", str(style_file))
    tlsmate.config.set("color", False)
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert re.match(r".*host +127\.0\.0\.1", captured.out, re.DOTALL)


def test_server_malfunctions(tlsmate, style_file, capsys):
    FontStyle.html = False
    yaml_data = """
server_malfunctions:
-   issue:
        description: 'received Finished: verify data does not match'
        name: VERIFY_DATA_INVALID
-   issue:
        description: 'certificate request without extension SignatureAlgorithms received'
        name: CERT_REQ_NO_SIG_ALGOD
-   issue:
        description: message length incorrect
        name: MESSAGE_LENGTH_ERROR
    message:
        id: 14
        name: SERVER_HELLO_DONE
-   extension:
        id: 23
        name: EXTENDED_MASTER_SECRET
    issue:
        description: extension length incorrect
        name: EXTENTION_LENGHT_ERROR
"""  # noqa
    data = yaml.safe_load(io.StringIO(yaml_data))
    tlsmate.server_profile.load(data)
    tlsmate.config.set("style", str(style_file))
    tlsmate.config.set("color", False)
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert "Severe server implementation flaws" in captured.out
    assert "- received Finished: verify data does not match" in captured.out
    assert (
        "- certificate request without extension SignatureAlgorithms received"
        in captured.out
    )
    assert "- message length incorrect (message: SERVER_HELLO_DONE)" in captured.out
    assert (
        "- extension length incorrect (extension: EXTENDED_MASTER_SECRET)"
        in captured.out
    )


def test_with_compression(tlsmate, style_file, capsys):
    FontStyle.html = False
    yaml_data = """
versions:
-   support: 'TRUE'
    version:
        id: 770
        name: TLS11
    ciphers:
        cipher_suites:
        -   id: 4865
            name: TLS_AES_128_GCM_SHA256
        server_preference: 'FALSE'
features:
    compression:
    -   id: 0
        name: 'NULL'
    -   id: 1
        name: DEFLATE
"""
    data = yaml.safe_load(io.StringIO(yaml_data))
    tlsmate.server_profile.load(data)
    tlsmate.config.set("style", str(style_file))
    tlsmate.config.set("color", False)
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert re.match(r".*compression +supported", captured.out, re.DOTALL)


def test_with_html(tlsmate, style_file, capsys):
    tlsmate.server_profile.load({})
    tlsmate.config.set("style", str(style_file))
    tlsmate.config.set("format", "html")
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert captured.out.startswith("<pre>")
    assert captured.out.endswith("</pre>\n")


def test_without_style(tlsmate):
    tlsmate.server_profile.load({})
    tlsmate.config.set("style", "not_existing_file")
    tlsmate.config.set("format", "text")
    with pytest.raises(FileNotFoundError, match="not_existing_file"):
        TextProfileWorker(tlsmate).run()


def test_server_profile(tlsmate, style_file, capsys, server_profile):
    tlsmate.server_profile.load(utils.deserialize_data(str(server_profile)))
    tlsmate.config.set("style", "not_existing_file")
    tlsmate.config.set("format", "text")
    assert True
