import pgpy
import os
from datetime import timedelta
from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm


class Key:
    """PGP Key as described in RFC 4880"""

    def __init__(self, path_demo_dir=None, filename=None, key_str=None, size=512):
        """This function intializes a PGP key. There are several possibilities to do it: You can specify a path or a key in string format to load an existing key. If neither a path nor a key string is given, a new key is generated.

        :param path_demo_dir: Path to the ASC file (default: None)
        :type path_demo_dir: str
        :param filename: name os the ASC file storing the PGP key
        :type filename: str
        :param key_str: PGP key in string format (default: None)
        :type key_str: str
        :param size: size of the key if an new key is generated (default: 512)
        :type size: int
        """
        if isinstance(path_demo_dir, str):
            self.loadFromFile(path_demo_dir, filename)
        elif isinstance(key_str, str):
            key_list = pgpy.PGPKey.from_blob(
                key_str.replace("\\n", "\n").strip('"'))
            self.key = key_list[0]
        else:
            self.key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, size)

    def generateKey(self, userID, comment="", email=""):
        """This function generates a new PGP key.

        :param userID: User ID name, or photo. If this is a bytearray, it will be loaded as a photo. Otherwise, it will be used as the name field for a User ID.
        :type pn: bytearray, str, unicode  
        :param comment: The comment field for a User ID. Ignored if this is a photo.
        :type comment: str, unicode
        :param email: The email address field for a User ID. Ignored if this is a photo.
        :type email: str, unicode
        :return: PGP key 
        :rtype: pgpy.PGPKey
        """
        self.uid = pgpy.PGPUID.new(userID, comment, email)
        self.key.add_uid(self.uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
                         hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384,
                                 HashAlgorithm.SHA512, HashAlgorithm.SHA224],
                         ciphers=[SymmetricKeyAlgorithm.AES256,
                                  SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
                         compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP, CompressionAlgorithm.Uncompressed])
        return self.key

    def addKeyExpiration(self, expDays):
        """This function specifies the amount of days the key should be valid.

        :param expDays: Amount of days after which the key should expire.
        :type expDays: int
        """
        self.key.add_uid(self.uid, key_expires=timedelta(days=expDays))

    def exportsecKeyToFile(self, filename="secKey.asc", path = None):
        """This function exports the key to an ASC file in the key folder with the given filename.

        :param filename: filename of the output file
        :type filename: str
        """
        if not path:
            save_path = 'key'
            fp = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(fp, "..", save_path, filename)
        else:
            path = os.path.join(path,filename)
        f = open(path, "w")
        keystr = str(self.key)
        f.write(keystr)
        f.close()

    def exportPubKeyToFile(self, filename="pubKey.asc", path = None):
        """This function exports the key to an ASC file in the key folder with the given filename.

        :param filename: filename of the output file
        :type filename: str
        """
        if not path:
            save_path = 'key'
            fp = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(fp, "..", save_path, filename)
        else:
            path = os.path.join(path,filename)
        f = open(path, "w")
        keystr = str(self.key.pubkey)
        f.write(keystr)
        f.close()

    def loadFromFile(self, path_demo_dir, filename):
        """This function loads a PGP key that is given as an ASC file from a subdirectory.

        :param path_demo_dir: Path to the ASC file (default: None)
        :type path_demo_dir: str
        :param filename: name os the ASC file storing the PGP key
        :type filename: str
        """

        path = os.path.join(path_demo_dir, filename)
        self.key, _ = pgpy.PGPKey.from_file(path)
