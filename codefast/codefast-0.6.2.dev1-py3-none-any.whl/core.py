from cryptography.fernet import Fernet

class Privacy:
    """ Universal Encrypt/Decrypt APIs
    """
    def fernet_encrypt(self, fernet_key:str, b_content:bytes)->bytes:
        """ A ferner encrypt wrapper
        Args: 
            fernet_key: str, fernet key
            b_content: bytes, binary content to be encrypted
        """
        fernet_client=Fernet(fernet_key)
        return fernet_client.encrypt(b_content)
    
    def fernet_decrypt(self, fernet_key:str, b_content:bytes)->bytes:
        fernet_client=Fernet(fernet_key)
        return fernet_client.decrypt(b_content)

    