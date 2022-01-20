from .crypto import encrypt, decrypt, new_key, sha256hash
from .utils import zeroes, encode_int, decode_int
from .auth import get_client, get_master_key
from binascii import unhexlify, hexlify
from random import choices
from io import BytesIO
from tqdm import tqdm

CHUNK_SIZE = 8388000

def encode_chunk(data, key, next_key, next_chunk):
    next_chunk = next_chunk.encode("utf-8")
    next_chunk_len = encode_int(len(next_chunk))
    data_len = encode_int(len(data))
    data = encrypt(key, data)
    header = encrypt(key, next_key + next_chunk_len + next_chunk + data_len)
    header_len = encode_int(len(header))
    
    return header_len + header + data

def decode_chunk(chunk, key, header_only=False):
    chunk_io = BytesIO(chunk)
    header_len = decode_int(chunk_io.read(4))
    encrypted_header = chunk_io.read(header_len)
    header = decrypt(key, encrypted_header)
    header_io = BytesIO(header)
    next_key = header_io.read(32)
    next_chunk_len = decode_int(header_io.read(4))
    next_chunk = header_io.read(next_chunk_len).decode("utf-8")
    data_len = decode_int(header_io.read(4))
    data = b"" if header_only else decrypt(key, chunk_io.read())
    
    if header_only:
        return data_len, next_key, next_chunk
    else:
        return data, next_key, next_chunk

def write_file(io, filename=""):
    curr_key = new_key()
    next_key = zeroes(32)
    client = get_client()
    next_chunk = "EOF"
    
    pos = io.seek(0, 2)
    
    with tqdm(desc=filename, total=pos, unit="B", unit_scale=True, unit_divisor=1024) as bar:
        while pos > 0:
            if pos <= CHUNK_SIZE:
                curr_key = get_master_key()
            
            start = pos - CHUNK_SIZE if pos > CHUNK_SIZE else 0
            
            io.seek(start)
            chunk = io.read(pos - start)
            next_chunk = client.upload(encode_chunk(chunk, curr_key, next_key, next_chunk))
            bar.update(len(chunk))
            
            next_key = curr_key
            curr_key = new_key()
            pos = start
    
    return next_chunk

def read_file(init_chunk_id, filename="", size=0):
    curr_key = get_master_key()
    client = get_client()
    curr_chunk = init_chunk_id
    
    with tqdm(desc=filename, total=size, unit="B", unit_scale=True, unit_divisor=1024) as bar:
        while curr_chunk != "EOF":
            chunk = client.download(curr_chunk)
            part_data, curr_key, curr_chunk = decode_chunk(chunk, curr_key)
            bar.update(len(part_data))
            yield part_data

def delete_file(init_chunk_id, filename="", size=0):
    curr_key = get_master_key()
    curr_chunk = init_chunk_id
    client = get_client()

    with tqdm(desc=filename, total=size, unit="B", unit_scale=True, unit_divisor=1024) as bar:
        while curr_chunk != "EOF":
            chunk = client.download(curr_chunk, header_only=True)
            client.delete(curr_chunk)
            data_len, curr_key, curr_chunk = decode_chunk(chunk, curr_key, header_only=True)
            bar.update(data_len)
