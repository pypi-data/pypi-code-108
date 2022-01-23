# -*- coding: utf-8 -*-
"""Module containing various mapping tables

Attributes:
    supported_cipher_suites (dict): maps :obj:`tlsmate.tls.CipherSuite` to
        :obj:`tlsmate.structs.CipherSuite` objects

    supported_ciphers (dict): maps :obj:`tlsmate.tls.SymmetricCipher` to
        :obj:`tlsmate.structs.Cipher` objects

    supported_macs (dict): maps :obj:`tlsmate.tls.HashPrimitive` to
        :obj:`tlsmate.structs.Mac` objects

    key_exchange (dict): maps :obj:`tlsmate.tls.KeyExchangeAlgorithm` to
        :obj:`tlsmate.structs.KeyExchange` objects

    curve_to_group (dict): maps supported group strings to
        :obj:`tlsmate.tls.SupportedGroups` objects
"""
# import basic stuff
from typing import Dict

# import own stuff
import tlsmate.structs as structs
import tlsmate.tls as tls

# import other stuff
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import algorithms, aead

# this map contains all cipher suites for which a full handshake is supported,
# i.e., application data can be exchanged encrypted

supported_cipher_suites: Dict[tls.CipherSuite, structs.CipherSuite] = {
    tls.CipherSuite.TLS_NULL_WITH_NULL_NULL: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.NULL,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.NULL,
    ),
    tls.CipherSuite.TLS_RSA_WITH_NULL_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_RSA_WITH_NULL_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_EXPORT_WITH_RC4_40_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_EXPORT,
        cipher=tls.SymmetricCipher.RC4_40,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_RSA_WITH_RC4_128_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_RSA_WITH_RC4_128_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_EXPORT_WITH_RC2_CBC_40_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_EXPORT,
        cipher=tls.SymmetricCipher.RC2_CBC_40,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_RSA_WITH_IDEA_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.IDEA_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_EXPORT_WITH_DES40_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_EXPORT,
        cipher=tls.SymmetricCipher.DES40_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_WITH_DES_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.DES_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_DSS_EXPORT_WITH_DES40_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS_EXPORT,
        cipher=tls.SymmetricCipher.DES40_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_DES_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.DES_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_RSA_EXPORT_WITH_DES40_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA_EXPORT,
        cipher=tls.SymmetricCipher.DES40_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_DES_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.DES_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_DSS_EXPORT_WITH_DES40_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS_EXPORT,
        cipher=tls.SymmetricCipher.DES40_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_DES_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.DES_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_RSA_EXPORT_WITH_DES40_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA_EXPORT,
        cipher=tls.SymmetricCipher.DES40_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_DES_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.DES_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_ANON_EXPORT_WITH_RC4_40_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON_EXPORT,
        cipher=tls.SymmetricCipher.RC4_40,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_RC4_128_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_DH_ANON_EXPORT_WITH_DES40_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON_EXPORT,
        cipher=tls.SymmetricCipher.DES40_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_DES_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.DES_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_KRB5_WITH_DES_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5,
        cipher=tls.SymmetricCipher.DES_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_KRB5_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_KRB5_WITH_RC4_128_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_KRB5_WITH_IDEA_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5,
        cipher=tls.SymmetricCipher.IDEA_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_KRB5_WITH_DES_CBC_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5,
        cipher=tls.SymmetricCipher.DES_CBC,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_KRB5_WITH_3DES_EDE_CBC_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_KRB5_WITH_RC4_128_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_KRB5_WITH_IDEA_CBC_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5,
        cipher=tls.SymmetricCipher.IDEA_CBC,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_KRB5_EXPORT_WITH_DES_CBC_40_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5_EXPORT,
        cipher=tls.SymmetricCipher.DES_CBC_40,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_KRB5_EXPORT_WITH_RC2_CBC_40_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5_EXPORT,
        cipher=tls.SymmetricCipher.RC2_CBC_40,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_KRB5_EXPORT_WITH_RC4_40_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5_EXPORT,
        cipher=tls.SymmetricCipher.RC4_40,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_KRB5_EXPORT_WITH_DES_CBC_40_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5_EXPORT,
        cipher=tls.SymmetricCipher.DES_CBC_40,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_KRB5_EXPORT_WITH_RC2_CBC_40_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5_EXPORT,
        cipher=tls.SymmetricCipher.RC2_CBC_40,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_KRB5_EXPORT_WITH_RC4_40_MD5: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.KRB5_EXPORT,
        cipher=tls.SymmetricCipher.RC4_40,
        mac=tls.HashPrimitive.MD5,
    ),
    tls.CipherSuite.TLS_PSK_WITH_NULL_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_NULL_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_NULL_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_WITH_NULL_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_AES_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_CAMELLIA_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_CAMELLIA_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_CAMELLIA_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_CAMELLIA_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_CAMELLIA_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_CAMELLIA_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_AES_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_AES_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_AES_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_AES_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_AES_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_CAMELLIA_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_CAMELLIA_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_CAMELLIA_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_CAMELLIA_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_CAMELLIA_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_CAMELLIA_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_PSK_WITH_RC4_128_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_PSK_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_PSK_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_PSK_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_RC4_128_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_RC4_128_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_WITH_SEED_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.SEED_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_SEED_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.SEED_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_SEED_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.SEED_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_SEED_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.SEED_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_SEED_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.SEED_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_SEED_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.SEED_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_RSA_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_PSK_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_PSK_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_AES_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_PSK_WITH_NULL_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_NULL_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_AES_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_NULL_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_NULL_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_AES_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_NULL_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_NULL_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_CAMELLIA_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_CAMELLIA_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_CAMELLIA_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_CAMELLIA_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_CAMELLIA_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_CAMELLIA_256_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_NULL_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_RC4_128_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_NULL_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_RC4_128_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_NULL_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_RC4_128_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_NULL_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_RC4_128_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_ANON_WITH_NULL_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ANON,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_ANON_WITH_RC4_128_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ANON,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_ANON_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ANON,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_ANON_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ANON,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDH_ANON_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ANON,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_SRP_SHA_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.SRP_SHA,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_SRP_SHA_RSA_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.SRP_SHA_RSA,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_SRP_SHA_DSS_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.SRP_SHA_DSS,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_SRP_SHA_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.SRP_SHA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_SRP_SHA_RSA_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.SRP_SHA_RSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_SRP_SHA_DSS_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.SRP_SHA_DSS,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_SRP_SHA_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.SRP_SHA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_SRP_SHA_RSA_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.SRP_SHA_RSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_SRP_SHA_DSS_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.SRP_SHA_DSS,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_AES_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_RC4_128_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.RC4_128,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_3DES_EDE_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_AES_128_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_AES_256_CBC_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_AES_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.AES_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_AES_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.AES_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_NULL_SHA: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA1,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_NULL_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_NULL_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.NULL,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_PSK_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_PSK_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_ARIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.ARIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_ARIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.ARIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_ARIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.ARIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_ARIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.ARIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_CAMELLIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_CAMELLIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_CAMELLIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_CAMELLIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_RSA_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_DSS_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_DSS_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_DSS,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DH_ANON_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DH_ANON,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_ECDSA_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_ECDSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDH_RSA_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDH_RSA,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_PSK_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_CAMELLIA_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_CAMELLIA_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_PSK_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_CAMELLIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_CAMELLIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_CAMELLIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_CAMELLIA_128_CBC_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_128_CBC,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_CAMELLIA_256_CBC_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.CAMELLIA_256_CBC,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_RSA_WITH_AES_128_CCM: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.AES_128_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_AES_256_CCM: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.AES_256_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_AES_128_CCM: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.AES_128_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_AES_256_CCM: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.AES_256_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_AES_128_CCM_8: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.AES_128_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_WITH_AES_256_CCM_8: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA,
        cipher=tls.SymmetricCipher.AES_256_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_AES_128_CCM_8: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.AES_128_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_AES_256_CCM_8: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.AES_256_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_AES_128_CCM: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.AES_128_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_AES_256_CCM: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.AES_256_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_AES_128_CCM: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.AES_128_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_AES_256_CCM: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.AES_256_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_AES_128_CCM_8: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.AES_128_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_AES_256_CCM_8: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.AES_256_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_DHE_WITH_AES_128_CCM_8: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK_DHE,
        cipher=tls.SymmetricCipher.AES_128_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_DHE_WITH_AES_256_CCM_8: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK_DHE,
        cipher=tls.SymmetricCipher.AES_256_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_CCM: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.AES_128_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_CCM: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.AES_256_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.AES_128_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_CCM_8: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.AES_256_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECCPWD_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECCPWD,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECCPWD_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECCPWD,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECCPWD_WITH_AES_128_CCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECCPWD,
        cipher=tls.SymmetricCipher.AES_128_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECCPWD_WITH_AES_256_CCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECCPWD,
        cipher=tls.SymmetricCipher.AES_256_CCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_RSA,
        cipher=tls.SymmetricCipher.CHACHA20_POLY1305,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
        cipher=tls.SymmetricCipher.CHACHA20_POLY1305,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_RSA,
        cipher=tls.SymmetricCipher.CHACHA20_POLY1305,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_PSK_WITH_CHACHA20_POLY1305_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.PSK,
        cipher=tls.SymmetricCipher.CHACHA20_POLY1305,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_CHACHA20_POLY1305_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.CHACHA20_POLY1305,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_DHE_PSK_WITH_CHACHA20_POLY1305_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.DHE_PSK,
        cipher=tls.SymmetricCipher.CHACHA20_POLY1305,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_RSA_PSK_WITH_CHACHA20_POLY1305_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.RSA_PSK,
        cipher=tls.SymmetricCipher.CHACHA20_POLY1305,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_AES_128_CCM_8_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.AES_128_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_ECDHE_PSK_WITH_AES_128_CCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.ECDHE_PSK,
        cipher=tls.SymmetricCipher.AES_128_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    # ********************
    # TLS1.3 cipher suites
    # ********************
    tls.CipherSuite.TLS_AES_128_GCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.TLS13_KEY_SHARE,
        cipher=tls.SymmetricCipher.TLS13_AES_128_GCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_AES_256_GCM_SHA384: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.TLS13_KEY_SHARE,
        cipher=tls.SymmetricCipher.TLS13_AES_256_GCM,
        mac=tls.HashPrimitive.SHA384,
    ),
    tls.CipherSuite.TLS_CHACHA20_POLY1305_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.TLS13_KEY_SHARE,
        cipher=tls.SymmetricCipher.CHACHA20_POLY1305,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_AES_128_CCM_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.TLS13_KEY_SHARE,
        cipher=tls.SymmetricCipher.TLS13_AES_128_CCM,
        mac=tls.HashPrimitive.SHA256,
    ),
    tls.CipherSuite.TLS_AES_128_CCM_8_SHA256: structs.CipherSuite(
        key_ex=tls.KeyExchangeAlgorithm.TLS13_KEY_SHARE,
        cipher=tls.SymmetricCipher.TLS13_AES_128_CCM_8,
        mac=tls.HashPrimitive.SHA256,
    ),
}

# map cipher to various parameters relevant for the record layer

supported_ciphers: Dict[tls.SymmetricCipher, structs.Cipher] = {
    tls.SymmetricCipher.AES_128_CBC: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=algorithms.AES,
        c_type=tls.CipherType.BLOCK,
        key_len=16,
        block_size=16,
        iv_len=16,
        tag_length=None,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.AES_256_CBC: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=algorithms.AES,
        c_type=tls.CipherType.BLOCK,
        key_len=32,
        block_size=16,
        iv_len=16,
        tag_length=None,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.AES_128_GCM: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=aead.AESGCM,
        c_type=tls.CipherType.AEAD,
        key_len=16,
        block_size=16,
        iv_len=4,
        tag_length=16,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.AES_256_GCM: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=aead.AESGCM,
        c_type=tls.CipherType.AEAD,
        key_len=32,
        block_size=16,
        iv_len=4,
        tag_length=16,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.AES_128_CCM: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=aead.AESCCM,
        c_type=tls.CipherType.AEAD,
        key_len=16,
        block_size=16,
        iv_len=4,
        tag_length=16,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.AES_128_CCM_8: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=aead.AESCCM,
        c_type=tls.CipherType.AEAD,
        key_len=16,
        block_size=16,
        iv_len=4,
        tag_length=8,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.AES_256_CCM: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=aead.AESCCM,
        c_type=tls.CipherType.AEAD,
        key_len=32,
        block_size=16,
        iv_len=4,
        tag_length=16,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.AES_256_CCM_8: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=aead.AESCCM,
        c_type=tls.CipherType.AEAD,
        key_len=32,
        block_size=16,
        iv_len=4,
        tag_length=8,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.CHACHA20_POLY1305: structs.Cipher(
        primitive=tls.CipherPrimitive.CHACHA,
        algo=aead.ChaCha20Poly1305,
        c_type=tls.CipherType.AEAD,
        key_len=32,
        block_size=16,
        iv_len=12,
        tag_length=16,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.TRIPPLE_DES_EDE_CBC: structs.Cipher(
        primitive=tls.CipherPrimitive.TRIPPLE_DES,
        algo=algorithms.TripleDES,
        c_type=tls.CipherType.BLOCK,
        key_len=24,
        block_size=8,
        iv_len=8,
        tag_length=None,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.CAMELLIA_128_CBC: structs.Cipher(
        primitive=tls.CipherPrimitive.CAMELLIA,
        algo=algorithms.Camellia,
        c_type=tls.CipherType.BLOCK,
        key_len=16,
        block_size=16,
        iv_len=16,
        tag_length=None,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.CAMELLIA_256_CBC: structs.Cipher(
        primitive=tls.CipherPrimitive.CAMELLIA,
        algo=algorithms.Camellia,
        c_type=tls.CipherType.BLOCK,
        key_len=32,
        block_size=16,
        iv_len=16,
        tag_length=None,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.IDEA_CBC: structs.Cipher(
        primitive=tls.CipherPrimitive.IDEA,
        algo=algorithms.IDEA,
        c_type=tls.CipherType.BLOCK,
        key_len=16,
        block_size=8,
        iv_len=8,
        tag_length=None,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.RC4_128: structs.Cipher(
        primitive=tls.CipherPrimitive.RC4,
        algo=algorithms.ARC4,
        c_type=tls.CipherType.STREAM,
        key_len=16,
        block_size=None,
        iv_len=0,
        tag_length=None,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.SEED_CBC: structs.Cipher(
        primitive=tls.CipherPrimitive.SEED,
        algo=algorithms.SEED,
        c_type=tls.CipherType.BLOCK,
        key_len=16,
        block_size=16,
        iv_len=16,
        tag_length=None,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.TLS13_AES_128_GCM: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=aead.AESGCM,
        c_type=tls.CipherType.AEAD,
        key_len=16,
        block_size=16,
        iv_len=12,
        tag_length=16,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.TLS13_AES_256_GCM: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=aead.AESGCM,
        c_type=tls.CipherType.AEAD,
        key_len=32,
        block_size=16,
        iv_len=12,
        tag_length=16,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.TLS13_AES_128_CCM: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=aead.AESCCM,
        c_type=tls.CipherType.AEAD,
        key_len=16,
        block_size=16,
        iv_len=12,
        tag_length=16,
        cipher_supported=True,
    ),
    tls.SymmetricCipher.TLS13_AES_128_CCM_8: structs.Cipher(
        primitive=tls.CipherPrimitive.AES,
        algo=aead.AESCCM,
        c_type=tls.CipherType.AEAD,
        key_len=16,
        block_size=16,
        iv_len=12,
        tag_length=8,
        cipher_supported=True,
    ),
    # ***************************
    # List of unsupported ciphers
    # ***************************
    tls.SymmetricCipher.ARIA_128_CBC: structs.Cipher(
        primitive=tls.CipherPrimitive.ARIA, c_type=tls.CipherType.BLOCK
    ),
    tls.SymmetricCipher.ARIA_128_GCM: structs.Cipher(
        primitive=tls.CipherPrimitive.ARIA, c_type=tls.CipherType.AEAD
    ),
    tls.SymmetricCipher.ARIA_256_CBC: structs.Cipher(
        primitive=tls.CipherPrimitive.ARIA, c_type=tls.CipherType.BLOCK
    ),
    tls.SymmetricCipher.ARIA_256_GCM: structs.Cipher(
        primitive=tls.CipherPrimitive.ARIA, c_type=tls.CipherType.AEAD
    ),
    tls.SymmetricCipher.CAMELLIA_128_GCM: structs.Cipher(
        primitive=tls.CipherPrimitive.CAMELLIA, c_type=tls.CipherType.AEAD
    ),
    tls.SymmetricCipher.CAMELLIA_256_GCM: structs.Cipher(
        primitive=tls.CipherPrimitive.CAMELLIA, c_type=tls.CipherType.AEAD
    ),
    tls.SymmetricCipher.DES40_CBC: structs.Cipher(
        primitive=tls.CipherPrimitive.DES, c_type=tls.CipherType.BLOCK
    ),
    tls.SymmetricCipher.DES_CBC: structs.Cipher(
        primitive=tls.CipherPrimitive.DES, c_type=tls.CipherType.BLOCK
    ),
    tls.SymmetricCipher.DES_CBC_40: structs.Cipher(
        primitive=tls.CipherPrimitive.DES, c_type=tls.CipherType.BLOCK
    ),
    tls.SymmetricCipher.NULL: structs.Cipher(
        primitive=tls.CipherPrimitive.NULL, c_type=tls.CipherType.NULL
    ),
    tls.SymmetricCipher.RC2_CBC_40: structs.Cipher(
        primitive=tls.CipherPrimitive.RC2, c_type=tls.CipherType.BLOCK
    ),
    tls.SymmetricCipher.RC4_40: structs.Cipher(
        primitive=tls.CipherPrimitive.RC4, c_type=tls.CipherType.STREAM
    ),
}

# map hash algorithms to mac parameters

supported_macs: Dict[tls.HashPrimitive, structs.Mac] = {
    tls.HashPrimitive.SHA1: structs.Mac(
        hash_algo=hashes.SHA1, mac_len=20, key_len=20, hmac_algo=hashes.SHA256
    ),
    tls.HashPrimitive.SHA256: structs.Mac(
        hash_algo=hashes.SHA256, mac_len=32, key_len=32, hmac_algo=hashes.SHA256
    ),
    tls.HashPrimitive.SHA384: structs.Mac(
        hash_algo=hashes.SHA384, mac_len=48, key_len=48, hmac_algo=hashes.SHA384
    ),
    tls.HashPrimitive.SHA512: structs.Mac(
        hash_algo=hashes.SHA512, mac_len=None, key_len=None, hmac_algo=None
    ),
    tls.HashPrimitive.MD5: structs.Mac(
        hash_algo=hashes.MD5, mac_len=16, key_len=16, hmac_algo=hashes.SHA256
    ),
}

key_exchange: Dict[tls.KeyExchangeAlgorithm, structs.KeyExchange] = {
    tls.KeyExchangeAlgorithm.DHE_DSS: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH,
        key_auth=tls.KeyAuthentication.DSS,
        key_ex_supported=True,
        default_sig_scheme=tls.SignatureScheme.DSA_SHA1,
    ),
    tls.KeyExchangeAlgorithm.DHE_RSA: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH,
        key_auth=tls.KeyAuthentication.RSA,
        key_ex_supported=True,
        default_sig_scheme=tls.SignatureScheme.RSA_PKCS1_SHA1,
    ),
    tls.KeyExchangeAlgorithm.DH_ANON: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH,
        key_auth=tls.KeyAuthentication.NONE,
        key_ex_supported=True,
        default_sig_scheme=None,
    ),
    tls.KeyExchangeAlgorithm.RSA: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.RSA,
        key_auth=tls.KeyAuthentication.NONE,
        key_ex_supported=True,
        default_sig_scheme=tls.SignatureScheme.RSA_PKCS1_SHA1,
    ),
    tls.KeyExchangeAlgorithm.DH_DSS: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH,
        key_auth=tls.KeyAuthentication.DSS,
        key_ex_supported=False,
        default_sig_scheme=tls.SignatureScheme.DSA_SHA1,
    ),
    tls.KeyExchangeAlgorithm.DH_RSA: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH,
        key_auth=tls.KeyAuthentication.RSA,
        key_ex_supported=False,
        default_sig_scheme=tls.SignatureScheme.RSA_PKCS1_SHA1,
    ),
    tls.KeyExchangeAlgorithm.ECDH_ECDSA: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.ECDH,
        key_auth=tls.KeyAuthentication.ECDSA,
        key_ex_supported=True,
        default_sig_scheme=tls.SignatureScheme.ECDSA_SHA1,
    ),
    tls.KeyExchangeAlgorithm.ECDHE_ECDSA: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.ECDH,
        key_auth=tls.KeyAuthentication.ECDSA,
        key_ex_supported=True,
        default_sig_scheme=tls.SignatureScheme.ECDSA_SHA1,
    ),
    tls.KeyExchangeAlgorithm.ECDH_RSA: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.ECDH,
        key_auth=tls.KeyAuthentication.RSA,
        key_ex_supported=True,
        default_sig_scheme=tls.SignatureScheme.RSA_PKCS1_SHA1,
    ),
    tls.KeyExchangeAlgorithm.ECDHE_RSA: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.ECDH,
        key_auth=tls.KeyAuthentication.RSA,
        key_ex_supported=True,
        default_sig_scheme=tls.SignatureScheme.RSA_PKCS1_SHA1,
    ),
    tls.KeyExchangeAlgorithm.DHE_RSA_EXPORT: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH,
        key_auth=tls.KeyAuthentication.RSA,
        key_ex_supported=True,
        default_sig_scheme=tls.SignatureScheme.RSA_PKCS1_SHA1,
    ),
    tls.KeyExchangeAlgorithm.TLS13_KEY_SHARE: structs.KeyExchange(
        key_ex_type=None, key_auth=None, key_ex_supported=True, default_sig_scheme=None
    ),
    # **********************************
    # Algorithms currently not supported
    # **********************************
    tls.KeyExchangeAlgorithm.DHE_DSS_EXPORT: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH, key_auth=tls.KeyAuthentication.DSS
    ),
    tls.KeyExchangeAlgorithm.DHE_PSK: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.DH_ANON_EXPORT: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.DH_DSS_EXPORT: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH, key_auth=tls.KeyAuthentication.DSS
    ),
    tls.KeyExchangeAlgorithm.DH_RSA_EXPORT: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH, key_auth=tls.KeyAuthentication.RSA
    ),
    tls.KeyExchangeAlgorithm.ECCPWD: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.NONE, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.ECDHE_PSK: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.ECDH, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.ECDH_ANON: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.ECDH, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.KRB5: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.NONE, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.KRB5_EXPORT: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.NONE, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.NULL: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.NONE, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.PSK: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.NONE, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.PSK_DHE: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.DH, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.RSA_EXPORT: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.RSA, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.RSA_PSK: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.RSA, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.SRP_SHA: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.NONE, key_auth=tls.KeyAuthentication.NONE
    ),
    tls.KeyExchangeAlgorithm.SRP_SHA_DSS: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.NONE, key_auth=tls.KeyAuthentication.DSS
    ),
    tls.KeyExchangeAlgorithm.SRP_SHA_RSA: structs.KeyExchange(
        key_ex_type=tls.KeyExchangeType.NONE, key_auth=tls.KeyAuthentication.RSA
    ),
}

curve_to_group: Dict[str, tls.SupportedGroups] = {
    "brainpoolP256r1": tls.SupportedGroups.BRAINPOOLP256R1,
    "brainpoolP384r1": tls.SupportedGroups.BRAINPOOLP384R1,
    "brainpoolP512r1": tls.SupportedGroups.BRAINPOOLP512R1,
    "secp192r1": tls.SupportedGroups.SECP192R1,
    "secp224r1": tls.SupportedGroups.SECP224R1,
    "secp256k1": tls.SupportedGroups.SECP256K1,
    "secp256r1": tls.SupportedGroups.SECP256R1,
    "secp384r1": tls.SupportedGroups.SECP384R1,
    "secp521r1": tls.SupportedGroups.SECP521R1,
    "sect163k1": tls.SupportedGroups.SECT163K1,
    "sect163r2": tls.SupportedGroups.SECT163R2,
    "sect233k1": tls.SupportedGroups.SECT233K1,
    "sect233r1": tls.SupportedGroups.SECT233R1,
    "sect283k1": tls.SupportedGroups.SECT283K1,
    "sect283r1": tls.SupportedGroups.SECT283R1,
    "sect409k1": tls.SupportedGroups.SECT409K1,
    "sect409r1": tls.SupportedGroups.SECT409R1,
    "sect571k1": tls.SupportedGroups.SECT571K1,
    "sect571r1": tls.SupportedGroups.SECT571R1,
}

issue_to_alert_description: Dict[tls.ServerIssue, tls.AlertDescription] = {
    tls.ServerIssue.PSK_OUT_OF_RANGE: tls.AlertDescription.ILLEGAL_PARAMETER,
    tls.ServerIssue.KEY_SHARE_NOT_PRESENT: tls.AlertDescription.HANDSHAKE_FAILURE,
    tls.ServerIssue.SECURE_RENEG_FAILED: tls.AlertDescription.ILLEGAL_PARAMETER,
    tls.ServerIssue.VERIFY_DATA_INVALID: tls.AlertDescription.ILLEGAL_PARAMETER,
    tls.ServerIssue.CERT_REQ_NO_SIG_ALGO: tls.AlertDescription.MISSING_EXTENSION,
    tls.ServerIssue.EXTENTION_LENGHT_ERROR: tls.AlertDescription.DECODE_ERROR,
    tls.ServerIssue.SNI_NO_HOSTNAME: tls.AlertDescription.HANDSHAKE_FAILURE,
    tls.ServerIssue.FFDH_GROUP_UNKNOWN: tls.AlertDescription.ILLEGAL_PARAMETER,
    tls.ServerIssue.MESSAGE_LENGTH_ERROR: tls.AlertDescription.DECODE_ERROR,
    tls.ServerIssue.INCOMPATIBLE_KEY_EXCHANGE: tls.AlertDescription.HANDSHAKE_FAILURE,
    tls.ServerIssue.PARAMETER_LENGTH_ERROR: tls.AlertDescription.DECODE_ERROR,
    tls.ServerIssue.RECORD_TOO_SHORT: tls.AlertDescription.BAD_RECORD_MAC,
    tls.ServerIssue.RECORD_MAC_INVALID: tls.AlertDescription.BAD_RECORD_MAC,
    tls.ServerIssue.RECORD_WRONG_PADDING_LENGTH: tls.AlertDescription.BAD_RECORD_MAC,
    tls.ServerIssue.RECORD_WRONG_PADDING_BYTES: tls.AlertDescription.BAD_RECORD_MAC,
    tls.ServerIssue.ILLEGAL_PARAMETER_VALUE: tls.AlertDescription.ILLEGAL_PARAMETER,
}
