import PIL
from PIL import Image
import imageio

##########################################################
def scale_image(imgpath, scaleratio, outpath):
    """Scale (even large) images by @scaleratio and outputs to @outpath"""
    PIL.Image.MAX_IMAGE_PIXELS = sys.maxsize
    img = imageio.imread(imgpath)
    wnew = int(img.shape[0] * scaleratio)
    hnew = int(img.shape[1] * scaleratio)
    img = Image.fromarray(img).resize((hnew, wnew), Image.ANTIALIAS)
    img.save(outpath)
