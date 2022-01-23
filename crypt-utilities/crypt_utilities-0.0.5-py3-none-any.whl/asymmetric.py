
from typing import Union
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives import serialization, hashes

# --------------------------------- Asymmetric Encryption ----------------------------------
# ------------------------------------------------------------------------------------------
def generate_private_key(size:int=2048) -> RSAPrivateKey:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=size
    )
    return private_key

def extract_public_key(private_key:RSAPrivateKey) -> RSAPublicKey:
    return private_key.public_key()

def serialize_pem_private_key(private_key:RSAPrivateKey, password:bytes=None,
                                    file_path:Union[str, Path]=None) -> bytes:
    enc_alg = serialization.NoEncryption()
    if password is not None:
        enc_alg = serialization.BestAvailableEncryption(password)
        
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc_alg
    )
    
    if file_path is not None:
        with open(file_path, 'wb') as file:
            file.write(pem)
    
    return pem
    
def serialize_pem_public_key(public_key:RSAPublicKey, file_path:Union[str, Path]=None) -> bytes:
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    if file_path is not None:
        with open(file_path, 'wb') as file:
            file.write(pem)
        
    return pem

def load_pem_private_key(private_key_path:Union[str, Path], password:bytes=None) -> RSAPrivateKey:
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=password,
        )
    return private_key
    
def load_pem_public_key(public_key_path:Union[str, Path]) -> RSAPublicKey:
    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read()
        )
    return public_key

def rsa_encrypt(message:bytes, public_key:RSAPublicKey) -> bytes:
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext
    
def rsa_decrypt(ciphertext:bytes, private_key:RSAPrivateKey) -> bytes:
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext

def generate_rsa_key_pairs(private_key_password:str=None, file_path:Union[str, Path]='./', quiet:bool=True):
    """Generates RSA Key pairs. The function checks if the generated keys are valid, just in case 
    something went wrong

    Args:
        private_key_password (str, optional): [description]. Defaults to None. Optional password to use
            when serializing the private key.
        file_path (Union[str, Path], optional): [description]. Defaults to './'.
        quiet (bool, optional): [description]. Defaults to True.
    """
    def log(*msg):
        if not quiet:
            print(*msg)
    
    if type(file_path) != Path:
        file_path = Path(file_path).resolve() 
    password = None
    if private_key_password is not None:
        password = private_key_password.encode()
    # Generate and safe keys in a file
    private_key_path = file_path/'private_key'
    public_key_path = file_path/'public_key'
    private_key = generate_private_key()
    public_key = extract_public_key(private_key)
    # Checking the keys are valid (just in case)
    msg = b'Hey there!'
    ciphertext = rsa_encrypt(msg, public_key)
    deciphered_text = rsa_decrypt(ciphertext, private_key)
    if msg != deciphered_text: 
        log("[!] Keys are invalid")
        raise Exception("Keys are not valid")
    else:
        log(" + The keys are valid")
        log(f"     => Decrypted message = '{deciphered_text.decode()}'")
    # Checking keys saved in the files are valid (again, just in case)
    serialize_pem_private_key(private_key, file_path=private_key_path, password=password)
    serialize_pem_public_key(public_key, file_path=public_key_path)
    private_key_recovered = load_pem_private_key(private_key_path, password=password)
    public_key_recovered = load_pem_public_key(public_key_path)
    msg = b'Hey There 2!'
    ciphertext = rsa_encrypt(msg, public_key_recovered)
    deciphered_text = rsa_decrypt(ciphertext, private_key_recovered)
    if msg != deciphered_text: 
        log("[!] Recovered keys are not valid")
        raise Exception("Recovered Keys are not valid")
    else:
        log(" + Recovered keys are valid")
        log(f"     => Decrypted message = '{deciphered_text.decode()}'")

# Creating RSA key pairs with extra password security and checking they are valid 
if __name__ == "__main__":
    pem_private_password = 'example'; path = './src/'
    generate_rsa_key_pairs(private_key_password=pem_private_password, file_path=path)