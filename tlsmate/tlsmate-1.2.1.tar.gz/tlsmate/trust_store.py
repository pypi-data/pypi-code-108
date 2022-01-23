# -*- coding: utf-8 -*-
"""Module defining a class representing the trust store
"""
# import basic stuff
import contextlib
import logging
import os
from typing import List, Any, Optional

# import own stuff
import tlsmate.cert as crt
import tlsmate.cert_utils as cert_utils
import tlsmate.recorder as rec

# import other stuff
import pem
from cryptography.hazmat.primitives.serialization import Encoding


class TrustStore(object):
    """Represents a trust store containing trusted root certificates

    Objects of this class are iterable, yielding the certificates one by one.

    Arguments:
        ca_files (list of file names): A list of files which contain certificates in
            PEM-format.
    """

    def __init__(self, recorder: rec.Recorder) -> None:
        self._recorder = recorder
        self._ca_files: Optional[List[str]] = None
        self._cert_cache: List[crt.Certificate] = []
        self._fingerprint_cache: List[bytes] = []

    def set_ca_files(self, ca_files: List[str]) -> None:
        """Store the CA files containing certs in PEM format

        Arguments:
            ca_files: A list of file names. Each file can contain multiple
                certificates in PEM format.
        """

        if ca_files:
            for ca_file in ca_files:
                logging.debug(f"using {ca_file} as trust store")
            self._ca_files = ca_files

    def __iter__(self):
        """Iterator over all certificates
        """

        for cert in self._cert_cache:
            yield cert

        if self._ca_files:
            with contextlib.redirect_stderr(open(os.devnull, "w")):
                for file_name in self._ca_files:
                    pem_list = pem.parse_file(file_name)
                    for pem_item in pem_list:
                        if not isinstance(pem_item, pem.Certificate):
                            continue
                        yield crt.Certificate(pem=pem_item.as_bytes())

    def add_cert(self, cert: crt.Certificate) -> None:
        """Add a certificate to the trust store if not yet present.

        Arguments:
            The certificate to add
        """

        if cert.fingerprint_sha256 not in self._fingerprint_cache:
            logging.debug(
                f'adding certificate "{cert.parsed.subject.rfc4514_string()}" '
                f"to trust store cache"
            )
            # TODO: resolve type issue
            assert cert.fingerprint_sha256
            self._fingerprint_cache.append(cert.fingerprint_sha256)
            self._cert_cache.append(cert)
            if self._recorder.is_recording():
                cert_pem = cert.parsed.public_bytes(Encoding.DER).hex()
                self._recorder.trace(trust_store=cert_pem)

    def cert_in_trust_store(self, cert: crt.Certificate) -> bool:
        """Checks if a given certificate is present in the trust store.

        Arguments:
            cert: the certificate to check

        Returns:
            True, if the given certificate is present in the trust store
        """

        if self._ca_files is None and not self._cert_cache:
            return False

        for cert2 in self:
            if cert2 == cert:
                self.add_cert(cert2)
                return True

        return False

    def issuer_in_trust_store(self, issuer_name: Any) -> Optional[crt.Certificate]:
        """Returns the certificate for a given issuer name from the trust store.

        Arguments:
            issuer_name: the name of the issuer

        Returns:
            the issuer certificate or None if the certificate is not found.
        """

        for cert in self:
            # TODO: Optimize this, as the issuer_name is string_prepped with
            # always the same result in the loop
            if cert_utils.equal_names(cert.parsed.subject, issuer_name):
                self.add_cert(cert)
                return cert

        return None
