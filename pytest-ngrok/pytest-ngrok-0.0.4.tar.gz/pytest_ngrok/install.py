import io
import os
import shutil
from urllib.request import urlopen
from zipfile import ZipFile


def fetch_url(url, stream_cls=io.BytesIO):
    stream = stream_cls()
    stream.write(urlopen(url).read())
    stream.seek(0)
    return stream


def install_bin(bin_path, remote_url):
    if os.path.exists(bin_path):
        raise ValueError("Path is exists!")
    dir_path = os.path.dirname(bin_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    zfile = ZipFile(fetch_url(remote_url))
    with open(bin_path, 'wb') as f:
        shutil.copyfileobj(zfile.open('ngrok'), f)
    os.chmod(bin_path, 0o755)
