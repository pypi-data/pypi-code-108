"""Basic methods"""
import secrets
import hashlib

def k1bytes():
    token = secrets.token_hex(512)

    return token

def m1bytes():
    token = secrets.token_hex(512*1024)
    return token

def g1bytes():
    token = secrets.token_hex(512*1024*1024)
    return token 

def rsha512():
    token = hashlib.sha512(secrets.token_hex(8).encode()).hexdigest()
    return token 

def rsha256():
    token = hashlib.sha256(secrets.token_hex(8).encode()).hexdigest()
    return token 

def rsha1():
    token = hashlib.sha1(secrets.token_hex(8).encode()).hexdigest()
    return token 
