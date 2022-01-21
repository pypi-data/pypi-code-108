r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["CifsServiceSecurity", "CifsServiceSecuritySchema"]
__pdoc__ = {
    "CifsServiceSecuritySchema.resource": False,
    "CifsServiceSecurity": False,
}


class CifsServiceSecuritySchema(ResourceSchema):
    """The fields of the CifsServiceSecurity object"""

    aes_netlogon_enabled = fields.Boolean(data_key="aes_netlogon_enabled")
    r""" Specifies whether or not an AES session key is enabled for the Netlogon channel. """

    encrypt_dc_connection = fields.Boolean(data_key="encrypt_dc_connection")
    r""" Specifies whether encryption is required for domain controller connections. """

    kdc_encryption = fields.Boolean(data_key="kdc_encryption")
    r""" Specifies whether AES-128 and AES-256 encryption is enabled for all Kerberos-based communication with the Active Directory KDC.
To take advantage of the strongest security with Kerberos-based communication, AES-256 and AES-128 encryption can be enabled on the CIFS server.
Kerberos-related communication for CIFS is used during CIFS server creation on the SVM, as well
as during the SMB session setup phase.
The CIFS server supports the following encryption types for Kerberos communication:

    * RC4-HMAC
    * DES
    * AES
When the CIFS server is created, the domain controller creates a computer machine account in
Active Directory. After a newly created machine account authenticates, the KDC and the CIFS server
negotiates encryption types. At this time, the KDC becomes aware of the encryption capabilities of
the particular machine account and uses those capabilities in subsequent communication with the
CIFS server.
In addition to negotiating encryption types during CIFS server creation, the encryption types are
renegotiated when a machine account password is reset. """

    ldap_referral_enabled = fields.Boolean(data_key="ldap_referral_enabled")
    r""" Specifies whether or not LDAP referral chasing is enabled for AD LDAP connections. """

    lm_compatibility_level = fields.Str(data_key="lm_compatibility_level")
    r""" It is CIFS server minimum security level, also known as the LMCompatibilityLevel. The minimum security level is the minimum level of the security tokens that        the CIFS server accepts from SMB clients.
The available values are:

* lm_ntlm_ntlmv2_krb          Accepts LM, NTLM, NTLMv2 and Kerberos
* ntlm_ntlmv2_krb             Accepts NTLM, NTLMv2 and Kerberos
* ntlmv2_krb                  Accepts NTLMv2 and Kerberos
* krb                         Accepts Kerberos only


Valid choices:

* lm_ntlm_ntlmv2_krb
* ntlm_ntlmv2_krb
* ntlmv2_krb
* krb """

    restrict_anonymous = fields.Str(data_key="restrict_anonymous")
    r""" Specifies what level of access an anonymous user is granted. An anonymous user (also known as a "null user") can list or enumerate certain types of system information from Windows hosts on the network, including user names and details, account policies, and share names. Access for the anonymous user can be controlled by specifying one of three access restriction settings.
 The available values are:

 * no_restriction   - No access restriction for an anonymous user.
 * no_enumeration   - Enumeration is restricted for an anonymous user.
 * no_access        - All access is restricted for an anonymous user.


Valid choices:

* no_restriction
* no_enumeration
* no_access """

    session_security = fields.Str(data_key="session_security")
    r""" Specifies client session security for AD LDAP connections.
The available values are:

  * none - No Signing or Sealing.
  * sign - Sign LDAP traffic.
  * seal - Seal and Sign LDAP traffic


Valid choices:

* none
* sign
* seal """

    smb_encryption = fields.Boolean(data_key="smb_encryption")
    r""" Specifies whether encryption is required for incoming CIFS traffic. """

    smb_signing = fields.Boolean(data_key="smb_signing")
    r""" Specifies whether signing is required for incoming CIFS traffic. SMB signing helps to ensure that network traffic between the CIFS server and the client is not compromised. """

    try_ldap_channel_binding = fields.Boolean(data_key="try_ldap_channel_binding")
    r""" Specifies whether or not channel binding is attempted in the case of TLS/LDAPS. """

    use_ldaps = fields.Boolean(data_key="use_ldaps")
    r""" Specifies whether or not to use use LDAPS for secure Active Directory LDAP connections
by using the TLS/SSL protocols. """

    use_start_tls = fields.Boolean(data_key="use_start_tls")
    r""" Specifies whether or not to use SSL/TLS for allowing secure LDAP communication with
Active Directory LDAP servers. """

    @property
    def resource(self):
        return CifsServiceSecurity

    gettable_fields = [
        "aes_netlogon_enabled",
        "encrypt_dc_connection",
        "kdc_encryption",
        "ldap_referral_enabled",
        "lm_compatibility_level",
        "restrict_anonymous",
        "session_security",
        "smb_encryption",
        "smb_signing",
        "try_ldap_channel_binding",
        "use_ldaps",
        "use_start_tls",
    ]
    """aes_netlogon_enabled,encrypt_dc_connection,kdc_encryption,ldap_referral_enabled,lm_compatibility_level,restrict_anonymous,session_security,smb_encryption,smb_signing,try_ldap_channel_binding,use_ldaps,use_start_tls,"""

    patchable_fields = [
        "aes_netlogon_enabled",
        "encrypt_dc_connection",
        "kdc_encryption",
        "ldap_referral_enabled",
        "restrict_anonymous",
        "session_security",
        "smb_encryption",
        "smb_signing",
        "try_ldap_channel_binding",
        "use_ldaps",
        "use_start_tls",
    ]
    """aes_netlogon_enabled,encrypt_dc_connection,kdc_encryption,ldap_referral_enabled,restrict_anonymous,session_security,smb_encryption,smb_signing,try_ldap_channel_binding,use_ldaps,use_start_tls,"""

    postable_fields = [
        "aes_netlogon_enabled",
        "encrypt_dc_connection",
        "kdc_encryption",
        "ldap_referral_enabled",
        "restrict_anonymous",
        "session_security",
        "smb_encryption",
        "smb_signing",
        "try_ldap_channel_binding",
        "use_ldaps",
        "use_start_tls",
    ]
    """aes_netlogon_enabled,encrypt_dc_connection,kdc_encryption,ldap_referral_enabled,restrict_anonymous,session_security,smb_encryption,smb_signing,try_ldap_channel_binding,use_ldaps,use_start_tls,"""


class CifsServiceSecurity(Resource):

    _schema = CifsServiceSecuritySchema
