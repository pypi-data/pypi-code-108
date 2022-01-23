# -*- coding: utf-8 -*-
"""Module for handling a certificate chain
"""
# import basic stuff
import logging
import time
import datetime
from typing import List, Optional

# import own stuff
import tlsmate.cert as crt
import tlsmate.cert_utils as cert_utils
import tlsmate.recorder as recorder
import tlsmate.tls as tls

# import other stuff
import requests
from cryptography import x509
from cryptography.x509 import ocsp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import AuthorityInformationAccessOID
from cryptography.exceptions import InvalidSignature


class CertChain(object):
    """Class representing a certificate chain.

    This object is iterable, yielding the x509 representation of the certificates.
    """

    def __init__(self):
        from tlsmate.tlsmate import TlsMate

        tlsmate = TlsMate.instance
        self._cert_chain_cache = tlsmate.cert_chain_cache
        self.certificates = []
        self._digest = hashes.Hash(hashes.SHA256())
        self._digest_value = None
        self._raise_on_failure = True
        self.issues = []
        self.successful_validation = False
        self.root_cert = None
        self.root_cert_transmitted = False
        self._recorder = tlsmate.recorder
        self._config = tlsmate.config
        self._trust_store = tlsmate.trust_store
        self._crl_manager = tlsmate.crl_manager
        self._trust_path = None
        self._proxies = None
        proxy = self._config.get("proxy")
        if proxy:
            self._proxies = dict(http=proxy, https=proxy)

    def append_bin_cert(self, bin_cert: bytes) -> None:
        """Append the chain by a certificate given in raw format.

        Arguments:
            bin_cert: the certificate to append in raw format
        """
        self.certificates.append(crt.Certificate(der=bin_cert, parse=True))
        self._digest.update(bin_cert)

    def append_pem_cert(self, pem_cert: bytes) -> None:
        """Append the chain by a certificate given in pem format.

        Arguments:
            pem_cert: the certificate to append in pem format
        """
        cert = crt.Certificate(pem=pem_cert)
        self.certificates.append(cert)
        self._digest.update(cert.bytes)

    @property
    def digest(self):
        """bytes: a SHA256 digest of the complete chain, usable for comparison"""
        if self._digest_value is None:
            self._digest_value = self._digest.finalize()
        return self._digest_value

    def _valid_crl(self, cert, issuer_cert, timestamp):
        """Check the CRL state for the given certificate."""

        if not self._config.get("crl"):
            cert.crl_status = tls.CertCrlStatus.UNDETERMINED
            return True

        try:
            dist_points = cert.parsed.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.CRL_DISTRIBUTION_POINTS
            )
        except x509.ExtensionNotFound:
            return True

        crl_urls = []
        for dist_point in dist_points.value:
            if dist_point.full_name is not None:
                for gen_name in dist_point.full_name:
                    if isinstance(gen_name, x509.UniformResourceIdentifier):
                        if gen_name.value.startswith("http://"):
                            crl_urls.append(gen_name.value)
            elif dist_point.relative_me is not None:
                raise NotImplementedError

        cert.crl_status = self._crl_manager.get_crl_status(
            crl_urls,
            cert.parsed.serial_number,
            cert.parsed.issuer,
            issuer_cert,
            timestamp,
            self._proxies,
        )
        logging.debug(f'CRL status is {cert.crl_status} for certificate "{cert}"')
        if cert.crl_status is not tls.CertCrlStatus.NOT_REVOKED:
            cert.mark_untrusted(f"CRL status not ok: {cert.crl_status}")
            return False

        return True

    def _verify_ocsp_resp(self, cert, response, timestamp, issuer_cert):
        if not response:
            return None

        ocsp_decoded = ocsp.load_der_ocsp_response(response)

        if ocsp_decoded.response_status is not ocsp.OCSPResponseStatus.SUCCESSFUL:
            return tls.OcspStatus.INVALID_RESPONSE

        if ocsp_decoded.certificates:
            sig_cert = crt.Certificate(
                x509_cert=ocsp_decoded.certificates[0], parse=True
            )
            self._determine_trust_path(sig_cert, -1, timestamp, None, False)
            if sig_cert.trusted is tls.ScanState.FALSE:
                return tls.OcspStatus.INVALID_ISSUER_CERT

        else:
            sig_cert = issuer_cert

        if sig_cert is None:
            return tls.OcspStatus.NO_ISSUER

        else:
            # check signature
            try:
                sig_scheme = cert_utils.map_x509_sig_scheme(
                    ocsp_decoded.signature_hash_algorithm,
                    ocsp_decoded.signature_algorithm_oid,
                )
                sig_cert.validate_signature(
                    sig_scheme, ocsp_decoded.tbs_response_bytes, ocsp_decoded.signature,
                )

            except InvalidSignature:
                return tls.OcspStatus.SIGNATURE_INVALID

        if ocsp_decoded.this_update > timestamp:
            return tls.OcspStatus.INVALID_TIMESTAMP

        if ocsp_decoded.next_update and ocsp_decoded.next_update < timestamp:
            return tls.OcspStatus.INVALID_TIMESTAMP

        if ocsp_decoded.certificate_status == ocsp.OCSPCertStatus.GOOD:
            return tls.OcspStatus.NOT_REVOKED

        elif ocsp_decoded.certificate_status == ocsp.OCSPCertStatus.REVOKED:
            return tls.OcspStatus.REVOKED

        else:
            return tls.OcspStatus.UNKNOWN

    def verify_ocsp_stapling(
        self, responses: List[bytes], raise_on_failure: bool
    ) -> List[Optional[tls.OcspStatus]]:
        """Check the status for a OCSP response

        Arguments:
            responses: the OCSP response
            raise_on_failure: An indication, if the validation shall abort
                in case exceptional cases are detected. Normally set to False for
                server scans.

        Returns:
            the status, one for each response. An list element can be None, if
            an empty response is provided.
        """

        ret_status: List[Optional[tls.OcspStatus]] = []
        for idx, resp in enumerate(responses):
            if not resp:
                ret_status.append(None)
                continue

            cert = self.certificates[idx]
            if not self.successful_validation:
                ocsp_status = tls.OcspStatus.INVALID_ISSUER_CERT

            else:
                ocsp_status = self._verify_ocsp_resp(
                    cert, resp, self._recorder.get_timestamp(), cert.issuer_cert,
                )
            ret_status.append(ocsp_status)
            issue = f"OCSP stapling status {ocsp_status} for certificate {cert}"
            logging.debug(issue)
            if ocsp_status is not tls.OcspStatus.NOT_REVOKED and raise_on_failure:
                raise tls.UntrustedCertificate(issue)

        return ret_status

    def _valid_ocsp(self, cert, issuer_cert, timestamp):
        """Check the OCSP status for the given certificate."""

        if not self._config.get("ocsp"):
            cert.ocsp_status = tls.OcspStatus.UNDETERMINED
            return True

        try:
            aia = cert.parsed.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.AUTHORITY_INFORMATION_ACCESS
            ).value

        except x509.ExtensionNotFound:
            return True

        ocsps = [
            ia for ia in aia if ia.access_method == AuthorityInformationAccessOID.OCSP
        ]
        if not ocsps:
            return True

        ocsp_url = ocsps[0].access_location.value
        builder = ocsp.OCSPRequestBuilder()

        # Hm, some OCSP servers do not support SHA256, so let's use SHA1 until we
        # are told otherwise.
        builder = builder.add_certificate(
            cert.parsed, issuer_cert.parsed, hashes.SHA1()
        )
        req = builder.build()
        start = time.time()
        try:
            if self._recorder.is_injecting():
                ocsp_resp = self._recorder.inject_response()

            else:
                ocsp_resp = requests.post(
                    ocsp_url,
                    headers={"Content-Type": "application/ocsp-request"},
                    data=req.public_bytes(serialization.Encoding.DER),
                    timeout=5,
                    proxies=self._proxies,
                )
                self._recorder.trace_response(
                    time.time() - start, recorder.SocketEvent.DATA, ocsp_resp
                )

        except requests.Timeout:
            self._recorder.trace_response(
                time.time() - start, recorder.SocketEvent.TIMEOUT
            )
            cert.ocsp_status = tls.OcspStatus.TIMEOUT
            cert.mark_untrusted(f"connection to OCSP server {ocsp_url} timed out")
            return False

        except Exception:
            self._recorder.trace_response(
                time.time() - start, recorder.SocketEvent.CLOSURE
            )
            cert.ocsp_status = tls.OcspStatus.INVALID_RESPONSE
            cert.mark_untrusted(f"connection to OCSP server {ocsp_url} failed")
            return False

        if ocsp_resp.ok:
            cert.ocsp_status = self._verify_ocsp_resp(
                cert, ocsp_resp.content, self._recorder.get_timestamp(), issuer_cert,
            )
            issue = f"OCSP status is {cert.ocsp_status}"
            if cert.ocsp_status is not tls.OcspStatus.NOT_REVOKED:
                cert.mark_untrusted(issue)
                return False

            else:
                logging.debug(f"{issue} for certificate {cert}")
                return True

        return False

    def _issuer_certs(self, cert):
        """Get a list of all potential issuers from the certificate chain."""
        issuers = []
        for issuer_idx in range(1, len(self.certificates)):
            issuer_cert = self.certificates[issuer_idx]
            if cert.auth_key_id and issuer_cert.subject_key_id:
                match = cert.auth_key_id == issuer_cert.subject_key_id

            else:
                match = cert_utils.equal_names(
                    cert.parsed.issuer, issuer_cert.parsed.subject
                )

            if match:
                issuers.append((issuer_idx, issuer_cert))

        return issuers

    def _determine_trust_path(self, cert, idx, timestamp, domain_name, full_validation):
        trust_path = [idx] if idx is not None else []
        if cert.trusted is not tls.ScanState.UNDETERMINED:
            return trust_path

        cert.trusted = tls.ScanState.TRUE
        if not cert.has_valid_period(timestamp) and not full_validation:
            return trust_path

        if idx == 0:
            if not cert.has_valid_subject(domain_name) and not full_validation:
                return trust_path

        elif idx is None:
            cert.issuer_cert = cert
            return trust_path

        if cert.self_signed:
            issuers = [(idx, cert)]
            if not self._trust_store.cert_in_trust_store(cert):
                cert.mark_untrusted("self-signed certificate not found in trust store")
                if not full_validation:
                    return trust_path

            else:
                self.root_cert_transmitted = True
                self.root_cert = None

        else:
            issuers = self._issuer_certs(cert)
            # placeholder for certificate from the trust store
            issuers.append((None, None))

        issuer_trust_path = []
        for issuer_idx, issuer_cert in issuers:
            if not issuer_cert:
                issuer_cert = self._trust_store.issuer_in_trust_store(
                    cert.parsed.issuer
                )
                if issuer_cert:
                    issuer_cert.from_trust_store = True
                    self.root_cert_transmitted = False
                    self.root_cert = issuer_cert

                else:
                    if len(issuers) == 1:
                        cert.mark_untrusted(
                            f"issuer certificate "
                            f'"{cert.parsed.issuer.rfc4514_string()}" not found '
                            f"in trust store"
                        )
                    break

            if not cert.self_signed:
                issuer_trust_path = self._determine_trust_path(
                    issuer_cert, issuer_idx, timestamp, domain_name, full_validation,
                )
                if issuer_cert.trusted is tls.ScanState.FALSE:
                    continue

            else:
                issuer_trust_path = []

            cert.issuer_cert = issuer_cert

            try:
                issuer_cert.validate_cert_signature(cert)

            except Exception:
                cert.mark_untrusted("invalid signature")
                continue

            if (
                not self._valid_crl(cert, issuer_cert, timestamp)
                and not full_validation
            ):
                continue

            if (
                not self._valid_ocsp(cert, issuer_cert, timestamp)
                and not full_validation
            ):
                continue

            if issuer_idx is not None:
                if issuer_idx < idx:
                    self.issues.append("certificates of the chain are not in sequence")

            break

        return trust_path + issuer_trust_path

    def validate(
        self, timestamp: datetime.datetime, domain_name: str, raise_on_failure: bool
    ) -> None:
        """Validates the certificate chain. Only the minimal checks are supported.

        If a discrepancy is found, an exception is raised (depending on
        raise_on_failure).

        Arguments:
            timestamp: the timestamp to check against
            domain_name: the domain name to validate the host certificate against
            raise_on_failure: whether an exception shall be raised if the
                validation fails or not. Useful for a TLS scan, as the scan
                shall continue.

        Raises:
            tls.UntrustedCertificate: in case a certificate within the chain cannot be
                validated and `raise_on_failure` is True.
        """

        server_cert = self.certificates[0]
        valid = self._cert_chain_cache.get_cached_validation_state(self)
        if valid is not None:
            logging.debug(
                f"using certificate chain validation status {valid} from cache"
            )
            if not valid and raise_on_failure:
                raise tls.UntrustedCertificate(
                    f"cached status for {self.certificates[0]} is not valid"
                )
            return

        trust_path = self._determine_trust_path(
            server_cert, 0, timestamp, domain_name, not raise_on_failure
        )

        self.successful_validation = all(
            [self.certificates[idx].trusted is tls.ScanState.TRUE for idx in trust_path]
        )
        self._cert_chain_cache.update_cached_validation_state(self)

        if raise_on_failure and not self.successful_validation:
            issue = "not trusted"
            for idx in trust_path:
                if self.certificates[idx].issues:
                    issue = self.certificates[idx].issues[0]
                    break

            raise tls.UntrustedCertificate(f"certificate {server_cert}: {issue}")

        # And now check for gratuitous certificate in the chain
        if not raise_on_failure and trust_path:
            for idx, cert in enumerate(self.certificates):
                if idx not in trust_path:
                    if cert.trusted is tls.ScanState.UNDETERMINED:
                        cert.issues.append(
                            "gratuitous certificate, not part of trust chain"
                        )

                    elif cert.trusted is tls.ScanState.FALSE:
                        cert.issues.append(
                            "certificate part of untrusted alternate trust path"
                        )

    def serialize(self) -> List[str]:
        """Serialize the certificate chain

        Returns:
            A list of certificates which build the chain. The format is a str,
            representing the DER-format for each certificate.
        """
        return [cert.bytes.hex() for cert in self.certificates]

    def deserialize(self, chain: List[str]) -> None:
        """Deserializes a certificate chain.

        Arguments:
            chain (list of str): The list of certificates of the chain. Each certificate
                is represented in DER-format as a string.
        """
        for cert in chain:
            self.append_bin_cert(bytes.fromhex(cert))


class CertChainCache(object):
    """Caches the validation state for a given certificate chain
    """

    _CACHE_SIZE = 100

    def __init__(self):
        self._cache = {}

    def get_cached_validation_state(self, cert_chain: CertChain) -> bool:
        """Returns the validation state of a certificate chain from the cache.

        If not present in the cache, the certificate chain is added with the status
        False.

        Arguments:
            cert_chain: the certificate chain object

        Returns:
            the validation status of the certificate chain from the cache or
            None if the certificate chain is not found.
        """

        val = self._cache.get(cert_chain.digest)
        if val is None:
            # Here keep cache at a reasonable size
            if len(self._cache) >= self._CACHE_SIZE:
                del self._cache[next(iter(self._cache))]

            self._cache[cert_chain.digest] = False

        return val

    def update_cached_validation_state(self, cert_chain: CertChain) -> None:
        """Updates a certificate chain entry in the cache.

        Arguments:
            cert_chain: the certificate chain object
        """

        self._cache[cert_chain.digest] = cert_chain.successful_validation
