"""
:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import hashlib
import domipy

ENCODING = "utf-8"

class LoginRequest(domipy.Command): 
    """
        send: LOGIN<password_hash>
    """
    def __init__(self, username, password, salt, nonce):
        domipy.Command.__init__(self, "_LOGIN_", "_LOGIN_")
        self._password = password
        self._username = username
        self._salt = salt
        self._nonce = nonce

    def command(self):
        salted_pass = self._password+self._salt
        m = hashlib.sha512()
        m.update(bytes(salted_pass, ENCODING))
        hash = m.hexdigest()
        m2 = hashlib.sha512()
        m2.update(bytes(hash+self._nonce,ENCODING))

        return "LOGINPSW@{}:{}".format(self._username, m2.hexdigest())
        
    def is_binary(self):
        return True


