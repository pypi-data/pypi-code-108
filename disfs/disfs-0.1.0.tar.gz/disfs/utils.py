from struct import pack, unpack
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from requests import get, post
from io import BytesIO

def zeroes(n):
    return bytes([0]*n)

def convert_to_png(data):
    PNG = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00\x0cIDAT\x18Wc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa75\x81\x84\x00\x00\x00\x00IEND\xaeB`\x82\x00\x12n\\bLObG@\x11\x10\x00B\xf0%\x00\x01'
    return PNG + data

def decode_int(data):
    return unpack("<I", data)[0]

def encode_int(num):
    return pack("<I", num)

# TODO: for all pbreqs, implement callback instead of baked-in tqdm
# TODO: maybe not here, but somewhere implement config-based callback (none vs. pbar)

def pbget(url, session=None, disable=False):
    data = b""
    
    if session:
        resp = session.get(url, stream=True)
    else:
        resp = get(url, stream=True)
    
    resp.raise_for_status()
    content_len = int(resp.headers.get('content-length', 0))
    with tqdm(desc=f"Chunk", total=content_len, unit="B", unit_scale=True, unit_divisor=1024, leave=False, disable=disable) as bar:
        for piece in resp.iter_content(1024):
            bar.update(len(piece))
            data += piece
    
    return data

def pbpost(url, data, session, disable=False):
    with tqdm(desc="Chunk", total=len(data), unit="B", unit_scale=True, unit_divisor=1024, leave=False, disable=disable) as bar:
        io = CallbackIOWrapper(bar.update, BytesIO(data), "read")
        resp = session.post(url, data=io)
    
    resp.raise_for_status()
    return resp

def pbmpost(method, url, data, session, extra_data={}, filename="upload.bin", disable=False):
    fields = extra_data
    fields["file"] = (filename, data)
    
    with tqdm(desc="Chunk", total=len(data), unit="B", unit_scale=True, unit_divisor=1024, leave=False, disable=disable) as bar:
        enc = MultipartEncoder(fields=fields)
        mon = MultipartEncoderMonitor(enc, lambda monitor: bar.update(monitor.bytes_read - bar.n))
        headers = {"Content-Type": mon.content_type}
        resp = session.request(method, url, data=mon, headers=headers)
    
    resp.raise_for_status()
    return resp
