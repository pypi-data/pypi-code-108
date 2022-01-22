from tqdm import tqdm
import os
import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from PIL import Image
import cv2

def load_images(folder, num = 30000):
    images = []
    count = 0
    for filename in tqdm(os.listdir(folder)):
        if count == num:
            break
        img = mpimg.imread(os.path.join(folder, filename))
        if img is not None:
            images.append(img)
            count +=1
    return images


def load_images_sequentially(folder, num = 809, identifier = ""):
    count = 0
    images = []
    for i in tqdm(range(num)):
        if count == num:
            break
        img = mpimg.imread(os.path.join(folder, f'{i}{identifier}.png'))
        if img is not None:
            images.append(img)
            count +=1
    return images


def extractToPath(slices, path):
    for i in tqdm(range(slices.shape[0])):
        im = Image.fromarray(cv2.resize(slices[i], dsize=(128,128), interpolation=cv2.INTER_CUBIC))
        im.save(path + "/" + f'{i}.jpg')
        
        

