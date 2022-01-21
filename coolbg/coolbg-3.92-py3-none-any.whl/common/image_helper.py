from PIL import Image,ImageEnhance
import numpy as np
def ReduceOpacity(im, opacity):
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im
def hideImage(im):
    return ReduceOpacity(im,0)

def create_virgin_layer(w, h):
    return np.asarray(Image.new('RGBA', (w, h), (1, 1, 1, 0)))
