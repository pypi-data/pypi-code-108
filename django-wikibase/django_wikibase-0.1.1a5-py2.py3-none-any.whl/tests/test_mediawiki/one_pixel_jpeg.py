from PIL import Image
from os.path import exists

def make_one_pixel_jpeg(file_path: str):
    if exists(file_path):
        return
    im = Image.new(mode='L', size=(1, 1))
    im.save(file_path)
