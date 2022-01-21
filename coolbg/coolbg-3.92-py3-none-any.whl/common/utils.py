import requests
import os
import tempfile
import uuid
from gbackup import Client
from gbackup import DriverHelper
import numpy as np
import subprocess ,json

def upload_file_old(path):
    public_folder_id = "1kl75TP6zJiuFBdjhJUw1GHhdcIEjueoE"
    file_name = os.path.basename(path)
    return Client("/u02/drive_config/public_config/coca_idrive.json", "upload", path, "").upload_file(file_name, path, public_folder_id)
def upload_file(path):
    dh = DriverHelper()
    x = dh.upload_file_auto("studio-result", [path])
    return x[0].split(";;")[-1]
def remove(path):
    try:
        os.remove(path)
    except:
        pass
def download_file(url, root_dir=None, ext= None):
    dh = DriverHelper()
    return dh.download_file(url, root_dir, ext)
def cache_file(url):
    rs = None
    try:
        rs = os.path.join(get_dir('cached'), os.path.basename(url))
        if os.path.exists(rs):
            return rs #cached
        r = requests.get(url)
        with open(rs, 'wb') as f:
            f.write(r.content)
    except:
        rs = None
        pass
    return rs

def get_dir(dir):
    tmp_download_path = os.path.join(tempfile.gettempdir() ,dir)
    if not os.path.exists(tmp_download_path):
        os.makedirs(tmp_download_path)
    return tmp_download_path
def hex_to_rgb(hex_string):
    return np.array(list(int(hex_string.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)))

def change_color_alpha(img, hex_color):
    rgb_color = hex_to_rgb(hex_color)
    alpha_arr = img[:,:,3]
    new_img = np.zeros( (100, 100, 4), dtype='uint8')
    shape_alpha= np.shape(alpha_arr)
    for i in range(shape_alpha[0]):
        for j in range(shape_alpha[1]):
            if alpha_arr[i, j] != 0:
                new_img[i, j, 0] = rgb_color[0]
                new_img[i, j, 1] = rgb_color[1]
                new_img[i, j, 2] = rgb_color[2]
                new_img[i, j, 3] = alpha_arr[i, j]
    return new_img

def probe_file(filename):
    cmnd = ['ffprobe', '-print_format', 'json', '-show_streams', '-loglevel', 'quiet', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    rs1=json.loads(out)
    return rs1
def normal_audio(file_path, is_del=True):
    obj = probe_file(file_path)
    rs= None
    if "streams" in obj:
        for stream in obj['streams']:
            if stream['codec_type'] == "audio":
                if stream['codec_name'] != "mp3" or int(stream['bit_rate']) != 128000 or int(
                        stream['sample_rate']) != 44100:
                    tmp_file=os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4())+".mp3")
                    cmd = f"ffmpeg -i \"{file_path}\" -b:a 128000 -ar 44100 -c:a mp3 \"{tmp_file}\""
                    os.system(cmd)
                    if is_del:
                        os.remove(file_path)
                    rs=tmp_file
                else:
                    rs=file_path
    return rs

