#   Copyright (c) 2021, Zenqi

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#: https://stackoverflow.com/questions/42568262

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

from sidle.utils import (
    convert_bytes,
    convert_string
)

from typing import (
    Any
)
from sidle.errors import PasswordError

class SidleEncryption:
    """
    Simple Encrypting and Decrypting strings
    with password
    
    Parameter:
        password (Any):
            The password that can be used for both
            encryption and decryption
    """

    def __init__(self, password: Any):
        """
        Initialize SidleEncryption
        """
        self.password = convert_bytes(password)

    def encrypt(self, string: str):
        """
        Encrypt the given string and return
        encrypted bytes that can be decrypted with the
        given password.
        """

        if string == " " or string == "":
            raise ValueError('cannot be null')

        string = convert_bytes(string)
        
        key = self.__password_to_key(self.password)
        IV = self.make_initialization_vector()
        encryptor = AES.new(key, AES.MODE_CBC, IV)

        # store the IV at the beginning and encrypt
        return IV + encryptor.encrypt(self.pad_string(string))

    def decrypt(self, encrypted_string: bytes):
        """
        Decrypt the given encrypted string
        """

        key = self.__password_to_key(self.password)
        
        # extract the IV from the beginning
        IV = encrypted_string[:AES.block_size]  
        decryptor = AES.new(key, AES.MODE_CBC, IV)

        _str = decryptor.decrypt(encrypted_string[AES.block_size:])
        
        try:
            string = convert_string(
                self.unpad_string(_str)
            )
            
        except Exception:
            string = self.unpad_string(_str)
        
        if string == "":
            raise PasswordError

        return string


    def make_initialization_vector(self):
        """
        An initialization vector (IV) is a fixed-size input to a cryptographic
        primitive that is typically required to be random or pseudorandom.
        Randomization is crucial for encryption schemes to achieve semantic 
        security, a property whereby repeated usage of the scheme under the 
        same key does not allow an attacker to infer relationships 
        between segments of the encrypted message.
        """
        return Random.new().read(AES.block_size)
    
    
    def unpad_string(self, string: str):
        """
        Unpad the given string
        """

        to_pad = string[0]
        if to_pad == 0:
            return string
        
        return string[1:-to_pad]

    def pad_string(self, string, chunk_size=AES.block_size):
        """
        Pad string the peculirarity that uses the first byte
        is used to store how much padding is applied
        """
        assert chunk_size  <= 256, 'We are using one byte to represent padding'
        to_pad = (chunk_size - (len(string) + 1)) % chunk_size
        return bytes([to_pad]) + string + bytes([0] * to_pad)

    def __password_to_key(self, password: Any):
        """
        Use SHA-256 over the password to get a proper-sized AES key.
        This hashes the password into a 256 bit string. 
        """

        return SHA256.new(password).digest()
        
