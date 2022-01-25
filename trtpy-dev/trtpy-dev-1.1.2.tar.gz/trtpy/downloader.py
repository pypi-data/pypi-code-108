import os
import requests
import traceback
import hashlib
import zipfile
from tqdm import tqdm

CACHE_ROOT = os.path.expanduser('~/.cache/trtpy')

def get_cache_path(file):
    return os.path.join(CACHE_ROOT, file)

def compute_file_md5(file):
    handle = hashlib.md5()

    with open(file, "rb") as f:
        while True:
            b = f.read(1024 * 64)
            if len(b) == 0:
                break

            handle.update(b)

    return handle.hexdigest()

def get_file_url_md5sum(url):
    resp = requests.get(url + ".md5sum")
    if resp.status_code != 200:
        return None

    return str(resp.content, encoding="utf-8")


def download_to_file(url, file):
    
    try:
        root_dir = os.path.realpath(os.path.dirname(file))
        os.makedirs(root_dir, exist_ok=True)

        chunk_kb_size = 1024
        response   = requests.get(url, stream=True)
        if response.status_code != 200:
            print(f"Download failed: {url}")
            return False

        content_iter = response.iter_content(chunk_size=chunk_kb_size)
        if "Content-Length" in response.headers:
            content_length = int(response.headers["Content-Length"])
            block_count = int((content_length + chunk_kb_size - 1) / chunk_kb_size)
        else:
            content_length = None
            block_count = None
        
        desc = "Download " + os.path.basename(url)
        bar_format = "{l_bar}|{bar}|{n_fmt} KB/{total_fmt} KB {elapsed}<{remaining}"
        pbar = tqdm(content_iter, total=block_count, desc=desc, bar_format=bar_format)
        with open(file, "wb") as fout:
            for ib in pbar:
                fout.write(ib)

    except Exception as e:
        traceback.print_exc()
        return False
    
    return True


def download_and_verify_md5_saveto_file(url, file):
    
    try:
        remote_md5 = get_file_url_md5sum(url)
        if os.path.exists(file):
            local_md5 = compute_file_md5(file)
            if remote_md5 == local_md5:
                # MD5 matched
                print(f"File already download in {file}")
                return True, remote_md5

        return download_to_file(url, file), remote_md5
    except Exception as e:
        traceback.print_exc()
        return False, None
    
    return True, remote_md5

def extract_zip_to(file, to):
    zfile = zipfile.ZipFile(file)
    zfile.extractall(to)
    return zfile.namelist()