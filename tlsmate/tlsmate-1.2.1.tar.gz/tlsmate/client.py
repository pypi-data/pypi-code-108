# -*- coding: utf-8 -*-
"""Module containing the class for the client
"""
# import basic stuff
import time
from typing import List, Optional

# import own stuff
import tlsmate.client_auth as client_auth
import tlsmate.client_state as client_state
import tlsmate.config as conf
import tlsmate.connection as conn
import tlsmate.msg as msg
import tlsmate.recorder as rec
import tlsmate.structs as structs
import tlsmate.tls as tls

# import other stuff


class Client(object):
    """The class representing a TLS client

    Connections are initiated by the TLS client, and it also stores data across
    several connections, like session tickets.

    A TLS client has a dedicated client profile
    (:obj:`tlsmate.client_state.ClientProfile`) which controls the TLS
    connections, e.g. the supported TLS versions, the supported cipher suites
    and other attributes are defined there (e.g. set of supported groups,
    whether encrypt-then-mac is supported, etc.)

    The client profile is used for setting up TLS messages in case only the
    message class and not a message instance is provided in the test case.
    """

    # The following properties are deprecated and will likely be removed with the next
    # major release. They are kept here for backward compatibility reasons.
    # TODO: remove properties with the next major release.
    @property
    def alert_on_invalid_cert(self) -> bool:
        """Controls the behavior in case a certificate or
        the complete certificate chain cannot successfully be validated. If
        True, the connection will be closed with a fatal alert. If False, the
        connection continues. The latter is useful for scanning a server, as
        the handshake would be aborted prematurely otherwise.
        """
        return self._alert_on_invalid_cert

    @alert_on_invalid_cert.setter
    def alert_on_invalid_cert(self, val: bool) -> None:
        self._alert_on_invalid_cert = val
        self._config.set("alert_on_invalid_cert", val)

    @property
    def server_issues(self) -> List[structs.Malfunction]:
        return self.session.server_issues

    def __init__(
        self,
        config: conf.Configuration,
        recorder: rec.Recorder,
        client_auth: client_auth.ClientAuth,
    ) -> None:
        """Initialize the client object

        Args:
            tlsmate: the tlsmate application object.
        """
        self._config = config
        self._recorder = recorder
        self._client_auth = client_auth

        self._host: str = self._config.get("host")
        self._port: int = self._config.get("port")
        self._sni: str = self._config.get("sni") or self._host
        self.profile: client_state.ClientProfile = client_state.create_profile(
            tls.Profile.MODERN
        )
        self.session = client_state.SessionState(
            self._host, self._port, self._sni, self._recorder
        )
        self.alert_on_invalid_cert = True

    def init_profile(
        self, profile_values: Optional[structs.ProfileValues] = None
    ) -> None:
        """Resets the client profile to a very basic state

        :note:
            At least the versions and the cipher_suite list must be provided before
            this profile can be used.

        Compression methods is set to [:obj:`tlsmate.tls.CompressionMethod.NULL`], and
        by default the sni extension is enabled. Everything else is empty or disabled.

        Arguments:
            profile_values: the profile values to additionally use to
                initialize the client profile
        """

        self.profile = client_state.init_profile(profile_values)

    def set_profile(self, profile: tls.Profile) -> None:
        """Initializes the client according to the given profile.

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

        self.profile = client_state.create_profile(profile)

    def create_connection(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        sni: Optional[str] = None,
    ) -> conn.TlsConnection:
        """Create a new connection object

        Arguments:
            host: the host to contact. If not given, the host is taken from the
                configuration. The given string can be a URL or an IP address.
                port (int): the port number

        Returns:
            the created connection object
        """

        target_host = host or self._host
        target_sni = sni or host or self._sni or self._host
        self._port = port or self._port

        if target_host != self._host or target_sni != self._sni:
            self._host = target_host
            self._sni = target_sni
            self.session = client_state.SessionState(
                target_host, self._port, self._sni, self._recorder,
            )

        self.session.port = self._port

        interval = self._config.get("interval")
        if interval:
            time.sleep(interval / 1000)

        return conn.TlsConnection(
            profile=self.profile,
            session=self.session,
            config=self._config,
            recorder=self._recorder,
            client_auth=self._client_auth,
        )

    def get_sni(self) -> str:
        """Returns the sni.

        This method is deprecated and will likely be removed with the next
        major release. It is kept here for backward compatibility reasons.

        Returns:
            the sni
        """

        # TODO: remove method with the next major release
        return self._sni

    def client_hello(self) -> msg.ClientHello:
        """Constructs a client hello dependent on the client profile and the session.

        This method is deprecated and will likely be removed with the next
        major release. It is kept here for backward compatibility reasons.

        Returns:
            the instantiated ClientHello message
        """

        # TODO: remove method with the next major release
        return msg.client_hello(
            self.profile, self.session, self._recorder, self._client_auth
        )
