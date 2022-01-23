# -*- coding: utf-8 -*-
"""Module for handling client auth (keys & cert chains)
"""
# import basic stuff
import pem
from typing import Any, List, Tuple, Set, Optional

# import own stuff
import tlsmate.cert_chain as cert_chain
import tlsmate.recorder as rec
import tlsmate.tls as tls

# import other stuff
from cryptography.hazmat.primitives import serialization


PrivateKey = Any


class ClientAuth(object):
    """Manages client authentication (multiple keys and cert chains)

    This class can hold multiple different client authentication sets. Each set
    consists of the private key and the certificate chain that will be provided
    to the server. Good practice: the chain does not contain the root certificate.

    Arguments:
        tlsmate: The tlsmate application object.
    """

    def __init__(self, recorder: rec.Recorder) -> None:
        self._used_idx: Set[int] = set()
        self._auth: List[Tuple[PrivateKey, cert_chain.CertChain]] = []
        self._recorder = recorder

    def add_auth(self, key: PrivateKey, chain: cert_chain.CertChain) -> None:
        """Add a client auth set to this object.

        Arguments:
            key: the private key
            chain: the associated certificate chain.
        """

        self._auth.append((key, chain))

    def add_auth_files(self, key_file: str, chain_file: str) -> None:
        """Add a set of files to the instances of this class.

        A set consists of a file in PEM-format containing the private key, and a file
        containing the certificate chain presented to the server in PEM-format.

        Arguments:
            key_file: the name of the key file
            chain_file: the name of the certificate chain file
        """
        with open(key_file, "rb") as fd:
            key = serialization.load_pem_private_key(fd.read(), password=None)

        chain = cert_chain.CertChain()
        pem_list = pem.parse_file(chain_file)
        for pem_item in pem_list:
            chain.append_pem_cert(pem_item.as_bytes())

        self.add_auth(key, chain)

    def supported(self) -> bool:
        """Provides an indication if client authentication is actually used.

        Returns:
            An indication if client authentication is actually used.
        """

        return bool(self._auth)

    def find_algo(
        self, algo: tls.SignatureScheme, version: tls.Version
    ) -> Optional[int]:
        """Find a client certificate which supports the given signature algorithm.

        Arguments:
            algo: the signature scheme to look for
            version: the TLS version of the connection

        Returns:
            A reference to the client certificate/key which supports the given
            signature algorithm. Returns None if no suitable certificate is found.
        """

        for idx, key_chain in enumerate(self._auth):
            cert = key_chain[1].certificates[0]
            if version is tls.Version.TLS13:
                cert_algos = cert.tls13_signature_algorithms

            else:
                cert_algos = cert.tls12_signature_algorithms

            if algo in cert_algos:
                if self._recorder.is_recording():
                    if idx not in self._used_idx:
                        self._used_idx.add(idx)
                        self._recorder.trace_client_auth(self.serialize_key_chain(idx))
                return idx

        return None

    def serialize_key_chain(self, idx: int) -> Tuple[str, List[str]]:
        """Serialize the set of (key, chain) for a given reference.

        Arguments:
            idx: the reference to the set of (key, certificate chain)

        Returns:
            A list, where the first element represents the serialized key, and
            the seconds element represents the serialized certificate chain.
        """

        key, chain = self._auth[idx]
        key_bytes = key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return key_bytes.hex(), chain.serialize()

    def deserialize_key_chain(self, key_chain: Tuple[str, List[str]]) -> None:
        """Deserializes the pair of the given key/cert-chain.

        Arguments:
            key_chain: contains two elements: the key and the certificate chain.
        """

        key, chain = key_chain
        priv_key = serialization.load_der_private_key(bytes.fromhex(key), None)
        chn = cert_chain.CertChain()
        chn.deserialize(chain)
        self.add_auth(priv_key, chn)

    def get_chain(self, idx: int) -> "cert_chain.CertChain":
        """For the given reference return the corresponding certificate chain.

        Arguments:
            idx: the reference.

        Returns:
            the certificate chain
        """

        return self._auth[idx][1]

    def get_key(self, idx: int) -> bytes:
        """For the given reference return the corresponding private key.

        Arguments:
            idx: the reference.

        Returns:
            the cryptography key object
        """

        return self._auth[idx][0]
