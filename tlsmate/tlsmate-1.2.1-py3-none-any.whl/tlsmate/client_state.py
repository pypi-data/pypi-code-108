# -*- coding: utf-8 -*-
"""Module containing the class for the client state
"""
# import basic stuff
from dataclasses import dataclass, field
from typing import List, Optional, Union, Mapping, Callable, Dict

# import own stuff
import tlsmate.key_exchange as kex
import tlsmate.recorder as rec
import tlsmate.structs as structs
import tlsmate.tls as tls


@dataclass
class ClientProfile(object):
    """Data class defining the TLS profile of the client.

    The client profile defines the protocol parameters, extensions and features
    which are supported by the client. The data is used when ``tlsmate`` generates
    the ClientHello message autonomously, e.g., when using::

        conn.send(msg.ClientHello)

        or

        conn.handshake()

    The client profile is used as well to check a received ServerHello for
    consistency, e.g., the version provided by the server must be in the
    version list of the client profile.

    Attributes:
        versions: The list of protocol versions the client shall support. Note,
            that the highest version will be picked to offer it in a
            ClientHello. For the extension SupportedVersions this list will be
            ordered, so that the highest version comes first. Arbitrary integer
            values can be provided in the list as well, allowing to check if
            the server ignores unknown values.
            Default: []
        compression_methods: A list of supported compression methods. This list
            will be used to populate the compression list in the ClientHello
            message.
            Default: [:obj:`tlsmate.tls.CompressionMethod.NULL`]
        cipher_suites: A list of cipher suites which will be offered to the
            server in the sequence given. Note, that arbitrary integer values
            are supported as well, allowing to check if the server ignores
            unknown values.
            Default: []
        support_sni: An indication if the SNI extension shall be supported. If
            True, the SNI will be taken from the CLI parameter ``--sni`` or (if
            not given), from the host name.
            Default: True
        ec_point_formats: The list of ec-point formats supported by the client.
            If set to None, the extension will not be generated.
            Default: None
        supported_groups: The list of named groups supported by the client. If
            set to None, the extension will not be present in the ClientHello
            message. Note, that arbitrary integer values are supported as well,
            allowing to check if the server ignores unknown values.
            Default: None
        signature_algorithms: The list of signature algorithms supported by the
            client. If set to None, the extension will not be present in the
            ClientHello message. Note, that arbitrary integer values are
            supported as well, allowing to check if the server ignores unknown
            values.
            Default: None
        heartbeat_mode: The mode which is offered in the heartbeat extension.
            If set to None, the extension will not be setup when using the
            :meth:`Client.client_hello` method.
            Default: None
        support_session_id: An indication if the client shall support
            resumption via the session id. Received session ids from the server
            will be offered in subsequent handshakes. Default: False
        support_session_ticket: An indication if the client shall support
            resumption via the extensions SessionTicket. Received session
            tickets from the server will be offered in subsequent handshakes.
            Default: False
        support_extended_master_secret: An indication if the client shall
            support the extensions ExtendedMasterSecret.
            Default: False
        support_encrypt_then_mac: An indication if the client shall support the
            EncryptThenMac extension.
            Default: False
        support_secure_renegotiation: An indication if the client shall support
            secure renegotiation. This will generate the RenegotiationInfo
            extension.
            Default: False
        support_scsv_renegotiation: An indication, if the cipher suite value
            TLS_EMPTY_RENEGOTIATION_INFO_SCSV shall be added to the cipher
            suite list. Only applicable if support_secure_renegotiation is
            True.
            Default: False
        support_psk: An indication whether the client offers a PSK with the
            ClientHello (i.e. NewSessionTicket message have been received
            before).
            Default: False
        support_status_request: An indication, if the extensions status request
            shall be supported.
            Default: False
        support_status_request_v2: The status type of the request. NONE is used
            to suppress the extension.
            Default: NONE
        key_shares: The list of key shares supported for TLS1.3. Note, that
            arbitrary integer values are supported as well, allowing to check
            if the server ignores unknown values.
            Default: None
        psk_key_exchange_modes: The list of PSK key exchange modes used in the
            extension psk_key_exchange_modes. Note, that arbitrary integer
            values are supported as well, allowing to check if the server
            ignores unknown values.
            Default: None
        early_data: The application data to be sent with 0-RTT. TLS1.3 only. If
            None, then no early data will be sent. Early data can only be sent
            in subsequent abbreviated handshakes.
            Default: None
        client_auth_supported: True, if client key and client certificate is present.
    """

    # common for all versions
    versions: List = field(default_factory=lambda: [])
    compression_methods: List = field(
        default_factory=lambda: [tls.CompressionMethod.NULL]
    )
    cipher_suites: List = field(default_factory=lambda: [])

    support_sni: bool = True
    ec_point_formats: Optional[List[Union[tls.EcPointFormat, int]]] = None
    supported_groups: Optional[List[tls.SupportedGroups]] = None
    signature_algorithms: Optional[List[Union[tls.SignatureScheme, int]]] = None
    heartbeat_mode: Optional[tls.HeartbeatMode] = None
    support_status_request: bool = False
    support_status_request_v2: tls.StatusType = tls.StatusType.NONE
    client_auth_supported: bool = False

    # TLS1.2 and below
    support_session_id: bool = False
    support_session_ticket: bool = False
    support_extended_master_secret: bool = False
    support_encrypt_then_mac: bool = False
    support_secure_renegotiation: bool = False
    support_scsv_renegotiation: bool = False

    # TLS1.3 specific
    support_psk: bool = False
    key_shares: Optional[List[tls.SupportedGroups]] = None
    psk_key_exchange_modes: Optional[List[tls.PskKeyExchangeMode]] = None
    early_data: Optional[bytes] = None


def _client_profile_interoperability() -> ClientProfile:
    """Define profile for interoperability, like used in modern browsers

    Profile properties:
      - TLS Versions 1.0 - 1.3
      - ECDHE cipher & RSA-based key transport
      - AESGCM, AES, CHACHA_POLY and 3DES as last resort
      - Signature algorithms: ECDSA+SHA1, RSA PKCS1+SHA1 as last resort
      - Resumption, encrypt-then-mac, extended-master-secret
      - pskmode psk_dhe
    """
    return ClientProfile(
        versions=[
            tls.Version.TLS10,
            tls.Version.TLS11,
            tls.Version.TLS12,
            tls.Version.TLS13,
        ],
        cipher_suites=[
            tls.CipherSuite.TLS_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_CHACHA20_POLY1305_SHA256,
            tls.CipherSuite.TLS_AES_256_GCM_SHA384,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA,
            tls.CipherSuite.TLS_RSA_WITH_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_RSA_WITH_AES_256_GCM_SHA384,
            tls.CipherSuite.TLS_RSA_WITH_AES_128_CBC_SHA,
            tls.CipherSuite.TLS_RSA_WITH_AES_256_CBC_SHA,
            tls.CipherSuite.TLS_RSA_WITH_3DES_EDE_CBC_SHA,
        ],
        supported_groups=[
            tls.SupportedGroups.X25519,
            tls.SupportedGroups.SECP256R1,
            tls.SupportedGroups.SECP384R1,
            tls.SupportedGroups.SECP521R1,
        ],
        signature_algorithms=[
            tls.SignatureScheme.ECDSA_SECP256R1_SHA256,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA256,
            tls.SignatureScheme.RSA_PKCS1_SHA256,
            tls.SignatureScheme.ECDSA_SECP384R1_SHA384,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA384,
            tls.SignatureScheme.RSA_PKCS1_SHA384,
            tls.SignatureScheme.ECDSA_SECP521R1_SHA512,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA512,
            tls.SignatureScheme.RSA_PKCS1_SHA512,
            tls.SignatureScheme.ECDSA_SHA1,
            tls.SignatureScheme.RSA_PKCS1_SHA1,
        ],
        key_shares=[tls.SupportedGroups.X25519, tls.SupportedGroups.SECP256R1],
        psk_key_exchange_modes=[tls.PskKeyExchangeMode.PSK_DHE_KE],
        ec_point_formats=[tls.EcPointFormat.UNCOMPRESSED],
        support_extended_master_secret=True,
        support_session_id=True,
        support_session_ticket=True,
        support_encrypt_then_mac=True,
    )


def _client_profile_legacy():
    """Define profile for legacy like client

    Profile properties:
      - TLS Versions 1.0 - 1.2
      - ECDHE cipher & DHE & RSA-based key transport
      - AESGCM, AES, CHACHA_POLY and 3DES as last resort
      - Signature algorithms: ECDSA+SHA1, RSA PKCS1+SHA1 as last resort
      - Resumption, encrypt-then-mac, extended-master-secret
    """

    return ClientProfile(
        versions=[tls.Version.TLS10, tls.Version.TLS11, tls.Version.TLS12],
        cipher_suites=[
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA,
            tls.CipherSuite.TLS_DHE_RSA_WITH_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_DHE_RSA_WITH_AES_256_GCM_SHA384,
            tls.CipherSuite.TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256,
            tls.CipherSuite.TLS_DHE_RSA_WITH_AES_128_CBC_SHA256,
            tls.CipherSuite.TLS_DHE_RSA_WITH_AES_256_CBC_SHA256,
            tls.CipherSuite.TLS_DHE_RSA_WITH_AES_128_CBC_SHA,
            tls.CipherSuite.TLS_DHE_RSA_WITH_AES_256_CBC_SHA,
            tls.CipherSuite.TLS_RSA_WITH_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_RSA_WITH_AES_256_GCM_SHA384,
            tls.CipherSuite.TLS_RSA_WITH_AES_128_CBC_SHA,
            tls.CipherSuite.TLS_RSA_WITH_AES_256_CBC_SHA,
            tls.CipherSuite.TLS_RSA_WITH_3DES_EDE_CBC_SHA,
        ],
        supported_groups=[
            tls.SupportedGroups.X25519,
            tls.SupportedGroups.SECP256R1,
            tls.SupportedGroups.SECP384R1,
            tls.SupportedGroups.SECP521R1,
        ],
        signature_algorithms=[
            tls.SignatureScheme.ECDSA_SECP256R1_SHA256,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA256,
            tls.SignatureScheme.RSA_PKCS1_SHA256,
            tls.SignatureScheme.ECDSA_SECP384R1_SHA384,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA384,
            tls.SignatureScheme.RSA_PKCS1_SHA384,
            tls.SignatureScheme.ECDSA_SECP521R1_SHA512,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA512,
            tls.SignatureScheme.RSA_PKCS1_SHA512,
            tls.SignatureScheme.ECDSA_SHA1,
            tls.SignatureScheme.RSA_PKCS1_SHA1,
        ],
        ec_point_formats=[tls.EcPointFormat.UNCOMPRESSED],
        support_extended_master_secret=True,
        support_session_id=True,
        support_session_ticket=True,
        support_encrypt_then_mac=True,
    )


def _client_profile_modern():
    """Define profile for "modern" configurations

    Profile properties:
      - TLS Versions 1.2 + 1.3
      - ECDHE cipher
      - AESGCM, CHACHA_POLY
      - signatures: ECDSA + PSS_RSAE
      - Resumption, encrypt-then-mac, extended-master-secret
      - pskmode psk_dhe
    """

    return ClientProfile(
        versions=[tls.Version.TLS12, tls.Version.TLS13],
        cipher_suites=[
            tls.CipherSuite.TLS_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_CHACHA20_POLY1305_SHA256,
            tls.CipherSuite.TLS_AES_256_GCM_SHA384,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256,
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
            tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
        ],
        supported_groups=[
            tls.SupportedGroups.X25519,
            tls.SupportedGroups.SECP256R1,
            tls.SupportedGroups.SECP384R1,
            tls.SupportedGroups.SECP521R1,
        ],
        signature_algorithms=[
            tls.SignatureScheme.ECDSA_SECP256R1_SHA256,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA256,
            tls.SignatureScheme.ECDSA_SECP384R1_SHA384,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA384,
            tls.SignatureScheme.ECDSA_SECP521R1_SHA512,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA512,
        ],
        key_shares=[tls.SupportedGroups.X25519, tls.SupportedGroups.SECP256R1],
        psk_key_exchange_modes=[tls.PskKeyExchangeMode.PSK_DHE_KE],
        ec_point_formats=[tls.EcPointFormat.UNCOMPRESSED],
        support_sni=True,
        support_extended_master_secret=True,
        support_session_id=True,
        support_session_ticket=True,
    )


def _client_profile_tls13():
    """Define profile for TLS1.3 only.

    Profile properties:
      - TLS Version 1.3
      - AESGCM + CHACHA_POLY
      - pskmode psk_dhe
    """

    return ClientProfile(
        versions=[tls.Version.TLS13],
        cipher_suites=[
            tls.CipherSuite.TLS_AES_128_GCM_SHA256,
            tls.CipherSuite.TLS_CHACHA20_POLY1305_SHA256,
            tls.CipherSuite.TLS_AES_256_GCM_SHA384,
        ],
        supported_groups=[
            tls.SupportedGroups.X25519,
            tls.SupportedGroups.SECP256R1,
            tls.SupportedGroups.SECP384R1,
            tls.SupportedGroups.SECP521R1,
        ],
        signature_algorithms=[
            tls.SignatureScheme.ECDSA_SECP256R1_SHA256,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA256,
            tls.SignatureScheme.RSA_PKCS1_SHA256,
            tls.SignatureScheme.ECDSA_SECP384R1_SHA384,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA384,
            tls.SignatureScheme.RSA_PKCS1_SHA384,
            tls.SignatureScheme.ECDSA_SECP521R1_SHA512,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA512,
            tls.SignatureScheme.RSA_PKCS1_SHA512,
        ],
        key_shares=[tls.SupportedGroups.X25519, tls.SupportedGroups.SECP256R1],
        psk_key_exchange_modes=[tls.PskKeyExchangeMode.PSK_DHE_KE],
        ec_point_formats=[tls.EcPointFormat.UNCOMPRESSED],
        support_sni=True,
    )


def create_profile(profile: tls.Profile) -> ClientProfile:
    """Creates a client profile according to the given profile.

    The following profiles are supported:

    - :obj:`tlsmate.tls.Profile.INTEROPERABILITY`

      - TLS Versions 1.0 - 1.3
      - ECDHE cipher & RSA-based key transport
      - AESGCM, AES, CHACHA_POLY and 3DES as last resort
      - Signature algorithms: ECDSA+SHA1, RSA PKCS1+SHA1 as last resort
      - Resumption, encrypt-then-mac, extended-master-secret
      - pskmode psk_dhe

    - :obj:`tlsmate.tls.Profile.LEGACY`

      - TLS Versions 1.0 - 1.2
      - ECDHE cipher & DHE & RSA-based key transport
      - AESGCM, AES, CHACHA_POLY and 3DES as last resort
      - Signature algorithms: ECDSA+SHA1, RSA PKCS1+SHA1 as last resort
      - Resumption, encrypt-then-mac, extended-master-secret

    - :obj:`tlsmate.tls.Profile.MODERN`

      - TLS Versions 1.2 + 1.3
      - ECDHE cipher
      - AESGCM, CHACHA_POLY
      - signatures: ECDSA + PSS_RSAE
      - Resumption, encrypt-then-mac, extended-master-secret
      - pskmode psk_dhe

    - :obj:`tlsmate.tls.Profile.TLS13`

      - TLS Version 1.3
      - AESGCM + CHACHA_POLY
      - pskmode psk_dhe

    Arguments:
        profile (:obj:`tlsmate.tls.Profile`): the profile to which the client
            shall be initialized.
    """

    mapping: Mapping[tls.Profile, Callable[[], ClientProfile]] = {
        tls.Profile.INTEROPERABILITY: _client_profile_interoperability,
        tls.Profile.TLS13: _client_profile_tls13,
        tls.Profile.MODERN: _client_profile_modern,
        tls.Profile.LEGACY: _client_profile_legacy,
    }

    if profile not in mapping:
        raise ValueError(f"client profile {profile} unknown")

    return mapping[profile]()


def init_profile(
    profile_values: Optional[structs.ProfileValues] = None,
) -> ClientProfile:
    """Creates a client profile reset to basic settings

    :note:
        At least the versions and the cipher_suite list must be provided before
        this profile can be used.

    Compression methods is set to [:obj:`tlsmate.tls.CompressionMethod.NULL`], and
    by default the sni extension is enabled. Everything else is empty or disabled.

    Arguments:
        profile_values: the profile values to additionally use to
            initialize the client profile
    """

    profile = ClientProfile()
    if profile_values:
        profile.versions = profile_values.versions[:]
        profile.cipher_suites = profile_values.cipher_suites[:]
        if profile_values.supported_groups:
            profile.supported_groups = profile_values.supported_groups[:]

        if profile_values.signature_algorithms:
            profile.signature_algorithms = profile_values.signature_algorithms[:]

        if profile_values.key_shares:
            profile.key_shares = profile_values.key_shares[:]

    return profile


class SessionState(object):
    """Represents the data associated with the targe.

    The lifetime of this object exceeds the lifetime of a connection.
    """

    def __init__(
        self, host: str, port: int, sni: Optional[str], recorder: rec.Recorder
    ) -> None:
        self.recorder = recorder
        self.host: str = host
        self.port: int = port
        self.sni: Optional[str] = sni
        self.session_state_id: Optional[structs.SessionStateId] = None
        self.session_state_ticket: Optional[structs.SessionStateTicket] = None
        self.psks: List[structs.Psk] = []
        self.key_shares: Dict[tls.SupportedGroups, kex.KeyExchange] = {}
        self.version: Optional[tls.Version] = None
        self.cs_details: Optional[structs.CipherSuiteDetails] = None
        self.server_issues: List[structs.Malfunction] = []

    def save_session_state_id(self, session_state: structs.SessionStateId) -> None:
        """Saves a session state

        Args:
            session_state: A session state to be stored on the client level,
                usable to resume connections using the session_id
        """

        self.session_state_id = session_state

    def get_session_state_id(self) -> Optional[structs.SessionStateId]:
        """Get the session state (id)

        Returns:
            the session state to resume a session from
        """

        return self.session_state_id

    def save_session_state_ticket(
        self, session_state: structs.SessionStateTicket
    ) -> None:
        """Saves a session state

        Args:
            session_state: A session state to be stored on the client level,
                usable to resume connections using the session ticket.
        """

        self.session_state_ticket = session_state

    def get_session_state_ticket(self) -> Optional[structs.SessionStateTicket]:
        """Get the session state (ticket)

        Returns:
            the session state to resume a session from
        """

        return self.session_state_ticket

    def save_psk(self, psk: structs.Psk) -> None:
        """Save a TLS1.3 PSK

        Arguments:
            psk: A pre-shared key be stored on the client level, usable to
                resume connections using the pre-shared key extension.
        """

        self.psks.append(psk)

    def report_server_issue(
        self,
        issue: tls.ServerIssue,
        message: Optional[tls.HandshakeType] = None,
        extension: Optional[tls.Extension] = None,
    ) -> None:
        """Store a server issue, if not done

        Arguments:
            issue: the reason for the exception
            message: the message, if applicable
            extension: the extension, if applicable
        """

        malfunction = structs.Malfunction(
            issue=issue, message=message, extension=extension
        )

        if malfunction not in self.server_issues:
            self.server_issues.append(malfunction)

    def create_key_share(self, group: tls.SupportedGroups) -> bytes:
        """Provide the key share for a given group.

        Arguments:
            group: the group to create a key share for

        Returns:
            the key to exchange with the remote side
        """

        key_share = kex.instantiate_named_group(self.recorder, group)
        self.key_shares[group] = key_share
        return key_share.get_key_share()
