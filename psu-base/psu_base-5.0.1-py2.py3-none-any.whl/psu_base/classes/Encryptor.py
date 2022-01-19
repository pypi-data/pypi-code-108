from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from psu_base.classes.Log import Log
import os
import hashlib

log = Log()


# Class for encrypting and decrypting string values using the PSU Base plugin's secret key
class Encryptor:
    psu_base_key_path = None

    def encrypt(self, content):
        if not self.has_psu_key():
            log.error("No PSU Base plugin key available to encrypt values.")
            return None

        encrypted_value = None
        try:
            # Use PSU Base plugin key to encrypt the data
            if self.psu_base_key_path and os.path.exists(self.psu_base_key_path):
                with open(self.psu_base_key_path, "rb") as ff:
                    key = RSA.importKey(ff.read())
                    cipher = PKCS1_OAEP.new(key)
                    encrypted_value = cipher.encrypt(str.encode(content))
            else:
                log.error("Unable to locate PSU Base plugin key.")

        except Exception as ee:
            log.error("Unable to encrypt value.")

        # Overwrite the content variable and delete it
        content = "                "
        del content

        return encrypted_value

    def decrypt(self, encrypted_bytes):
        if not self.has_psu_key():
            log.warning("No PSU Base plugin key available to decrypt values.")
            return None

        decrypted_value = None
        try:
            # Use PSU Base plugin key to decrypt the data
            if self.psu_base_key_path and os.path.exists(self.psu_base_key_path):
                with open(self.psu_base_key_path, "rb") as ff:
                    key = RSA.importKey(ff.read())
                    cipher = PKCS1_OAEP.new(key)
                    decrypted_value = cipher.decrypt(encrypted_bytes).decode("utf-8")
                    del key
                    del cipher
            else:
                log.error("Unable to locate PSU Base plugin key.")

        except Exception as ee:
            log.error("Unable to decrypt value.")

        return decrypted_value

    def encrypt_to_file(self, content, file_path):
        """Encrypt the given data and save it in a specified (binary) file"""
        if not self.has_psu_key():
            log.error("No PSU Base plugin key available to encrypt values.")
            return None

        # Encrypt the content
        encrypted_bytes = self.encrypt(content)

        # Overwrite the content variable and delete it
        content = "                "
        del content

        try:
            # Write encrypted data to file
            if encrypted_bytes:
                with open(file_path, "wb") as ff:
                    ff.write(encrypted_bytes)
                del encrypted_bytes
        except Exception as ee:
            log.error("Unable to write encrypted value to file.")

    def decrypt_from_file(self, file_path):
        """Decrypt the data in a specified (binary) file"""
        if not self.has_psu_key():
            log.error("No PSU Base plugin key available to encrypt values.")
            return None

        try:
            # Read encrypted data from file
            if os.path.isfile(file_path):
                with open(file_path, "rb") as ff:
                    return self.decrypt(ff.read())
        except Exception as ee:
            log.error("Unable to read encrypted value from file.")

    def locate_key_path(self):
        root_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        # A key in the project root takes priority
        priority_path = os.path.join(root_dir, ".psu_base.key")
        # A key in the user's home directory applies to all projects
        generic_path = os.path.join(os.path.expanduser("~"), ".psu_base.key")

        # Determine which key to use
        if os.path.exists(priority_path):
            self.psu_base_key_path = priority_path
        elif os.path.exists(generic_path):
            self.psu_base_key_path = generic_path
        else:
            log.debug(
                "Unable to locate PSU Base plugin key.  Development encryption functions not available."
            )

        # Cleanup
        del priority_path
        del generic_path

    def has_psu_key(self):
        return True if self.psu_base_key_path else False

    # Initialize an Encryptor object
    def __init__(self, given_key_path=None):
        """Create an Encryptor object"""
        if given_key_path:
            self.psu_base_key_path = given_key_path
        else:
            self.locate_key_path()


# Not encryption, but somewhat related.  Get a simple hash of a string
def getHash(source):
    hl = hashlib.new("ripemd160")
    hl.update(str.encode(source))
    return hl.hexdigest()
