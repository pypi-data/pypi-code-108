# -*- coding: utf-8 -*-
"""Module containing the class implementing the record layer
"""
# import basic stuff
import struct
from typing import Any

# import own stuff
import tlsmate.pdu as pdu
import tlsmate.structs as structs
import tlsmate.tls as tls

# import other stuff
from cryptography.hazmat.primitives import hmac, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, modes, aead


class RecordLayerState(object):
    """Class to represent a dynamic record layer state

    Attributes:
        param (:obj:`tlsmate.structs.StateUpdateParams`): the structure to initialize
            the record layer state.
    """

    def __init__(self, param: structs.StateUpdateParams) -> None:

        self._keys = param.keys
        self._mac = param.mac
        self._cipher = param.cipher
        self._compr = param.compr
        self._enc_then_mac = param.enc_then_mac
        self._version = param.version
        self._seq_nbr = 0
        self._cipher_object = None
        self._iv = param.keys.iv
        if self._cipher.c_type == tls.CipherType.STREAM:
            cipher = Cipher(
                self._cipher.algo(self._keys.enc), mode=None  # type: ignore
            )
            if param.is_write_state:
                self._cipher_object = cipher.encryptor()

            else:
                self._cipher_object = cipher.decryptor()

        if self._version is tls.Version.TLS13:
            self._cipher_object = param.cipher.algo

    def _encrypt_cbc(self, fragment, padding_cb=None, **kwargs):
        """Encrypt a fragment using a block cipher in CBC mode.

        Arguments:
            fragment (bytes): The fragment to encrypt.

        Returns:
            bytes: The encrypted fragment.
        """

        # padding
        length = len(fragment) + 1
        missing_bytes = self._cipher.block_size - (length % self._cipher.block_size)
        padding = struct.pack("!B", missing_bytes) * (missing_bytes + 1)

        if padding_cb:
            padding = padding_cb(bytearray(padding))

        fragment += padding

        if self._version <= tls.Version.TLS10:
            iv = self._iv

        else:
            # iv should be random but we want to have it reproducable
            iv = self._iv[:-4] + pdu.pack_uint32(self._seq_nbr)

        cipher = Cipher(self._cipher.algo(self._keys.enc), modes.CBC(iv))
        encryptor = cipher.encryptor()
        cipher_block = encryptor.update(fragment) + encryptor.finalize()
        if self._version <= tls.Version.TLS10:
            self._iv = cipher_block[-self._cipher.iv_len :]
            return cipher_block

        else:
            return iv + cipher_block

    def _append_mac(self, content_type, version, fragment, mac_cb=None, **kwargs):
        """Calculates the MAC and appends it to the fragment.

        Arguments:
            content_type (:obj:`tlsmate.constants.ContentType`): The content type.
            version (:obj:`tlsmate.constants.Version`): The version of the
                record layer.
            fragment: The message for which the MAC is calculated.

        Returns:
            bytes: The fragment appended with the MAC.
        """

        # TODO: move mac calculation to kdf object

        if version is tls.Version.SSL30:
            pad_len = 40 if self._mac.hash_algo.name == "sha1" else 48
            mac = hashes.Hash(self._mac.hash_algo())
            mac.update(
                self._keys.mac
                + b"\x36" * pad_len
                + pdu.pack_uint64(self._seq_nbr)
                + pdu.pack_uint8(content_type.value)
                + pdu.pack_uint16(len(fragment))
                + fragment
            )
            mac2 = hashes.Hash(self._mac.hash_algo())
            mac2.update(self._keys.mac + b"\x5c" * pad_len + mac.finalize())
            mac_bytes = mac2.finalize()

        else:
            mac_input = (
                pdu.pack_uint64(self._seq_nbr)
                + pdu.pack_uint8(content_type.value)
                + pdu.pack_uint16(version.value)
                + pdu.pack_uint16(len(fragment))
                + fragment
            )
            mac = hmac.HMAC(self._keys.mac, self._mac.hash_algo())
            mac.update(mac_input)
            mac_bytes = mac.finalize()

        if mac_cb:
            mac_bytes = mac_cb(bytearray(mac_bytes))

        return fragment + mac_bytes

    def _protect_block_cipher(self, rl_msg, data_cb=None, **kwargs):
        """Protects a fragment using a block cipher.

        The fragment is encrypted and authenticated with a MAC. Both modes,
        encrypt_then_mac and mac_then_encrypt are supported.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to protect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The protected record layer message.
        """

        fragment = rl_msg.fragment
        if data_cb:
            fragment = data_cb(bytearray(fragment))

        if self._enc_then_mac:
            fragment = self._encrypt_cbc(fragment, **kwargs)
            fragment = self._append_mac(
                rl_msg.content_type, rl_msg.version, fragment, **kwargs
            )

        else:
            fragment = self._append_mac(
                rl_msg.content_type, rl_msg.version, fragment, **kwargs
            )
            fragment = self._encrypt_cbc(fragment, **kwargs)

        self._seq_nbr += 1
        return structs.RecordLayerMsg(
            content_type=rl_msg.content_type, version=rl_msg.version, fragment=fragment
        )

    def _protect_stream_cipher(self, rl_msg):
        """Protects a fragment using a stream cipher.

        The fragment is authenticated with a MAC and then encrypted.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to protect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The protected record layer message.
        """

        fragment = self._append_mac(
            rl_msg.content_type, rl_msg.version, rl_msg.fragment
        )
        self._seq_nbr += 1
        return structs.RecordLayerMsg(
            content_type=rl_msg.content_type,
            version=rl_msg.version,
            fragment=self._cipher_object.update(fragment),
        )

    def _protect_chacha_cipher(self, rl_msg):
        """Protects a fragment using the CHACHA20_POLY1305 cipher.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to protect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The protected record layer message.
        """

        nonce_val = int.from_bytes(self._keys.iv, "big", signed=False) ^ self._seq_nbr
        nonce = nonce_val.to_bytes(self._cipher.iv_len, "big", signed=False)
        aad = (
            pdu.pack_uint64(self._seq_nbr)
            + pdu.pack_uint8(rl_msg.content_type.value)
            + pdu.pack_uint16(rl_msg.version.value)
            + pdu.pack_uint16(len(rl_msg.fragment))
        )
        chachapoly = aead.ChaCha20Poly1305(self._keys.enc)
        self._seq_nbr += 1
        return structs.RecordLayerMsg(
            content_type=rl_msg.content_type,
            version=rl_msg.version,
            fragment=chachapoly.encrypt(nonce, rl_msg.fragment, aad),
        )

    def _protect_aead_cipher(self, rl_msg):
        """Protects a fragment using an AEAD cipher.

        This supports AES_GCM (128&256) as well as AES_CCM and AES_CCM_8.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to protect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The protected record layer message.
        """

        kwargs = {}
        if self._cipher.tag_length != 16:
            kwargs["tag_length"] = self._cipher.tag_length

        aes_aead = self._cipher.algo(self._keys.enc, **kwargs)
        nonce_explicit = pdu.pack_uint64(self._seq_nbr)
        nonce = self._keys.iv + nonce_explicit
        aad = (
            pdu.pack_uint64(self._seq_nbr)
            + pdu.pack_uint8(rl_msg.content_type.value)
            + pdu.pack_uint16(rl_msg.version.value)
            + pdu.pack_uint16(len(rl_msg.fragment))
        )
        self._seq_nbr += 1
        return structs.RecordLayerMsg(
            content_type=rl_msg.content_type,
            version=rl_msg.version,
            fragment=nonce_explicit + aes_aead.encrypt(nonce, rl_msg.fragment, aad),
        )

    def _protect(self, rl_msg, **kwargs):
        """Protects a fragment.

        Supports stream ciphers, block cipher, AEAD ciphers and POLY20_CHACHA1305.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to protect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The protected record layer message.

        Raises:
            ValueError: if the cipher type is unknown.
        """

        if self._cipher.c_type == tls.CipherType.BLOCK:
            return self._protect_block_cipher(rl_msg, **kwargs)

        elif self._cipher.c_type == tls.CipherType.STREAM:
            return self._protect_stream_cipher(rl_msg)

        elif self._cipher.c_type == tls.CipherType.AEAD:
            if self._cipher.primitive == tls.CipherPrimitive.CHACHA:
                return self._protect_chacha_cipher(rl_msg)

            else:
                return self._protect_aead_cipher(rl_msg)

        else:
            raise ValueError("Unknown cipher type")

    def _tls13_protect(self, rl_msg):
        """Protects a fragment using the TLS1.3 specification.

        All TLS1.3 ciphers are supported.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to protect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The protected record layer message.
        """

        fragment = bytes(rl_msg.fragment) + pdu.pack_uint8(rl_msg.content_type.value)
        aad = (
            pdu.pack_uint8(tls.ContentType.APPLICATION_DATA.value)
            + pdu.pack_uint16(rl_msg.version.value)
            + pdu.pack_uint16(len(fragment) + self._cipher.tag_length)
        )
        nonce_val = int.from_bytes(self._keys.iv, "big", signed=False) ^ self._seq_nbr
        nonce = nonce_val.to_bytes(self._cipher.iv_len, "big", signed=False)
        kwargs = {}
        if self._cipher.tag_length == 8:
            kwargs["tag_length"] = 8

        cipher = self._cipher_object(self._keys.enc, **kwargs)
        self._seq_nbr += 1
        return structs.RecordLayerMsg(
            content_type=tls.ContentType.APPLICATION_DATA,
            version=rl_msg.version,
            fragment=cipher.encrypt(nonce, fragment, aad),
        )

    def protect_msg(
        self, rl_msg: structs.RecordLayerMsg, **kwargs: Any
    ) -> structs.RecordLayerMsg:
        """Protects a fragment.

        Arguments:
            rl_msg: The record layer message to protect.
            kwargs: additional parameters which can be used to control CBC
                padding oracle related behavior

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The protected record layer message.
        """

        if self._version is tls.Version.TLS13:
            return self._tls13_protect(rl_msg)

        else:
            # Skip compression, we don't want to support it.
            return self._protect(rl_msg, **kwargs)

    def _verify_mac(self, content_type, version, fragment, mac_cb=None, **kwargs):
        """Verifies the MAC of a fragment.

        Arguments:
            content_type (:obj:`tlsmate.constants.ContentType`): The content type.
            version (:obj:`tlsmate.constants.Version`): The version of the
                record layer.
            fragment: The message for which the MAC is verified.

        Returns:
            bytes: The fragment appended with the MAC.

        Raises:
            :obj:`tlsmate.tls.ServerMalfunction`: If the MAC is incorrect.
        """

        if len(fragment) < self._mac.mac_len:
            raise tls.ServerMalfunction(tls.ServerIssue.RECORD_TOO_SHORT)

        msg_len = len(fragment) - self._mac.mac_len
        mac_received = fragment[msg_len:]
        if mac_cb:
            mac_received = mac_cb(bytearray(mac_received))

        msg = fragment[:msg_len]

        if version is tls.Version.SSL30:
            pad_len = 40 if self._mac.hash_algo.name == "sha1" else 48
            mac = hashes.Hash(self._mac.hash_algo())
            mac.update(
                self._keys.mac
                + b"\x36" * pad_len
                + pdu.pack_uint64(self._seq_nbr)
                + pdu.pack_uint8(content_type.value)
                + pdu.pack_uint16(msg_len)
                + msg
            )
            mac2 = hashes.Hash(self._mac.hash_algo())
            mac2.update(self._keys.mac + b"\x5c" * pad_len + mac.finalize())
            mac_calculated = mac2.finalize()

        else:
            mac_input = (
                pdu.pack_uint64(self._seq_nbr)
                + pdu.pack_uint8(content_type.value)
                + pdu.pack_uint16(version.value)
                + pdu.pack_uint16(msg_len)
                + msg
            )
            mac = hmac.HMAC(self._keys.mac, self._mac.hash_algo())
            mac.update(mac_input)
            mac_calculated = mac.finalize()

        if mac_calculated != mac_received:
            raise tls.ServerMalfunction(tls.ServerIssue.RECORD_MAC_INVALID)

        return msg

    def _decode_cbc(self, fragment, padding_cb=None, **kwargs):
        """Decodes a fragment using a block cipher in CBC mode.

        Arguments:
            fragment (bytes): The fragment to decode.

        Returns:
            bytes: the decoded fragment.

        Raises:
            :obj:`tlsmate.tls.ServerMalfunction`: If padding errors are detected.
        """

        if self._version <= tls.Version.TLS10:
            iv = self._iv
            cipher_text = fragment
            self._iv = fragment[-self._cipher.iv_len :]

        else:
            iv = fragment[: self._cipher.iv_len]
            cipher_text = fragment[self._cipher.iv_len :]

        cipher = Cipher(self._cipher.algo(self._keys.enc), modes.CBC(iv))
        decryptor = cipher.decryptor()
        plain_text = decryptor.update(cipher_text) + decryptor.finalize()

        # padding
        pad = plain_text[-1]
        pad_start = len(plain_text) - pad - 1
        if pad_start < 0:
            raise tls.ServerMalfunction(tls.ServerIssue.RECORD_WRONG_PADDING_LENGTH)

        padding = plain_text[pad_start:]
        if padding_cb:
            padding = padding_cb(bytearray(padding))

        plain_text = plain_text[:pad_start]

        if self._version is not tls.Version.SSL30:
            if (struct.pack("!B", pad) * (pad + 1)) != padding:
                raise tls.ServerMalfunction(tls.ServerIssue.RECORD_WRONG_PADDING_BYTES)

        return plain_text

    def _unprotect_block_cipher(self, rl_msg, data_cb=None, **kwargs):
        """Unprotects a record layer message (block cipher).

        The message is decrypted and the authentication is verified. Both modes,
        encrypt_then_mac and mac_then_encrypt are supported.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to unprotect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The unprotected record layer message (plain text).
        """

        if self._enc_then_mac:
            fragment = self._verify_mac(
                rl_msg.content_type, rl_msg.version, rl_msg.fragment, **kwargs,
            )
            plain_text = self._decode_cbc(fragment, **kwargs)

        else:
            fragment = self._decode_cbc(rl_msg.fragment, **kwargs)
            plain_text = self._verify_mac(
                rl_msg.content_type, rl_msg.version, fragment, **kwargs
            )

        if data_cb:
            plain_text = data_cb(bytearray(plain_text))

        self._seq_nbr += 1
        return structs.RecordLayerMsg(
            content_type=rl_msg.content_type,
            version=rl_msg.version,
            fragment=plain_text,
        )

    def _unprotect_stream_cipher(self, rl_msg, **kwargs):
        """Unprotects a record layer message (stream cipher).

        The message is decrypted and the authentication is verified.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to unprotect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The unprotected record layer message (plain text).
        """

        fragment = self._cipher_object.update(rl_msg.fragment)
        clear_text = self._verify_mac(
            rl_msg.content_type, rl_msg.version, fragment, **kwargs
        )
        self._seq_nbr += 1
        return structs.RecordLayerMsg(
            content_type=rl_msg.content_type,
            version=rl_msg.version,
            fragment=clear_text,
        )

    def _unprotect_chacha_cipher(self, rl_msg):
        """Unprotects a record layer message (CHACHA20_POLY1305 cipher).

        The message is decrypted and the authentication is verified.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to unprotect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The unprotected record layer message (plain text).
        """

        nonce_val = int.from_bytes(self._keys.iv, "big", signed=False) ^ self._seq_nbr
        nonce = nonce_val.to_bytes(self._cipher.iv_len, "big", signed=False)
        aad = (
            pdu.pack_uint64(self._seq_nbr)
            + pdu.pack_uint8(rl_msg.content_type.value)
            + pdu.pack_uint16(rl_msg.version.value)
            + pdu.pack_uint16(len(rl_msg.fragment) - self._cipher.tag_length)
        )
        chachapoly = aead.ChaCha20Poly1305(self._keys.enc)
        self._seq_nbr += 1
        return structs.RecordLayerMsg(
            content_type=rl_msg.content_type,
            version=rl_msg.version,
            fragment=chachapoly.decrypt(nonce, rl_msg.fragment, aad),
        )

    def _unprotect_aead_cipher(self, rl_msg):
        """Unprotects a record layer message (AEAD cipher).

        The message is decrypted and the authentication is verified.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to unprotect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The unprotected record layer message (plain text).
        """

        nonce_explicit = rl_msg.fragment[:8]
        cipher_text = rl_msg.fragment[8:]
        aad = (
            pdu.pack_uint64(self._seq_nbr)
            + pdu.pack_uint8(rl_msg.content_type.value)
            + pdu.pack_uint16(rl_msg.version.value)
            + pdu.pack_uint16(len(cipher_text) - self._cipher.tag_length)
        )
        nonce = bytes(self._keys.iv + nonce_explicit)
        kwargs = {}
        if self._cipher.tag_length != 16:
            kwargs["tag_length"] = self._cipher.tag_length

        aes_aead = self._cipher.algo(self._keys.enc, **kwargs)
        self._seq_nbr += 1
        return structs.RecordLayerMsg(
            content_type=rl_msg.content_type,
            version=rl_msg.version,
            fragment=aes_aead.decrypt(nonce, cipher_text, aad),
        )

    def _unprotect(self, rl_msg, **kwargs):
        """Unprotects a record layer message (all ciphers, but not for TLS1.3).

        The message is decrypted and the authentication is verified.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to unprotect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The unprotected record layer message (plain text).
        """

        if self._cipher.c_type == tls.CipherType.BLOCK:
            return self._unprotect_block_cipher(rl_msg, **kwargs)

        elif self._cipher.c_type == tls.CipherType.STREAM:
            return self._unprotect_stream_cipher(rl_msg, **kwargs)

        elif self._cipher.c_type == tls.CipherType.AEAD:
            if self._cipher.primitive == tls.CipherPrimitive.CHACHA:
                return self._unprotect_chacha_cipher(rl_msg)

            else:
                return self._unprotect_aead_cipher(rl_msg)

        else:
            raise ValueError("Unknown cipher type")

    def _tls13_unprotect(self, rl_msg):
        """Unprotects a record layer message (TLS1.3).

        The message is decrypted and the authentication is verified.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to unprotect.

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The unprotected record layer message (plain text).

        Raises:
            :obj:`tlsmate.tls.ServerMalfunction`: If padding errors are detected.
        """

        aad = (
            pdu.pack_uint8(rl_msg.content_type.value)
            + pdu.pack_uint16(rl_msg.version.value)
            + pdu.pack_uint16(len(rl_msg.fragment))
        )
        nonce_val = int.from_bytes(self._keys.iv, "big", signed=False) ^ self._seq_nbr
        nonce = nonce_val.to_bytes(self._cipher.iv_len, "big", signed=False)
        kwargs = {}
        if self._cipher.tag_length == 8:
            kwargs["tag_length"] = 8

        cipher = self._cipher_object(self._keys.enc, **kwargs)
        decoded = cipher.decrypt(nonce, rl_msg.fragment, aad)
        # find idx of last non-zero octet
        idx = len(decoded) - 1
        while idx >= 0:
            if decoded[idx] != 0:
                break

            idx -= 1

        if idx < 0:
            raise tls.ServerMalfunction(tls.ServerIssue.RECORD_WRONG_PADDING_LENGTH)

        self._seq_nbr += 1
        return structs.RecordLayerMsg(
            content_type=tls.ContentType.val2enum(decoded[idx], alert_on_failure=True),
            version=rl_msg.version,
            fragment=decoded[:idx],
        )

    def unprotect_msg(
        self, rl_msg: structs.RecordLayerMsg, **kwargs
    ) -> structs.RecordLayerMsg:
        """Unprotects a record layer message.

        The message is decrypted and the authentication is verified.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The record layer
                message to unprotect.

            kwargs (dict): additional parameters which can be used to control CBC
                padding oracle related behavior

        Returns:
            :obj:`tlsmate.structs.RecordLayerMsg`:
            The unprotected record layer message (plain text).
        """

        if self._version is tls.Version.TLS13:
            if rl_msg.content_type is tls.ContentType.CHANGE_CIPHER_SPEC:
                return rl_msg

            return self._tls13_unprotect(rl_msg)

        else:
            # We do not support compression.
            return self._unprotect(rl_msg, **kwargs)
