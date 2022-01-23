# -*- coding: utf-8 -*-

# import basic stuff

# import own stuff
import tlsmate.ext as ext
import tlsmate.tls as tls

import pytest

# import other stuff


def test_ServerNameIndication():
    data = bytes.fromhex("00 00 00 0e 00 0c 00 00 09 6c 6f 63 61 6c 68 6f 73 74")
    sni, offset = ext.Extension.deserialize(data, 0)
    assert offset == len(data)
    assert sni.host_name == "localhost"
    assert sni.serialize(None) == data
    sni = ext.ExtServerNameIndication(host_name="localhost")
    assert sni.serialize(None) == data


def test_sni_empty():
    data = bytes.fromhex("00 00 00 00")
    sni, offset = ext.Extension.deserialize(data, 0)
    assert sni.host_name is None


def test_sni_wrong_length():
    data = bytes.fromhex("00 00 00 0e 00 0d 00 00 09 6c 6f 63 61 6c 68 6f 73 74")
    with pytest.raises(tls.ServerMalfunction, match="extension length incorrect"):
        sni, offset = ext.Extension.deserialize(data, 0)


def test_sni_wrong_name_type():
    data = bytes.fromhex("00 00 00 0e 00 0c 01 00 09 6c 6f 63 61 6c 68 6f 73 74")
    with pytest.raises(tls.ServerMalfunction, match="host_name not present"):
        sni, offset = ext.Extension.deserialize(data, 0)


def test_ems_wrong_length():
    data = bytes.fromhex("00 17 00 01 00")
    with pytest.raises(tls.ServerMalfunction, match="extension length incorrect"):
        ems, offset = ext.Extension.deserialize(data, 0)


def test_etm_wrong_length():
    data = bytes.fromhex("00 16 00 01 00")
    with pytest.raises(tls.ServerMalfunction, match="extension length incorrect"):
        ems, offset = ext.Extension.deserialize(data, 0)


def test_ec_point_format():
    epf = ext.ExtEcPointFormats(ec_point_formats=[tls.EcPointFormat.UNCOMPRESSED, 5])
    assert epf.serialize(None) == bytes.fromhex("00 0b 00 03 02 00 05")


def test_ec_point_format_wrong_length():
    data = bytes.fromhex("00 0b 00 03 03 00 05")
    with pytest.raises(tls.ServerMalfunction, match="extension length incorrect"):
        epf, offset = ext.Extension.deserialize(data, 0)


def test_supported_groups_unknown_value():
    data = bytes.fromhex("00 0a 00 0a 00 08 00 1d 00 17 00 18 00 aa")
    groups, offset = ext.Extension.deserialize(data, 0)
    assert offset == len(data)
    assert type(groups) is ext.ExtSupportedGroups
    assert groups.supported_groups == [
        tls.SupportedGroups.X25519,
        tls.SupportedGroups.SECP256R1,
        tls.SupportedGroups.SECP384R1,
        0x00AA,
    ]


def test_sig_algo():
    extension = ext.ExtSignatureAlgorithms(
        signature_algorithms=[tls.SignatureScheme.ECDSA_SHA1, (0xAA, 0xBB)]
    )
    data = extension.serialize(None)
    assert data == bytes.fromhex("00 0d 00 06 00 04 02 03 aa bb")
    sig_algo, offset = ext.Extension.deserialize(data, 0)
    assert offset == len(data)
    assert type(sig_algo) is ext.ExtSignatureAlgorithms
    assert sig_algo.signature_algorithms == [tls.SignatureScheme.ECDSA_SHA1, 0xAABB]


def test_heartbeat():
    extension = ext.ExtHeartbeat(heartbeat_mode=0x11)
    assert extension.serialize(None) == bytes.fromhex("00 0f 00 01 11")


def test_cert_authorities():
    data = bytes.fromhex("00 2f 00 0e 00 0c 00 03 aa bb cc 00 05 11 22 33 44 55")
    ca, offset = ext.Extension.deserialize(data, 0)
    assert offset == len(data)
    assert type(ca) is ext.ExtCertificateAuthorities
    assert len(ca.authorities) == 2
    assert ca.authorities[0] == bytes.fromhex("aa bb cc")
    assert ca.authorities[1] == bytes.fromhex("11 22 33 44 55")


def test_status_request():
    extension = ext.ExtStatusRequest(responder_ids=[b"\4\5"], extensions=[b"\1"])
    data = bytes.fromhex("00 05 00 0c 01  00 04 00 02 04 05  00 03 00 01 01")
    assert extension.serialize(None) == data


def test_status_request_v2():
    extension = ext.ExtStatusRequestV2(responder_ids=[b"\4\5"], extensions=b"\1")
    data = bytes.fromhex("00 11 00 0e 00 0c 02 00 09 00 04 00 02 04 05  00 01 01")
    assert extension.serialize(None) == data


def test_status_request_v2_deserialize():
    data = bytes.fromhex("00 11 00 09 02 00 00 05 01 02 03 04 05")
    status, offset = ext.Extension.deserialize(data, 0)
    assert offset == len(data)
    assert type(status) is ext.ExtStatusRequestV2
    assert status.status_type is tls.StatusType.OCSP_MULTI
    assert status.ocsp_response == bytes.fromhex("01 02 03 04 05")


def test_unknown_ext():
    data = bytes.fromhex("00 ab 00 0e 00 0c 00 00 09 6c 6f 63 61 6c 68 6f 73 74")
    extension, offset = ext.Extension.deserialize(data, 0)
    assert offset == len(data)
    assert extension.extension_id is tls.Extension.UNKNOW_EXTENSION
    assert extension.id == 0x00AB
    assert extension.bytes == data[4:]
    assert extension.serialize(None) == data
    ext2 = ext.ExtUnknownExtension(
        id=0x00AB, bytes=bytes.fromhex("00 0c 00 00 09 6c 6f 63 61 6c 68 6f 73 74")
    )
    assert ext2.serialize(None) == data
