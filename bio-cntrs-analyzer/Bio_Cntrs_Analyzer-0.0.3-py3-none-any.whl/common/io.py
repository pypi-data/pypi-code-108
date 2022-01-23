import os
import cv2
import numpy as np


def im_load(name):
    f = open(name, "rb")
    chunk = bytearray(f.read())
    chunk_arr = np.frombuffer(chunk, dtype=np.uint8)
    img = cv2.imdecode(chunk_arr, cv2.IMREAD_UNCHANGED)
    f.close()

    return img


def im_save(target_path: str, image_np: np.ndarray):
    filename, file_extension = os.path.splitext(target_path)
    is_success, im_buf_arr = cv2.imencode(file_extension, image_np)
    return im_buf_arr.tofile(target_path)
