import hashlib

def get_file_hash(file_path):
    h = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def get_memory_file_hash(file_object):
    h = hashlib.sha256()
    while True:
        chunk = file_object.read(h.block_size)
        if not chunk:
            break
        h.update(chunk)
    return h.hexdigest()