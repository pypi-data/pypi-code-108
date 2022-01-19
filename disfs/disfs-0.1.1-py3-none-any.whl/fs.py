from .auth import get_master_key, get_client
from .crypto import encrypt, decrypt
from .file import read_file, write_file, delete_file
from os.path import basename, exists, getmtime
from json import loads, dumps
from config_path import ConfigPath
from time import time

FS_CACHE = ConfigPath("disfs", "fs_cache", ".txt").saveFilePath(mkdir=True)

def human_size(size):
    units = {
        "B": 1,
        "KB": 1000,
        "MB": 1000000,
        "GB": 1000000000,
        "TB": 1000000000000
    }
    
    for u in units:
        if units[u] <= size and size < units[u] * 1000:
            break
    
    return f"{round(size/units[u], 2)} {u}"

def write_fs(fs):
    with open(FS_CACHE, "w") as f:
        f.write(encrypt(get_master_key(), dumps(fs), string=True))

def get_fs():
    if exists(FS_CACHE) and (time() - getmtime(FS_CACHE) < 60 * 30):
        with open(FS_CACHE, "r") as f:
            fs = loads(decrypt(get_master_key(), f.read(), string=True))
    else:
        client = get_client()
        fs = {}
        
        for f in client.get_listing():
            try:
                fdata = loads(decrypt(get_master_key(), f["content"], string=True))
                fs[fdata["name"]] = (fdata["chunk"], fdata["size"])
            except:
                pass
        
        write_fs(fs)
    
    return fs

def add_entry(entry):
    enc_entry = encrypt(get_master_key(), dumps(entry), string=True)
    client = get_client()
    
    client.add_entry(enc_entry)

def get_entry(entry):
    return loads(decrypt(get_master_key(), entry["content"], string=True))

def add(file, **kwargs):
    fname = basename(file)
    
    with open(file, "rb") as f:
        size = f.seek(0, 2)
        f.seek(0)
        init_chunk = write_file(f, filename=fname)
    
    fs = get_fs()
    fs[fname] = (init_chunk, size)
    add_entry({"name": fname, "chunk": init_chunk, "size": size})
    write_fs(fs)

def get(file, out=None):
    out = out if out else file
    fdata = get_fs()[file]
    
    with open(out, "wb") as f:
        for chunk in read_file(fdata[0], filename=file, size=fdata[1]):
            f.write(chunk)

def rm(file, **kwargs):
    client = get_client()
    fs = get_fs()
    init_chunk = fs[file][0]
    size = fs[file][1]
    delete_file(init_chunk, filename=file, size=size)
    
    for entry in client.get_listing():
        e = get_entry(entry)
        
        if e["chunk"] == init_chunk:
            client.delete(entry["id"], listing=True)
    
    del fs[file]
    write_fs(fs)

def ls(*args, **kwargs):
    fs = get_fs()
    
    print("Current files:\n")
    
    for file in fs:
        print(f"{file} - {human_size(fs[file][1])}")