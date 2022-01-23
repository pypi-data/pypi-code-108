# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import datetime
import os
from tlsmate.cert_chain import CertChain
from tlsmate.cert import Certificate
from tlsmate.tls import UntrustedCertificate
from tlsmate import tls
from tlsmate import tlsmate as tm
from cryptography.x509 import ocsp, load_pem_x509_certificate, ReasonFlags
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives import hashes, serialization

import pytest
import requests


def init_crl(ca_dir, crl_manager, ca):
    port = 44400
    if "TLSMATE_CA_PORT" in os.environ:
        port = os.environ["TLSMATE_CA_PORT"]

    pem_file = ca_dir / f"crl/{ca}.crl.pem"
    with open(pem_file, "rb") as fd:
        crl = fd.read()
    crl_manager.add_crl(f"http://crl.localhost:{port}/crl/{ca}.crl", pem_crl=crl)


@pytest.fixture
def tlsmate_cert(ca_dir, trust_store_file):
    mate = tm.TlsMate()
    mate.trust_store.set_ca_files([trust_store_file])
    init_crl(ca_dir, mate.crl_manager, "root-rsa")
    init_crl(ca_dir, mate.crl_manager, "root-ecdsa")
    init_crl(ca_dir, mate.crl_manager, "ca-rsa")
    init_crl(ca_dir, mate.crl_manager, "ca-ecdsa")
    mate.config.set("ocsp", False)
    mate.config.set("crl", True)
    return mate


def test_revoked_certificate(
    tlsmate_cert, valid_time, server_revoked_rsa_cert, ca_rsa_cert
):

    chain = CertChain()
    for cert in (server_revoked_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(UntrustedCertificate, match=f" {tls.CertCrlStatus.REVOKED}"):
        chain.validate(valid_time, "revoked.localhost", True)


def test_certificate_not_yet_valid(tlsmate_cert, server_rsa_cert, ca_rsa_cert):

    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(UntrustedCertificate, match=r"validity period.*not yet reached"):
        chain.validate(datetime.datetime(2000, 2, 27), "localhost", True)


def test_certificate_expired(tlsmate_cert, server_rsa_cert, ca_rsa_cert):

    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(UntrustedCertificate, match=r"validity period.*exceeded"):
        chain.validate(datetime.datetime(2200, 2, 27), "localhost", True)


def test_dsa_certificate(tlsmate_cert, valid_time, server_dsa_cert, ca_rsa_cert):

    chain = CertChain()
    for cert in (server_dsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(valid_time, "localhost", True)
    assert True


def test_ed25519_certificate(
    tlsmate_cert, valid_time, server_ed25519_cert, ca_ecdsa_cert
):

    chain = CertChain()
    for cert in (server_ed25519_cert, ca_ecdsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(valid_time, "localhost", True)
    assert True


def test_ed448_certificate(tlsmate_cert, valid_time, server_ed448_cert, ca_ecdsa_cert):

    chain = CertChain()
    for cert in (server_ed448_cert, ca_ecdsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(valid_time, "localhost", True)
    assert True


def test_rsa_with_root_certificate(
    tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert, root_rsa_cert
):

    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert, root_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(valid_time, "localhost", True)
    assert True


def test_wrong_sni(tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert):

    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(UntrustedCertificate, match=r"subject name does not match"):
        chain.validate(valid_time, "example.com", True)


def test_root_not_last_in_chain(
    tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert, ca_ecdsa_cert, root_rsa_cert
):

    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert, ca_ecdsa_cert, root_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(valid_time, "localhost", True)
    assert True


def test_issuer_mismatch(tlsmate_cert, valid_time, server_rsa_cert, ca_ecdsa_cert):

    chain = CertChain()
    for cert in (server_rsa_cert, ca_ecdsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(UntrustedCertificate, match="not found in trust store"):
        chain.validate(valid_time, "localhost", True)


def test_signature_invalid_chain(
    tlsmate_cert, valid_time, server_rsa_cert, ca_2nd_rsa_cert
):

    chain = CertChain()
    for cert in (server_rsa_cert, ca_2nd_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(UntrustedCertificate, match="not found in trust store"):
        chain.validate(valid_time, "localhost", True)


def test_root_in_chain_not_in_truststore(
    tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert, root_rsa_cert
):

    # hard reset of the trust store
    tlsmate_cert.trust_store._ca_files = None

    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert, root_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(
        UntrustedCertificate, match="self-signed certificate not found in trust store"
    ):
        chain.validate(valid_time, "localhost", True)


def test_root_not_in_chain_not_in_truststore(
    tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert
):

    # hard reset of the trust store
    tlsmate_cert.trust_store._ca_files = None

    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(UntrustedCertificate, match="not found in trust store"):
        chain.validate(valid_time, "localhost", True)


def test_rsa_san(tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert):

    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(valid_time, "test.localhost", True)
    assert True

    chain.validate(valid_time, "hello.wildcard.localhost", True)
    assert True


def test_certs_not_in_sequence(
    tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert, root_rsa_cert
):

    chain = CertChain()
    for cert in (server_rsa_cert, root_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(valid_time, "localhost", True)
    assert "certificates of the chain are not in sequence" in chain.issues[0]


def test_gratuitous_certificate(
    tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert, ca_ecdsa_cert
):

    chain = CertChain()
    for cert in (server_rsa_cert, ca_ecdsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(valid_time, "localhost", False)
    assert (
        "gratuitous certificate, not part of trust chain"
        in chain.certificates[1].issues[0]
    )


def test_root_not_in_chain_not_in_truststore_no_exception(
    tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert
):

    # hard reset of the trust store
    tlsmate_cert.trust_store._ca_files = None

    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(valid_time, "localhost", False)
    assert chain.successful_validation is False


def requests_post_timeout(url, **kwargs):
    raise requests.Timeout


def test_ocsp_status_timeout(
    monkeypatch, tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert
):

    monkeypatch.setattr(requests, "post", requests_post_timeout)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(
        UntrustedCertificate, match=r".*connection to OCSP server .* timed out"
    ):
        chain.validate(valid_time, "localhost", True)


def requests_post_exception(url, **kwargs):
    raise ConnectionResetError


def test_ocsp_status_exception(
    monkeypatch, tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert
):

    monkeypatch.setattr(requests, "post", requests_post_exception)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(
        UntrustedCertificate, match=r".*connection to OCSP server .* failed"
    ):
        chain.validate(valid_time, "localhost", True)


def test_ocsp_status_cached_chain(
    monkeypatch, tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert
):

    monkeypatch.setattr(requests, "post", requests_post_exception)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(
        UntrustedCertificate, match=r".*connection to OCSP server .* failed"
    ):
        chain.validate(valid_time, "localhost", True)

    with pytest.raises(
        UntrustedCertificate, match=r".*cached status for .* is not valid"
    ):
        chain.validate(valid_time, "localhost", True)


class Response(object):
    def __init__(self, content=None):
        self.ok = True
        self.content = content


orig_validate_ocsp = CertChain._valid_ocsp


def validate_ocsp(self, cert, issuer_cert, timestamp):
    if str(cert) == "CN=localhost,O=The TlsMate Company (Server side) RSA,C=DE":
        return orig_validate_ocsp(self, cert, issuer_cert, timestamp)

    else:
        return True


def test_ocsp_status_invalid_signature(
    monkeypatch, tlsmate_cert, server_rsa_cert, ca_rsa_cert, root_rsa_cert, root_rsa_key
):

    now = datetime.datetime.now()

    def requests_posts(url, **kwargs):
        ca_cert = load_pem_x509_certificate(ca_rsa_cert.as_bytes())
        builder = ocsp.OCSPResponseBuilder()
        builder = builder.add_response(
            cert=load_pem_x509_certificate(server_rsa_cert.as_bytes()),
            issuer=ca_cert,
            cert_status=ocsp.OCSPCertStatus.GOOD,
            algorithm=hashes.SHA1(),
            this_update=now,
            next_update=now + datetime.timedelta(days=1),
            revocation_time=None,
            revocation_reason=None,
        ).responder_id(
            ocsp.OCSPResponderEncoding.HASH,
            load_pem_x509_certificate(root_rsa_cert.as_bytes()),
        )
        ocsp_resp = builder.sign(
            serialization.load_pem_private_key(root_rsa_key.as_bytes(), password=None),
            hashes.SHA1(),
        )

        return Response(content=ocsp_resp.public_bytes(Encoding.DER))

    monkeypatch.setattr(requests, "post", requests_posts)
    monkeypatch.setattr(CertChain, "_valid_ocsp", validate_ocsp)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(
        UntrustedCertificate, match=r".*OCSP status is SIGNATURE_INVALID"
    ):
        chain.validate(now, "localhost", True)


def test_ocsp_invalid_reponse(
    monkeypatch, tlsmate_cert, server_rsa_cert, ca_rsa_cert,
):

    now = datetime.datetime.now()

    def requests_posts(url, **kwargs):
        ocsp_resp = ocsp.OCSPResponseBuilder.build_unsuccessful(
            ocsp.OCSPResponseStatus.UNAUTHORIZED
        )
        return Response(content=ocsp_resp.public_bytes(Encoding.DER))

    monkeypatch.setattr(requests, "post", requests_posts)
    monkeypatch.setattr(CertChain, "_valid_ocsp", validate_ocsp)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(
        UntrustedCertificate, match=r".*OCSP status is INVALID_RESPONSE"
    ):
        chain.validate(now, "localhost", True)


def test_ocsp_status_with_cert(
    monkeypatch, tlsmate_cert, server_rsa_cert, ca_rsa_cert, ca_rsa_key
):

    now = datetime.datetime.now()

    def requests_posts(url, **kwargs):
        ca_cert = load_pem_x509_certificate(ca_rsa_cert.as_bytes())
        builder = ocsp.OCSPResponseBuilder()
        builder = (
            builder.add_response(
                cert=load_pem_x509_certificate(server_rsa_cert.as_bytes()),
                issuer=ca_cert,
                cert_status=ocsp.OCSPCertStatus.GOOD,
                algorithm=hashes.SHA1(),
                this_update=now,
                next_update=now + datetime.timedelta(days=1),
                revocation_time=None,
                revocation_reason=None,
            )
            .certificates([ca_cert])
            .responder_id(ocsp.OCSPResponderEncoding.HASH, ca_cert)
        )
        ocsp_resp = builder.sign(
            serialization.load_pem_private_key(ca_rsa_key.as_bytes(), password=None),
            hashes.SHA1(),
        )

        return Response(content=ocsp_resp.public_bytes(Encoding.DER))

    monkeypatch.setattr(requests, "post", requests_posts)
    monkeypatch.setattr(CertChain, "_valid_ocsp", validate_ocsp)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(now, "localhost", True)
    assert True


def test_ocsp_status_with_invalid_cert(
    monkeypatch,
    tlsmate_cert,
    server_rsa_cert,
    ca_rsa_cert,
    ca_rsa_key,
    server_expired_rsa_cert,
):

    now = datetime.datetime.now()

    def requests_posts(url, **kwargs):
        ca_cert = load_pem_x509_certificate(ca_rsa_cert.as_bytes())
        builder = ocsp.OCSPResponseBuilder()
        builder = (
            builder.add_response(
                cert=load_pem_x509_certificate(server_rsa_cert.as_bytes()),
                issuer=ca_cert,
                cert_status=ocsp.OCSPCertStatus.GOOD,
                algorithm=hashes.SHA1(),
                this_update=now,
                next_update=now + datetime.timedelta(days=1),
                revocation_time=None,
                revocation_reason=None,
            )
            .certificates(
                [load_pem_x509_certificate(server_expired_rsa_cert.as_bytes())]
            )
            .responder_id(ocsp.OCSPResponderEncoding.HASH, ca_cert)
        )
        ocsp_resp = builder.sign(
            serialization.load_pem_private_key(ca_rsa_key.as_bytes(), password=None),
            hashes.SHA1(),
        )
        return Response(content=ocsp_resp.public_bytes(Encoding.DER))

    monkeypatch.setattr(requests, "post", requests_posts)
    monkeypatch.setattr(CertChain, "_valid_ocsp", validate_ocsp)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(
        UntrustedCertificate, match=r".*OCSP status is INVALID_ISSUER_CERT"
    ):
        chain.validate(now, "localhost", True)


def test_ocsp_status_invalid_update_time(
    monkeypatch, tlsmate_cert, server_rsa_cert, ca_rsa_cert, ca_rsa_key
):

    now = datetime.datetime.now()

    def requests_posts(url, **kwargs):
        ca_cert = load_pem_x509_certificate(ca_rsa_cert.as_bytes())
        builder = ocsp.OCSPResponseBuilder()
        builder = (
            builder.add_response(
                cert=load_pem_x509_certificate(server_rsa_cert.as_bytes()),
                issuer=ca_cert,
                cert_status=ocsp.OCSPCertStatus.GOOD,
                algorithm=hashes.SHA1(),
                this_update=now + datetime.timedelta(days=1),
                next_update=now + datetime.timedelta(days=1),
                revocation_time=None,
                revocation_reason=None,
            )
            .certificates([ca_cert])
            .responder_id(ocsp.OCSPResponderEncoding.HASH, ca_cert)
        )
        ocsp_resp = builder.sign(
            serialization.load_pem_private_key(ca_rsa_key.as_bytes(), password=None),
            hashes.SHA1(),
        )

        return Response(content=ocsp_resp.public_bytes(Encoding.DER))

    monkeypatch.setattr(requests, "post", requests_posts)
    monkeypatch.setattr(CertChain, "_valid_ocsp", validate_ocsp)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(
        UntrustedCertificate, match=r".*OCSP status is INVALID_TIMESTAMP"
    ):
        chain.validate(now, "localhost", True)


def test_ocsp_status_invalid_next_update(
    monkeypatch, tlsmate_cert, server_rsa_cert, ca_rsa_cert, ca_rsa_key
):

    now = datetime.datetime.now()

    def requests_posts(url, **kwargs):
        ca_cert = load_pem_x509_certificate(ca_rsa_cert.as_bytes())
        builder = ocsp.OCSPResponseBuilder()
        builder = (
            builder.add_response(
                cert=load_pem_x509_certificate(server_rsa_cert.as_bytes()),
                issuer=ca_cert,
                cert_status=ocsp.OCSPCertStatus.GOOD,
                algorithm=hashes.SHA1(),
                this_update=now,
                next_update=now - datetime.timedelta(days=1),
                revocation_time=None,
                revocation_reason=None,
            )
            .certificates([ca_cert])
            .responder_id(ocsp.OCSPResponderEncoding.HASH, ca_cert)
        )
        ocsp_resp = builder.sign(
            serialization.load_pem_private_key(ca_rsa_key.as_bytes(), password=None),
            hashes.SHA1(),
        )

        return Response(content=ocsp_resp.public_bytes(Encoding.DER))

    monkeypatch.setattr(requests, "post", requests_posts)
    monkeypatch.setattr(CertChain, "_valid_ocsp", validate_ocsp)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(
        UntrustedCertificate, match=r".*OCSP status is INVALID_TIMESTAMP"
    ):
        chain.validate(now, "localhost", True)


def test_ocsp_invalid_response(
    monkeypatch, tlsmate_cert, server_rsa_cert, ca_rsa_cert, ca_rsa_key
):

    now = datetime.datetime.now()

    def requests_posts(url, **kwargs):
        ocsp_resp = ocsp.OCSPResponseBuilder.build_unsuccessful(
            ocsp.OCSPResponseStatus.UNAUTHORIZED
        )
        return Response(content=ocsp_resp.public_bytes(Encoding.DER))

    monkeypatch.setattr(requests, "post", requests_posts)
    monkeypatch.setattr(CertChain, "_valid_ocsp", validate_ocsp)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(
        UntrustedCertificate, match=r".*OCSP status is INVALID_RESPONSE"
    ):
        chain.validate(now, "localhost", True)


def test_ocsp_status_revoked(
    monkeypatch, tlsmate_cert, server_rsa_cert, ca_rsa_cert, ca_rsa_key
):

    now = datetime.datetime.now()

    def requests_posts(url, **kwargs):
        ca_cert = load_pem_x509_certificate(ca_rsa_cert.as_bytes())
        builder = ocsp.OCSPResponseBuilder()
        builder = (
            builder.add_response(
                cert=load_pem_x509_certificate(server_rsa_cert.as_bytes()),
                issuer=ca_cert,
                cert_status=ocsp.OCSPCertStatus.REVOKED,
                algorithm=hashes.SHA1(),
                this_update=now,
                next_update=now + datetime.timedelta(days=1),
                revocation_time=now - datetime.timedelta(days=100),
                revocation_reason=ReasonFlags.key_compromise,
            )
            .certificates([ca_cert])
            .responder_id(ocsp.OCSPResponderEncoding.HASH, ca_cert)
        )
        ocsp_resp = builder.sign(
            serialization.load_pem_private_key(ca_rsa_key.as_bytes(), password=None),
            hashes.SHA1(),
        )

        return Response(content=ocsp_resp.public_bytes(Encoding.DER))

    monkeypatch.setattr(requests, "post", requests_posts)
    monkeypatch.setattr(CertChain, "_valid_ocsp", validate_ocsp)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(UntrustedCertificate, match=r".*OCSP status is REVOKED"):
        chain.validate(now, "localhost", True)


def test_ocsp_status_unknown(
    monkeypatch, tlsmate_cert, server_rsa_cert, ca_rsa_cert, ca_rsa_key
):

    now = datetime.datetime.now()

    def requests_posts(url, **kwargs):
        ca_cert = load_pem_x509_certificate(ca_rsa_cert.as_bytes())
        builder = ocsp.OCSPResponseBuilder()
        builder = (
            builder.add_response(
                cert=load_pem_x509_certificate(server_rsa_cert.as_bytes()),
                issuer=ca_cert,
                cert_status=ocsp.OCSPCertStatus.UNKNOWN,
                algorithm=hashes.SHA1(),
                this_update=now,
                next_update=now + datetime.timedelta(days=1),
                revocation_time=None,
                revocation_reason=None,
            )
            .certificates([ca_cert])
            .responder_id(ocsp.OCSPResponderEncoding.HASH, ca_cert)
        )
        ocsp_resp = builder.sign(
            serialization.load_pem_private_key(ca_rsa_key.as_bytes(), password=None),
            hashes.SHA1(),
        )

        return Response(content=ocsp_resp.public_bytes(Encoding.DER))

    monkeypatch.setattr(requests, "post", requests_posts)
    monkeypatch.setattr(CertChain, "_valid_ocsp", validate_ocsp)

    tlsmate_cert.config.set("ocsp", True)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(UntrustedCertificate, match=r".*OCSP status is UNKNOWN"):
        chain.validate(now, "localhost", True)


def test_cert_no_ids(tlsmate_cert, valid_time, server_no_ids_rsa_cert, ca_rsa_cert):

    chain = CertChain()
    for cert in (server_no_ids_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(valid_time, "localhost", True)
    assert True


def test_cert_invalid_signature(
    monkeypatch, tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert
):
    def validate_cert_signature(cert):
        raise Exception("bla bla")

    monkeypatch.setattr(Certificate, "validate_cert_signature", validate_cert_signature)

    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    with pytest.raises(UntrustedCertificate, match="invalid signature"):
        chain.validate(valid_time, "localhost", True)


def test_cert_untrusted_trust_path(
    tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert, ca_ecdsa_cert
):

    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert, ca_ecdsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.certificates[2].trusted = tls.ScanState.FALSE
    chain.validate(valid_time, "localhost", False)
    assert (
        chain.certificates[2].issues[0]
        == "certificate part of untrusted alternate trust path"
    )


def test_no_crl(tlsmate_cert, valid_time, server_rsa_cert, ca_rsa_cert):

    tlsmate_cert.config.set("crl", False)
    chain = CertChain()
    for cert in (server_rsa_cert, ca_rsa_cert):
        chain.append_pem_cert(cert.as_bytes())

    chain.validate(valid_time, "localhost", False)
    for cert in chain.certificates:
        assert cert.crl_status is tls.CertCrlStatus.UNDETERMINED
