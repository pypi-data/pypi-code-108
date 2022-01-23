# -*- coding: utf-8 -*-
"""Implement unit tests for the module utils.
"""
from tlsmate import tls
from tlsmate import msg
from tlsmate import utils
import pytest


def test_message_length_error():
    data = bytes.fromhex("01 00 00 02 01")
    with pytest.raises(
        tls.ServerMalfunction, match=tls.ServerIssue.MESSAGE_LENGTH_ERROR.value
    ):
        msg.HandshakeMessage.deserialize(data, None)


def test_hello_reques_wrong_length():
    data = bytes.fromhex("00 00 00 02  01 02")
    with pytest.raises(
        tls.ServerMalfunction, match=tls.ServerIssue.MESSAGE_LENGTH_ERROR.value
    ):
        msg.HandshakeMessage.deserialize(data, None)


def test_decode_hello_retry_request():
    data = bytes.fromhex(
        "02 00 00 3d 03 03 CF 21 AD 74 E5 9A 61 11 BE 1D "
        "8C 02 1E 65 B8 91 C2 A2 11 16 7A BB 8C 5E 07 9E "
        "09 E2 C8 A8 33 9C 00 c0 2f 00 00 15 00 00 00 00 "
        "ff 01 00 01 00 00 0b 00 04 03 00 01 02 00 23 00 "
        "00 "
    )
    message = msg.HandshakeMessage.deserialize(data, None)
    assert type(message) is msg.HelloRetryRequest
    assert message.msg_type is tls.HandshakeType.HELLO_RETRY_REQUEST


def test_certificate_request_context(monkeypatch, tlsmate):

    conn = tlsmate.client.create_connection()
    conn.version = tls.Version.TLS13

    data = bytes.fromhex(
        "0b 00 06 c5  03 aa bb cc  00 06 be 00 03 56 30 82 03 52 30 "
        "82 02 d8 a0 03 02 01 02 02 08 08 a6 0c e9 5f 7f "
        "3a f9 30 0a 06 08 2a 86 48 ce 3d 04 03 02 30 55 "
        "31 0b 30 09 06 03 55 04 06 13 02 44 45 31 1c 30 "
        "1a 06 03 55 04 0a 0c 13 54 68 65 20 54 6c 73 4d "
        "61 74 65 20 43 6f 6d 70 61 6e 79 31 28 30 26 06 "
        "03 55 04 03 0c 1f 6c 6f 63 61 6c 68 6f 73 74 20 "
        "49 6e 74 65 72 6d 65 64 69 61 74 65 20 43 41 20 "
        "45 43 44 53 41 30 1e 17 0d 32 31 31 30 32 34 31 "
        "35 35 32 30 38 5a 17 0d 33 31 31 30 32 32 31 35 "
        "35 32 30 38 5a 30 53 31 0b 30 09 06 03 55 04 06 "
        "13 02 44 45 31 30 30 2e 06 03 55 04 0a 0c 27 54 "
        "68 65 20 54 6c 73 4d 61 74 65 20 43 6f 6d 70 61 "
        "6e 79 20 28 53 65 72 76 65 72 20 73 69 64 65 29 "
        "20 45 43 44 53 41 31 12 30 10 06 03 55 04 03 0c "
        "09 6c 6f 63 61 6c 68 6f 73 74 30 76 30 10 06 07 "
        "2a 86 48 ce 3d 02 01 06 05 2b 81 04 00 22 03 62 "
        "00 04 9a ed 29 5e b4 61 9d 2a 33 0d dc 6c 3a a4 "
        "77 c4 7b 2b a9 2b 5f 3e 10 bf 10 96 e9 12 4b 8f "
        "1a 23 f3 ce 00 e7 33 d1 33 c5 a8 fb b5 9f e9 ab "
        "6b 31 30 f2 e4 a1 aa 3d 0b 97 9a 2b 94 2d 5b 96 "
        "30 b4 6a 45 2f 38 a0 4e 55 70 b7 15 17 07 4c 87 "
        "72 40 61 4e 19 85 c1 c7 f3 b7 a1 25 d5 cf 44 ca "
        "23 e7 a3 82 01 75 30 82 01 71 30 0c 06 03 55 1d "
        "13 01 01 ff 04 02 30 00 30 2f 06 03 55 1d 11 04 "
        "28 30 26 82 0e 74 65 73 74 2e 6c 6f 63 61 6c 68 "
        "6f 73 74 82 14 2a 2e 77 69 6c 64 63 61 72 64 2e "
        "6c 6f 63 61 6c 68 6f 73 74 30 13 06 03 55 1d 25 "
        "04 0c 30 0a 06 08 2b 06 01 05 05 07 03 01 30 1d "
        "06 03 55 1d 0e 04 16 04 14 08 31 a9 8a 73 b8 b2 "
        "20 8e ea cf 9e c2 92 b9 1d ff 17 83 61 30 1f 06 "
        "03 55 1d 23 04 18 30 16 80 14 ed 0f 4f b8 b9 0e "
        "4e e5 a8 70 07 a1 ea 83 8d 8d e2 d9 6d f9 30 72 "
        "06 08 2b 06 01 05 05 07 01 01 04 66 30 64 30 39 "
        "06 08 2b 06 01 05 05 07 30 02 86 2d 68 74 74 70 "
        "3a 2f 2f 63 72 74 2e 6c 6f 63 61 6c 68 6f 73 74 "
        "3a 34 34 34 30 30 2f 63 65 72 74 73 2f 63 61 2d "
        "65 63 64 73 61 2e 63 72 74 30 27 06 08 2b 06 01 "
        "05 05 07 30 01 86 1b 68 74 74 70 3a 2f 2f 6f 63 "
        "73 70 2e 6c 6f 63 61 6c 68 6f 73 74 3a 34 34 34 "
        "30 32 30 3c 06 03 55 1d 1f 04 35 30 33 30 31 a0 "
        "2f a0 2d 86 2b 68 74 74 70 3a 2f 2f 63 72 6c 2e "
        "6c 6f 63 61 6c 68 6f 73 74 3a 34 34 34 30 30 2f "
        "63 72 6c 2f 63 61 2d 65 63 64 73 61 2e 63 72 6c "
        "30 13 06 03 55 1d 20 04 0c 30 0a 30 08 06 06 67 "
        "81 0c 01 02 01 30 14 06 08 2b 06 01 05 05 07 01 "
        "18 04 08 30 06 02 01 05 02 01 11 30 0a 06 08 2a "
        "86 48 ce 3d 04 03 02 03 68 00 30 65 02 30 6f 2c "
        "24 3a 7f 92 95 cc 67 27 c2 12 2e 60 bb 09 b2 ee "
        "03 eb 5a 6e 71 4c 88 35 f9 a4 cc 12 db 8e 73 05 "
        "da 8d de 15 72 ef bf 90 4f 91 8b 2d cf 87 02 31 "
        "00 b2 41 85 7d ef cf eb b1 1d 27 16 32 5f c2 e1 "
        "6a 32 a8 ae 98 b5 c0 87 74 54 5c 20 4d 69 59 d8 "
        "d1 3a 19 89 52 aa 2f 0f 05 4a cf cf 42 6e 34 41 "
        "a1 00 00 00 03 5e 30 82 03 5a 30 82 02 e1 a0 03 "
        "02 01 02 02 08 05 3f 15 f5 b0 b8 c5 50 30 0a 06 "
        "08 2a 86 48 ce 3d 04 03 02 30 4d 31 0b 30 09 06 "
        "03 55 04 06 13 02 44 45 31 1c 30 1a 06 03 55 04 "
        "0a 0c 13 54 68 65 20 54 6c 73 4d 61 74 65 20 43 "
        "6f 6d 70 61 6e 79 31 20 30 1e 06 03 55 04 03 0c "
        "17 6c 6f 63 61 6c 68 6f 73 74 20 52 6f 6f 74 20 "
        "43 41 20 45 43 44 53 41 30 1e 17 0d 32 31 31 30 "
        "32 34 31 35 35 32 30 38 5a 17 0d 33 31 31 30 32 "
        "32 31 35 35 32 30 38 5a 30 55 31 0b 30 09 06 03 "
        "55 04 06 13 02 44 45 31 1c 30 1a 06 03 55 04 0a "
        "0c 13 54 68 65 20 54 6c 73 4d 61 74 65 20 43 6f "
        "6d 70 61 6e 79 31 28 30 26 06 03 55 04 03 0c 1f "
        "6c 6f 63 61 6c 68 6f 73 74 20 49 6e 74 65 72 6d "
        "65 64 69 61 74 65 20 43 41 20 45 43 44 53 41 30 "
        "76 30 10 06 07 2a 86 48 ce 3d 02 01 06 05 2b 81 "
        "04 00 22 03 62 00 04 2c 37 11 38 3e 2b 31 35 1f "
        "9c ab e4 28 e7 35 32 8b 78 3c dc f6 e3 13 be aa "
        "50 cc 0e cb 7d a4 a5 de fe d9 9b f6 44 7a 53 80 "
        "cc e1 c8 98 44 23 0f ed 17 00 70 42 ad 2f 4e 66 "
        "73 9f 5e c6 82 7a 6b bd 0d 04 c4 8f 7c 0a 64 58 "
        "a1 fd d7 bd f1 bd 31 67 5d ee 06 f9 4c a1 9b ac "
        "c9 00 cc de e9 c0 49 a3 82 01 84 30 82 01 80 30 "
        "12 06 03 55 1d 13 01 01 ff 04 08 30 06 01 01 ff "
        "02 01 00 30 0e 06 03 55 1d 0f 01 01 ff 04 04 03 "
        "02 01 06 30 1d 06 03 55 1d 0e 04 16 04 14 ed 0f "
        "4f b8 b9 0e 4e e5 a8 70 07 a1 ea 83 8d 8d e2 d9 "
        "6d f9 30 1f 06 03 55 1d 23 04 18 30 16 80 14 18 "
        "61 69 ff 74 2d f6 44 ba dc 14 fd 04 00 55 48 b9 "
        "f9 98 5a 30 74 06 08 2b 06 01 05 05 07 01 01 04 "
        "68 30 66 30 3b 06 08 2b 06 01 05 05 07 30 02 86 "
        "2f 68 74 74 70 3a 2f 2f 63 72 74 2e 6c 6f 63 61 "
        "6c 68 6f 73 74 3a 34 34 34 30 30 2f 63 65 72 74 "
        "73 2f 72 6f 6f 74 2d 65 63 64 73 61 2e 63 72 74 "
        "30 27 06 08 2b 06 01 05 05 07 30 01 86 1b 68 74 "
        "74 70 3a 2f 2f 6f 63 73 70 2e 6c 6f 63 61 6c 68 "
        "6f 73 74 3a 34 34 34 30 34 30 3e 06 03 55 1d 1f "
        "04 37 30 35 30 33 a0 31 a0 2f 86 2d 68 74 74 70 "
        "3a 2f 2f 63 72 6c 2e 6c 6f 63 61 6c 68 6f 73 74 "
        "3a 34 34 34 30 30 2f 63 72 6c 2f 72 6f 6f 74 2d "
        "65 63 64 73 61 2e 63 72 6c 30 4e 06 03 55 1d 1e "
        "01 01 ff 04 44 30 42 a0 0e 30 0c 82 0a 2e 6c 6f "
        "63 61 6c 68 6f 73 74 a1 30 30 0a 87 08 00 00 00 "
        "00 00 00 00 00 30 22 87 20 00 00 00 00 00 00 00 "
        "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
        "00 00 00 00 00 00 00 00 00 30 14 06 08 2b 06 01 "
        "05 05 07 01 18 04 08 30 06 02 01 05 02 01 11 30 "
        "0a 06 08 2a 86 48 ce 3d 04 03 02 03 67 00 30 64 "
        "02 2f 05 03 4e 57 cf fa 40 5f dc 89 96 21 70 7b "
        "a5 d5 cd ec 3b 1d 2f e4 8e f2 ea 0c 27 84 ff 85 "
        "f9 ff 4b 8e 55 48 ad 06 85 f7 d4 08 00 a3 7b 2d "
        "f9 02 31 00 fd 5e ad b3 69 cd 4c 45 76 e0 86 a7 "
        "65 b2 e2 5b da 5d 23 6d 6d 8d 4d c7 c1 81 c0 0a "
        "2c 38 31 2a c5 1a 0b 57 60 ab 84 dc 39 62 37 25 "
        "35 94 f0 91 00 00 "
    )
    certificate = msg.HandshakeMessage.deserialize(data, conn)
    assert certificate.request_context == bytes.fromhex("aa bb cc")


def test_server_key_exchange_invalid_kex_type(tlsmate):
    conn = tlsmate.client.create_connection()
    conn.cs_details = utils.get_cipher_suite_details(
        tls.CipherSuite.TLS_RSA_WITH_AES_128_CBC_SHA256
    )
    data = bytes.fromhex("0c 00 00 01 01")

    with pytest.raises(
        tls.ServerMalfunction, match=tls.ServerIssue.INCOMPATIBLE_KEY_EXCHANGE.value
    ):
        msg.HandshakeMessage.deserialize(data, conn)


def test_server_hello_done_invalid_length():
    data = bytes.fromhex("0e 00 00 01 01")
    with pytest.raises(
        tls.ServerMalfunction, match=tls.ServerIssue.MESSAGE_LENGTH_ERROR.value
    ):
        msg.HandshakeMessage.deserialize(data, None)


def test_end_of_early_data_ok():
    data = bytes.fromhex("05 00 00 00 ")
    message = msg.HandshakeMessage.deserialize(data, None)
    assert type(message) is msg.EndOfEarlyData
    assert message.msg_type is tls.HandshakeType.END_OF_EARLY_DATA


def test_end_of_early_data_invalid_length():
    data = bytes.fromhex("05 00 00 01 01")
    with pytest.raises(
        tls.ServerMalfunction, match=tls.ServerIssue.MESSAGE_LENGTH_ERROR.value
    ):
        msg.HandshakeMessage.deserialize(data, None)


def test_certificate_request(tlsmate):
    conn = tlsmate.client.create_connection()
    conn.version = tls.Version.TLS12
    # for the moment only check if the cert-authotities are tranparently unpacked
    data = bytes.fromhex(
        "0d 00 00 13 01 01 00 02 04 01" "00 0b" "00 03 aa bb cc" "00 04 11 22 33 44"
    )
    message = msg.HandshakeMessage.deserialize(data, conn)
    assert len(message.certificate_authorities) == 2
    assert message.certificate_authorities[0] == bytes.fromhex("aa bb cc")
    assert message.certificate_authorities[1] == bytes.fromhex("11 22 33 44")


def test_change_cipher_spec():
    data = bytes.fromhex("00 02 01 02")
    with pytest.raises(
        tls.ServerMalfunction, match=tls.ServerIssue.MESSAGE_LENGTH_ERROR.value
    ):
        msg.ChangeCipherSpecMessage.deserialize(data, None)


def test_alert():
    alert = msg.Alert(level=13, description=45)
    data = alert.serialize(None)
    assert data == bytes.fromhex("0d 2d")


def test_ssl2_error():
    data = bytes.fromhex("00 00 04")
    message = msg.SSL2Message.deserialize(data, None)
    assert type(message) is msg.SSL2Error
    assert message.msg_type is tls.SSLMessagType.SSL2_ERROR
    assert message.error is tls.SSLError.BAD_CERTIFICATE
