# -*- coding: utf-8 -*-
"""Module defining various structures
"""
# import basic stuff
from typing import NamedTuple, Any, Optional, Type

# import own stuff
import tlsmate.kdf as kdf
import tlsmate.tls as tls

# import other stuff
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives._asymmetric import AsymmetricPadding


class SessionStateId(NamedTuple):
    """Set of items to store a session id in the client.
    """

    session_id: bytes
    cipher_suite: tls.CipherSuite
    version: tls.Version
    master_secret: bytes


class SessionStateTicket(NamedTuple):
    """Set of items to store a session ticket in the client.
    """

    ticket: bytes
    lifetime: int
    cipher_suite: tls.CipherSuite
    version: tls.Version
    master_secret: bytes


class EarlyData(NamedTuple):
    """Set of items required to determine the early data traffic keys
    """

    kdf: kdf.Kdf
    early_secret: bytes
    mac_len: int
    binders_bytes: Optional[bytes] = None


class Cipher(NamedTuple):
    """Set of properties describing a cipher.
    """

    primitive: Optional[tls.CipherPrimitive] = None
    algo: Optional[Any] = None
    c_type: Optional[tls.CipherType] = None
    key_len: Optional[int] = None
    block_size: Optional[int] = None
    iv_len: Optional[int] = None
    tag_length: Optional[int] = None
    cipher_supported: bool = False


class Mac(NamedTuple):
    """Set of properties describing a MAC.
    """

    hash_algo: Type[hashes.HashAlgorithm]
    mac_len: Optional[int]
    key_len: Optional[int]
    hmac_algo: Optional[Type[hashes.HashAlgorithm]]


class Psk(NamedTuple):
    """Set of items to store a TLS1.3 pre-shared key in the client.
    """

    psk: bytearray
    lifetime: int
    age_add: int
    ticket: bytes
    timestamp: float
    cipher_suite: tls.CipherSuite
    version: tls.Version
    hmac: Mac


class SymmetricKeys(NamedTuple):
    """Set of keys
    """

    mac: bytes
    enc: bytes
    iv: bytes


class StateUpdateParams(NamedTuple):
    """Set of properties used to update the record layer state.
    """

    cipher: Cipher
    mac: Mac
    keys: SymmetricKeys
    compr: tls.CompressionMethod
    enc_then_mac: bool
    version: tls.Version
    is_write_state: bool


class CipherSuite(NamedTuple):
    """Set of properties for a cipher suite.
    """

    key_ex: tls.KeyExchangeAlgorithm
    cipher: tls.SymmetricCipher
    mac: tls.HashPrimitive


class RecordLayerMsg(NamedTuple):
    """Set of properties describing a record layer message.
    """

    content_type: tls.ContentType
    version: tls.Version
    fragment: bytes


class UpperLayerMsg(NamedTuple):
    """Set of properties describing an upper layer message.

    "Upper Layer" comprises handshake, ccs and alert protocols.
    """

    content_type: tls.ContentType
    msg_type: tls.HandshakeType  # can be CCSType as well
    msg: bytes


class KeyExchange(NamedTuple):
    """Set of properties describing a key exchange method.
    """

    key_ex_type: Optional[tls.KeyExchangeType] = None
    key_auth: Optional[tls.KeyAuthentication] = None
    key_ex_supported: bool = False
    default_sig_scheme: Optional[tls.SignatureScheme] = None


class KeyShareEntry(NamedTuple):
    """Set of properties describing a key share entry.
    """

    group: tls.SupportedGroups
    key_exchange: Optional[bytes]


class CipherSuiteDetails(NamedTuple):
    """Structure which provides details for a cipher suite.
    """

    cipher_suite: tls.CipherSuite
    full_hs: bool = False
    key_exchange_supported: bool = False
    key_algo: Optional[tls.KeyExchangeAlgorithm] = None
    key_algo_struct: Optional[KeyExchange] = None
    cipher: Optional[tls.SymmetricCipher] = None
    cipher_struct: Optional[Cipher] = None
    mac: Optional[tls.HashPrimitive] = None
    mac_struct: Optional[Mac] = None


class ProfileValues(NamedTuple):
    """Structure for the most relevant parameters for client hello
    """

    versions: list = []
    cipher_suites: list = []
    supported_groups: list = []
    signature_algorithms: list = []
    key_shares: list = []
    """Only applicable for TLS1.3"""


class CertSigAlgo(NamedTuple):
    """Structure for certificate signature algorithms
    """

    algo: Optional[Type[hashes.HashAlgorithm]] = None
    padd: Optional[Type[AsymmetricPadding]] = None


class TransportEndpoint(NamedTuple):
    """Structure for host, type and port
    """

    host: str
    port: int
    host_type: tls.HostType


class ResolvedHost(NamedTuple):
    """Result of a DNS resolution
    """

    ipv4_addresses: list
    ipv6_addresses: list


class ConfigItem(NamedTuple):
    """A configuration setting
    """

    name: str
    default: Any = None
    type: Any = str


class Malfunction(NamedTuple):
    """Structure for server malfunction
    """

    issue: tls.ServerIssue
    message: Optional[tls.HandshakeType] = None
    extension: Optional[tls.Extension] = None
